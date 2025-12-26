#!/usr/bin/env python3
"""
Tests mínimos para Scheduler PRD (FASE 4B)
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

print("🧪 Tests Mínimos Scheduler PRD (FASE 4B)\n")
print("=" * 60)

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Importar funciones del scheduler
    sys.path.insert(0, str(BASE_DIR / '100trafico' / 'src' / 'project'))
    from scheduler_prd import (
        get_pending_contenidos,
        check_idempotencia,
        check_limits,
        get_cuentas_plataforma,
        process_contenido
    )
    
    # Limpiar datos de prueba anteriores
    modelo_nombre = "test_scheduler_prd"
    print("\n🧹 Limpiando datos de prueba anteriores...")
    try:
        modelos_existing = supabase.table('modelos').select("id").eq('nombre', modelo_nombre).execute()
        if modelos_existing.data:
            modelo_id_existing = modelos_existing.data[0]['id']
            # Eliminar en orden inverso
            supabase.table('publicaciones').delete().in_('contenido_id',
                supabase.table('contenidos').select('id').eq('modelo_id', modelo_id_existing).execute().data or []).execute()
            supabase.table('contenidos').delete().eq('modelo_id', modelo_id_existing).execute()
            supabase.table('cuentas_plataforma').delete().eq('modelo_id', modelo_id_existing).execute()
            supabase.table('modelos').delete().eq('id', modelo_id_existing).execute()
            print("   ✅ Datos anteriores eliminados")
    except:
        pass
    
    # Crear datos de prueba
    print("\n1️⃣  Preparando datos de prueba...")
    
    # Modelo
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
    print(f"   ✅ Modelo creado: {modelo_id}")
    
    # Plataforma
    platform_existing = supabase.table('plataformas').select("id").eq('nombre', 'kams').execute()
    if platform_existing.data:
        platform_id = platform_existing.data[0]['id']
    else:
        platform_data = {"nombre": "kams", "activa": True}
        platform_result = supabase.table('plataformas').insert(platform_data).execute()
        platform_id = platform_result.data[0]['id']
    print(f"   ✅ Plataforma: kams")
    
    # Cuenta
    cuenta_data = {
        "modelo_id": modelo_id,
        "plataforma_id": platform_id,
        "sesion_guardada": False
    }
    cuenta_result = supabase.table('cuentas_plataforma').insert(cuenta_data).execute()
    cuenta_id = cuenta_result.data[0]['id']
    print(f"   ✅ Cuenta creada: {cuenta_id}")
    
    # Contenido
    contenido_data = {
        "modelo_id": modelo_id,
        "archivo_path": f"modelos/{modelo_nombre}/test_video_scheduler.mp4",
        "caption_generado": "Test scheduler caption",
        "tags_generados": ["test", "scheduler"],
        "estado": "nuevo"
    }
    contenido_result = supabase.table('contenidos').insert(contenido_data).execute()
    contenido_id = contenido_result.data[0]['id']
    print(f"   ✅ Contenido creado: {contenido_id}")
    
    # Test 1: get_pending_contenidos
    print("\n2️⃣  Test 1: get_pending_contenidos()...")
    contenidos = get_pending_contenidos()
    if contenidos:
        encontrado = False
        for c in contenidos:
            if c.get('id') == contenido_id:
                encontrado = True
                print(f"   ✅ Contenido encontrado: {c.get('archivo_path')}")
                break
        if not encontrado:
            print(f"   ⚠️  Contenido no encontrado en lista")
    else:
        print(f"   ⚠️  No se encontraron contenidos")
    
    # Test 2: check_idempotencia (debe ser False inicialmente)
    print("\n3️⃣  Test 2: check_idempotencia() (inicialmente False)...")
    tiene_pubs = check_idempotencia(contenido_id)
    if not tiene_pubs:
        print(f"   ✅ Idempotencia OK: no tiene publicaciones")
    else:
        print(f"   ❌ Error: debería ser False")
    
    # Test 3: check_limits (debe ser False inicialmente)
    print("\n4️⃣  Test 3: check_limits() (inicialmente False)...")
    alcanzo_limite = check_limits(contenido_id)
    if not alcanzo_limite:
        print(f"   ✅ Límites OK: no alcanzó tope")
    else:
        print(f"   ❌ Error: debería ser False")
    
    # Test 4: get_cuentas_plataforma
    print("\n5️⃣  Test 4: get_cuentas_plataforma()...")
    cuentas = get_cuentas_plataforma(modelo_id, ["kams"])
    if cuentas:
        print(f"   ✅ {len(cuentas)} cuenta(s) encontrada(s)")
        for cuenta in cuentas:
            print(f"      - {cuenta.get('plataforma_nombre')}: {cuenta.get('id')}")
    else:
        print(f"   ❌ Error: debería encontrar cuenta")
    
    # Test 5: process_contenido (1 contenido → N publicaciones)
    print("\n6️⃣  Test 5: process_contenido() - 1 contenido → N publicaciones...")
    
    # Obtener contenido completo con join
    contenido_full = supabase.table('contenidos')\
        .select("*, modelos(*)")\
        .eq('id', contenido_id)\
        .execute()
    
    if contenido_full.data:
        contenido = contenido_full.data[0]
        success = process_contenido(contenido)
        
        if success:
            print(f"   ✅ Contenido procesado exitosamente")
            
            # Verificar publicaciones creadas
            publicaciones = supabase.table('publicaciones')\
                .select("*")\
                .eq('contenido_id', contenido_id)\
                .execute()
            
            if publicaciones.data:
                print(f"   ✅ {len(publicaciones.data)} publicación(es) creada(s)")
                for pub in publicaciones.data:
                    print(f"      - Estado: {pub.get('estado')}, Scheduled: {pub.get('scheduled_time')}")
            else:
                print(f"   ❌ Error: no se crearon publicaciones")
            
            # Verificar estado del contenido
            contenido_check = supabase.table('contenidos').select("estado").eq('id', contenido_id).execute()
            if contenido_check.data:
                estado = contenido_check.data[0].get('estado')
                if estado == 'aprobado':
                    print(f"   ✅ Contenido marcado como 'aprobado'")
                else:
                    print(f"   ❌ Error: estado debería ser 'aprobado', es '{estado}'")
        else:
            print(f"   ❌ Error procesando contenido")
    else:
        print(f"   ❌ Error: contenido no encontrado")
    
    # Test 6: Idempotencia (doble ejecución no duplica)
    print("\n7️⃣  Test 6: Idempotencia - doble ejecución no duplica...")
    
    # Contar publicaciones antes
    pubs_antes = supabase.table('publicaciones')\
        .select("id", count="exact")\
        .eq('contenido_id', contenido_id)\
        .execute()
    count_antes = pubs_antes.count if hasattr(pubs_antes, 'count') else len(pubs_antes.data) if pubs_antes.data else 0
    
    # Ejecutar de nuevo
    contenido_full = supabase.table('contenidos')\
        .select("*, modelos(*)")\
        .eq('id', contenido_id)\
        .execute()
    
    if contenido_full.data:
        contenido = contenido_full.data[0]
        success = process_contenido(contenido)
        
        # Contar publicaciones después
        pubs_despues = supabase.table('publicaciones')\
            .select("id", count="exact")\
            .eq('contenido_id', contenido_id)\
            .execute()
        count_despues = pubs_despues.count if hasattr(pubs_despues, 'count') else len(pubs_despues.data) if pubs_despues.data else 0
        
        if count_antes == count_despues:
            print(f"   ✅ Idempotencia OK: {count_antes} publicaciones (no duplicadas)")
        else:
            print(f"   ❌ Error: {count_antes} → {count_despues} (se duplicaron)")
    
    # Test 7: Sin cuentas válidas
    print("\n8️⃣  Test 7: Sin cuentas válidas → no crea publicaciones...")
    
    # Crear contenido sin cuentas (usar plataforma inexistente)
    contenido_sin_cuentas = {
        "modelo_id": modelo_id,
        "archivo_path": f"modelos/{modelo_nombre}/test_sin_cuentas.mp4",
        "estado": "nuevo"
    }
    contenido_sin_result = supabase.table('contenidos').insert(contenido_sin_cuentas).execute()
    contenido_sin_id = contenido_sin_result.data[0]['id']
    
    # Actualizar modelo para usar plataforma sin cuenta
    supabase.table('modelos').update({
        "configuracion_distribucion": {
            "plataformas": ["xxxfollow"],  # Plataforma sin cuenta
            "hora_inicio": "12:00",
            "ventana_horas": 5
        }
    }).eq('id', modelo_id).execute()
    
    contenido_full = supabase.table('contenidos')\
        .select("*, modelos(*)")\
        .eq('id', contenido_sin_id)\
        .execute()
    
    if contenido_full.data:
        contenido = contenido_full.data[0]
        success = process_contenido(contenido)
        
        # Verificar que NO se crearon publicaciones
        pubs = supabase.table('publicaciones')\
            .select("id")\
            .eq('contenido_id', contenido_sin_id)\
            .execute()
        
        if not pubs.data:
            print(f"   ✅ No se crearon publicaciones (sin cuentas válidas)")
        else:
            print(f"   ❌ Error: se crearon {len(pubs.data)} publicaciones (no debería)")
        
        # Verificar que contenido sigue en 'nuevo'
        contenido_check = supabase.table('contenidos').select("estado").eq('id', contenido_sin_id).execute()
        if contenido_check.data:
            estado = contenido_check.data[0].get('estado')
            if estado == 'nuevo':
                print(f"   ✅ Contenido sigue en 'nuevo' (no procesado)")
            else:
                print(f"   ⚠️  Estado: {estado} (esperado 'nuevo')")
    
    # Restaurar configuración
    supabase.table('modelos').update({
        "configuracion_distribucion": {
            "plataformas": ["kams"],
            "hora_inicio": "12:00",
            "ventana_horas": 5
        }
    }).eq('id', modelo_id).execute()
    
    # Limpiar
    print("\n🧹 Limpiando datos de prueba...")
    supabase.table('publicaciones').delete().eq('contenido_id', contenido_id).execute()
    supabase.table('publicaciones').delete().eq('contenido_id', contenido_sin_id).execute()
    supabase.table('contenidos').delete().eq('id', contenido_id).execute()
    supabase.table('contenidos').delete().eq('id', contenido_sin_id).execute()
    supabase.table('cuentas_plataforma').delete().eq('id', cuenta_id).execute()
    supabase.table('modelos').delete().eq('id', modelo_id).execute()
    print("   ✅ Datos de prueba eliminados")
    
    print("\n" + "=" * 60)
    print("✅ Tests completados")
    print("=" * 60)
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)



