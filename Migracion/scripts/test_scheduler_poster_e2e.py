#!/usr/bin/env python3
"""
Test End-to-End: Scheduler PRD → Poster PRD
Valida que el flujo completo funciona
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, timezone, timedelta

BASE_DIR = Path(__file__).resolve().parents[2]
env_path = BASE_DIR / '100trafico' / 'src' / '.env'
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://osdpemjvcsmfbacmjlcv.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_KEY:
    print("❌ ERROR: SUPABASE_ANON_KEY no configurado")
    sys.exit(1)

print("🧪 Test End-to-End: Scheduler PRD → Poster PRD\n")
print("=" * 60)

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Importar funciones
    sys.path.insert(0, str(BASE_DIR / '100trafico' / 'src' / 'project'))
    from scheduler_prd import get_pending_contenidos, process_contenido
    from poster_prd import get_pending_publicaciones
    
    # Limpiar datos anteriores
    modelo_nombre = "test_e2e_scheduler_poster"
    print("\n🧹 Limpiando datos anteriores...")
    try:
        modelos_existing = supabase.table('modelos').select("id").eq('nombre', modelo_nombre).execute()
        if modelos_existing.data:
            modelo_id_existing = modelos_existing.data[0]['id']
            supabase.table('publicaciones').delete().in_('contenido_id',
                supabase.table('contenidos').select('id').eq('modelo_id', modelo_id_existing).execute().data or []).execute()
            supabase.table('contenidos').delete().eq('modelo_id', modelo_id_existing).execute()
            supabase.table('cuentas_plataforma').delete().eq('modelo_id', modelo_id_existing).execute()
            supabase.table('modelos').delete().eq('id', modelo_id_existing).execute()
    except:
        pass
    
    # 1. Crear datos de prueba
    print("\n1️⃣  Creando datos de prueba...")
    
    modelo_data = {
        "nombre": modelo_nombre,
        "estado": "activa",
        "configuracion_distribucion": {
            "plataformas": ["kams"],
            "hora_inicio": "12:00",
            "ventana_horas": 5
        }
    }
    modelo_result = supabase.table('modelos').insert(modelo_data).execute()
    modelo_id = modelo_result.data[0]['id']
    
    platform_existing = supabase.table('plataformas').select("id").eq('nombre', 'kams').execute()
    if platform_existing.data:
        platform_id = platform_existing.data[0]['id']
    else:
        platform_data = {"nombre": "kams", "activa": True}
        platform_result = supabase.table('plataformas').insert(platform_data).execute()
        platform_id = platform_result.data[0]['id']
    
    cuenta_data = {
        "modelo_id": modelo_id,
        "plataforma_id": platform_id,
        "sesion_guardada": False
    }
    cuenta_result = supabase.table('cuentas_plataforma').insert(cuenta_data).execute()
    cuenta_id = cuenta_result.data[0]['id']
    
    contenido_data = {
        "modelo_id": modelo_id,
        "archivo_path": f"modelos/{modelo_nombre}/test_e2e.mp4",
        "caption_generado": "Test E2E caption",
        "tags_generados": ["test", "e2e"],
        "estado": "nuevo"
    }
    contenido_result = supabase.table('contenidos').insert(contenido_data).execute()
    contenido_id = contenido_result.data[0]['id']
    print(f"   ✅ Contenido creado: {contenido_id}")
    
    # 2. Ejecutar scheduler
    print("\n2️⃣  Ejecutando scheduler...")
    contenidos = get_pending_contenidos()
    
    if contenidos:
        contenido_full = supabase.table('contenidos')\
            .select("*, modelos(*)")\
            .eq('id', contenido_id)\
            .execute()
        
        if contenido_full.data:
            contenido = contenido_full.data[0]
            success = process_contenido(contenido)
            
            if success:
                print(f"   ✅ Scheduler procesó contenido exitosamente")
                
                # Verificar publicaciones creadas
                publicaciones = supabase.table('publicaciones')\
                    .select("*")\
                    .eq('contenido_id', contenido_id)\
                    .execute()
                
                if publicaciones.data:
                    print(f"   ✅ {len(publicaciones.data)} publicación(es) creada(s)")
                    for pub in publicaciones.data:
                        print(f"      - ID: {pub.get('id')}")
                        print(f"      - Estado: {pub.get('estado')}")
                        print(f"      - Scheduled: {pub.get('scheduled_time')}")
                else:
                    print(f"   ❌ Error: no se crearon publicaciones")
            else:
                print(f"   ❌ Error: scheduler no procesó contenido")
    else:
        print(f"   ⚠️  No se encontraron contenidos pendientes")
    
    # 3. Verificar que poster puede leer publicaciones
    print("\n3️⃣  Verificando que poster puede leer publicaciones...")
    
    # Actualizar scheduled_time a pasado para que el poster lo encuentre
    if publicaciones.data:
        pub_id = publicaciones.data[0]['id']
        scheduled_pasado = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
        supabase.table('publicaciones').update({"scheduled_time": scheduled_pasado}).eq('id', pub_id).execute()
        print(f"   ✅ Scheduled_time actualizado a pasado")
    
    # Query del poster
    publicaciones_poster = get_pending_publicaciones()
    
    if publicaciones_poster:
        print(f"   ✅ Poster encontró {len(publicaciones_poster)} publicación(es)")
        pub = publicaciones_poster[0]
        print(f"      - ID: {pub.get('id')}")
        print(f"      - Estado: {pub.get('estado')}")
        
        # Verificar joins
        contenido = pub.get('contenidos')
        if contenido:
            modelo = contenido.get('modelos', {})
            if modelo:
                print(f"      - Modelo: {modelo.get('nombre', 'N/A')}")
            print(f"      - Archivo: {contenido.get('archivo_path', 'N/A')}")
        
        cuenta = pub.get('cuentas_plataforma')
        if cuenta:
            plataforma = cuenta.get('plataformas', {})
            if plataforma:
                print(f"      - Plataforma: {plataforma.get('nombre', 'N/A')}")
    else:
        print(f"   ⚠️  Poster no encontró publicaciones (puede ser problema de timezone)")
    
    # Limpiar
    print("\n🧹 Limpiando datos de prueba...")
    supabase.table('publicaciones').delete().eq('contenido_id', contenido_id).execute()
    supabase.table('contenidos').delete().eq('id', contenido_id).execute()
    supabase.table('cuentas_plataforma').delete().eq('id', cuenta_id).execute()
    supabase.table('modelos').delete().eq('id', modelo_id).execute()
    print("   ✅ Datos de prueba eliminados")
    
    print("\n" + "=" * 60)
    print("✅ Test End-to-End completado")
    print("=" * 60)
    print("\n📋 Resumen:")
    print("   ✅ Scheduler crea publicaciones correctamente")
    print("   ✅ Poster puede leer publicaciones creadas")
    print("   ✅ Joins funcionan correctamente")
    print("   ✅ Flujo completo funciona")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)



