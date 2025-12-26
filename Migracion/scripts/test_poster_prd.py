#!/usr/bin/env python3
"""
Test del poster PRD: Verifica que puede leer publicaciones correctamente
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

print("🧪 Test del Poster PRD\n")

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Test 1: Query básica sin joins
    print("Test 1: Query básica de publicaciones...")
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        result = supabase.table('publicaciones')\
            .select("*")\
            .eq('estado', 'programada')\
            .lte('scheduled_time', now_iso)\
            .limit(5)\
            .execute()
        print(f"   ✅ Query funciona: {len(result.data) if result.data else 0} publicaciones encontradas")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Query con joins
    print("\nTest 2: Query con joins (contenidos, modelos, cuentas, plataformas)...")
    try:
        result = supabase.table('publicaciones')\
            .select("*, contenidos(*, modelos(*)), cuentas_plataforma(*, plataformas(*))")\
            .eq('estado', 'programada')\
            .limit(1)\
            .execute()
        
        if result.data:
            pub = result.data[0]
            print(f"   ✅ Join funciona")
            print(f"      - Publicación ID: {pub.get('id')}")
            print(f"      - Contenido: {pub.get('contenidos', {}).get('archivo_path', 'N/A')}")
            print(f"      - Modelo: {pub.get('contenidos', {}).get('modelos', {}).get('nombre', 'N/A')}")
            print(f"      - Plataforma: {pub.get('cuentas_plataforma', {}).get('plataformas', {}).get('nombre', 'N/A')}")
        else:
            print("   ℹ️  No hay publicaciones programadas (normal si no hay datos)")
    except Exception as e:
        print(f"   ❌ Error en join: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Crear publicación de prueba
    print("\nTest 3: Crear publicación de prueba...")
    try:
        # Buscar o crear modelo de prueba
        modelos = supabase.table('modelos').select("id, nombre").limit(1).execute()
        if not modelos.data:
            print("   ⚠️  No hay modelos, creando uno de prueba...")
            modelo_data = {
                "nombre": "test_poster_prd",
                "estado": "activa",
                "configuracion_distribucion": {"plataformas": ["kams"]}
            }
            modelo_result = supabase.table('modelos').insert(modelo_data).execute()
            modelo_id = modelo_result.data[0]['id']
        else:
            modelo_id = modelos.data[0]['id']
            print(f"   ℹ️  Usando modelo existente: {modelos.data[0]['nombre']}")
        
        # Buscar o crear plataforma
        plataformas = supabase.table('plataformas').select("id, nombre").eq('nombre', 'kams').execute()
        if not plataformas.data:
            print("   ⚠️  No hay plataforma kams, creando...")
            platform_data = {"nombre": "kams", "activa": True}
            platform_result = supabase.table('plataformas').insert(platform_data).execute()
            platform_id = platform_result.data[0]['id']
        else:
            platform_id = plataformas.data[0]['id']
        
        # Buscar o crear cuenta
        cuentas = supabase.table('cuentas_plataforma')\
            .select("id")\
            .eq('modelo_id', modelo_id)\
            .eq('plataforma_id', platform_id)\
            .execute()
        
        if not cuentas.data:
            cuenta_data = {
                "modelo_id": modelo_id,
                "plataforma_id": platform_id,
                "sesion_guardada": False
            }
            cuenta_result = supabase.table('cuentas_plataforma').insert(cuenta_data).execute()
            cuenta_id = cuenta_result.data[0]['id']
        else:
            cuenta_id = cuentas.data[0]['id']
        
        # Buscar o crear contenido
        contenidos = supabase.table('contenidos')\
            .select("id")\
            .eq('modelo_id', modelo_id)\
            .like('archivo_path', '%test%')\
            .limit(1)\
            .execute()
        
        if not contenidos.data:
            contenido_data = {
                "modelo_id": modelo_id,
                "archivo_path": "modelos/test_poster_prd/test_video.mp4",
                "caption_generado": "Test caption",
                "tags_generados": ["test"],
                "estado": "aprobado"
            }
            contenido_result = supabase.table('contenidos').insert(contenido_data).execute()
            contenido_id = contenido_result.data[0]['id']
        else:
            contenido_id = contenidos.data[0]['id']
        
        # Crear publicación de prueba
        scheduled_time = (datetime.now(timezone.utc) + timedelta(minutes=1)).isoformat()
        pub_data = {
            "contenido_id": contenido_id,
            "cuenta_plataforma_id": cuenta_id,
            "scheduled_time": scheduled_time,
            "caption_usado": "Test caption",
            "tags_usados": ["test"],
            "estado": "programada",
            "intentos": 0
        }
        pub_result = supabase.table('publicaciones').insert(pub_data).execute()
        pub_id = pub_result.data[0]['id']
        print(f"   ✅ Publicación de prueba creada: {pub_id}")
        
        # Test 4: Query del poster
        print("\nTest 4: Query del poster (con scheduled_time <= now)...")
        # Actualizar scheduled_time a pasado
        supabase.table('publicaciones').update({"scheduled_time": (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()}).eq('id', pub_id).execute()
        
        now_iso = datetime.now(timezone.utc).isoformat()
        result = supabase.table('publicaciones')\
            .select("*, contenidos(*, modelos(*)), cuentas_plataforma(*, plataformas(*))")\
            .eq('estado', 'programada')\
            .lte('scheduled_time', now_iso)\
            .order('scheduled_time', desc=False)\
            .execute()
        
        if result.data:
            print(f"   ✅ Query del poster funciona: {len(result.data)} publicación(es) encontrada(s)")
            pub = result.data[0]
            print(f"      - ID: {pub.get('id')}")
            print(f"      - Estado: {pub.get('estado')}")
            print(f"      - Modelo: {pub.get('contenidos', {}).get('modelos', {}).get('nombre', 'N/A')}")
            print(f"      - Plataforma: {pub.get('cuentas_plataforma', {}).get('plataformas', {}).get('nombre', 'N/A')}")
        else:
            print("   ⚠️  No se encontró la publicación (puede ser problema de timezone)")
        
        # Limpiar
        print("\n🧹 Limpiando datos de prueba...")
        supabase.table('publicaciones').delete().eq('id', pub_id).execute()
        print("   ✅ Datos de prueba eliminados")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ Tests completados")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)



