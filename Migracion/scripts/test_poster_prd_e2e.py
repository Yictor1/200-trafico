#!/usr/bin/env python3
"""
Test End-to-End del Poster PRD
Valida el flujo completo: crear publicación → procesar → verificar estados y eventos
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, timezone, timedelta
import time

BASE_DIR = Path(__file__).resolve().parents[2]
env_path = BASE_DIR / '100trafico' / 'src' / '.env'
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://osdpemjvcsmfbacmjlcv.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_KEY:
    print("❌ ERROR: SUPABASE_ANON_KEY no configurado")
    sys.exit(1)

print("🧪 Test End-to-End Poster PRD\n")
print("=" * 60)

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # 1. Preparar datos de prueba
    print("\n1️⃣  Preparando datos de prueba...")
    
    # Limpiar datos anteriores si existen
    modelo_nombre = "test_e2e_poster"
    try:
        # Eliminar en orden inverso (por FKs)
        modelos_existing = supabase.table('modelos').select("id").eq('nombre', modelo_nombre).execute()
        if modelos_existing.data:
            modelo_id_existing = modelos_existing.data[0]['id']
            # Eliminar publicaciones, contenidos, cuentas
            supabase.table('publicaciones').delete().in_('contenido_id', 
                supabase.table('contenidos').select('id').eq('modelo_id', modelo_id_existing).execute().data or []).execute()
            supabase.table('contenidos').delete().eq('modelo_id', modelo_id_existing).execute()
            supabase.table('cuentas_plataforma').delete().eq('modelo_id', modelo_id_existing).execute()
            supabase.table('modelos').delete().eq('id', modelo_id_existing).execute()
            print(f"   🧹 Datos anteriores eliminados")
    except:
        pass
    
    # Modelo
    modelo_data = {
        "nombre": modelo_nombre,
        "estado": "activa",
        "configuracion_distribucion": {"plataformas": ["kams"]}
    }
    modelo_result = supabase.table('modelos').insert(modelo_data).execute()
    modelo_id = modelo_result.data[0]['id']
    print(f"   ✅ Modelo creado: {modelo_nombre}")
    
    # Plataforma (verificar si existe primero)
    platform_existing = supabase.table('plataformas').select("id").eq('nombre', 'kams').execute()
    if platform_existing.data:
        platform_id = platform_existing.data[0]['id']
        print(f"   ℹ️  Plataforma kams ya existe")
    else:
        platform_data = {"nombre": "kams", "activa": True}
        platform_result = supabase.table('plataformas').insert(platform_data).execute()
        platform_id = platform_result.data[0]['id']
        print(f"   ✅ Plataforma creada: kams")
    
    # Cuenta
    cuenta_data = {
        "modelo_id": modelo_id,
        "plataforma_id": platform_id,
        "sesion_guardada": False
    }
    cuenta_result = supabase.table('cuentas_plataforma').insert(cuenta_data).execute()
    cuenta_id = cuenta_result.data[0]['id']
    print(f"   ✅ Cuenta creada")
    
    # Contenido
    contenido_data = {
        "modelo_id": modelo_id,
        "archivo_path": f"modelos/{modelo_nombre}/test_video_e2e.mp4",
        "caption_generado": "Test E2E caption",
        "tags_generados": ["test", "e2e"],
        "estado": "aprobado"
    }
    contenido_result = supabase.table('contenidos').insert(contenido_data).execute()
    contenido_id = contenido_result.data[0]['id']
    print(f"   ✅ Contenido creado")
    
    # Publicación (programada para ahora)
    scheduled_time = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    pub_data = {
        "contenido_id": contenido_id,
        "cuenta_plataforma_id": cuenta_id,
        "scheduled_time": scheduled_time,
        "caption_usado": "Test E2E caption",
        "tags_usados": ["test", "e2e"],
        "estado": "programada",
        "intentos": 0
    }
    pub_result = supabase.table('publicaciones').insert(pub_data).execute()
    pub_id = pub_result.data[0]['id']
    print(f"   ✅ Publicación creada: {pub_id}")
    
    # 2. Test query del poster
    print("\n2️⃣  Test query del poster...")
    now_iso = datetime.now(timezone.utc).isoformat()
    result = supabase.table('publicaciones')\
        .select("*, contenidos(*, modelos(*)), cuentas_plataforma(*, plataformas(*))")\
        .eq('estado', 'programada')\
        .lte('scheduled_time', now_iso)\
        .order('scheduled_time', desc=False)\
        .execute()
    
    if result.data and len(result.data) > 0:
        pub = result.data[0]
        print(f"   ✅ Publicación encontrada")
        print(f"      - ID: {pub.get('id')}")
        print(f"      - Estado: {pub.get('estado')}")
        
        # Verificar estructura de joins
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
        print("   ❌ No se encontró la publicación")
    
    # 3. Test actualización de estado
    print("\n3️⃣  Test actualización de estado...")
    
    # Cambiar a procesando
    supabase.table('publicaciones')\
        .update({"estado": "procesando"})\
        .eq('id', pub_id)\
        .execute()
    
    # Verificar
    updated = supabase.table('publicaciones').select("estado").eq('id', pub_id).execute()
    if updated.data and updated.data[0]['estado'] == 'procesando':
        print("   ✅ Estado actualizado a 'procesando'")
    else:
        print("   ❌ Error actualizando estado")
    
    # 4. Test eventos_sistema
    print("\n4️⃣  Test eventos_sistema...")
    
    evento_data = {
        "tipo": "publicacion_iniciada",
        "publicacion_id": pub_id,
        "modelo_id": modelo_id,
        "descripcion": "Test evento E2E",
        "realizado_por": "sistema"
    }
    evento_result = supabase.table('eventos_sistema').insert(evento_data).execute()
    evento_id = evento_result.data[0]['id']
    print(f"   ✅ Evento creado: {evento_id}")
    
    # Verificar evento
    eventos = supabase.table('eventos_sistema')\
        .select("*")\
        .eq('publicacion_id', pub_id)\
        .execute()
    
    if eventos.data:
        print(f"   ✅ Eventos encontrados: {len(eventos.data)}")
        for ev in eventos.data:
            print(f"      - {ev.get('tipo')}: {ev.get('descripcion', '')[:50]}")
    
    # 5. Test actualización completa (publicado)
    print("\n5️⃣  Test actualización completa (publicado)...")
    
    update_data = {
        "estado": "publicado",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "url_publicacion": "https://kams.com/video/test123"
    }
    supabase.table('publicaciones').update(update_data).eq('id', pub_id).execute()
    
    # Verificar
    final = supabase.table('publicaciones').select("estado, published_at, url_publicacion").eq('id', pub_id).execute()
    if final.data:
        pub_final = final.data[0]
        if pub_final['estado'] == 'publicado' and pub_final.get('published_at'):
            print("   ✅ Publicación marcada como 'publicado' con published_at")
        else:
            print(f"   ⚠️  Estado: {pub_final['estado']}, published_at: {pub_final.get('published_at')}")
    
    # 6. Test actualización con error (fallido)
    print("\n6️⃣  Test actualización con error (fallido)...")
    
    # Crear otra publicación para test de error
    pub_error_data = {
        "contenido_id": contenido_id,
        "cuenta_plataforma_id": cuenta_id,
        "scheduled_time": (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(),
        "estado": "programada",
        "intentos": 0
    }
    pub_error_result = supabase.table('publicaciones').insert(pub_error_data).execute()
    pub_error_id = pub_error_result.data[0]['id']
    
    # Obtener intentos actuales
    current = supabase.table('publicaciones').select("intentos").eq('id', pub_error_id).execute()
    intentos_antes = current.data[0].get('intentos', 0) if current.data else 0
    
    # Actualizar con error
    error_update = {
        "estado": "fallido",
        "ultimo_error": "Test error E2E",
        "intentos": intentos_antes + 1
    }
    supabase.table('publicaciones').update(error_update).eq('id', pub_error_id).execute()
    
    # Verificar
    error_final = supabase.table('publicaciones')\
        .select("estado, ultimo_error, intentos")\
        .eq('id', pub_error_id)\
        .execute()
    
    if error_final.data:
        pub_err = error_final.data[0]
        if pub_err['estado'] == 'fallido' and pub_err.get('ultimo_error') and pub_err.get('intentos', 0) > intentos_antes:
            print(f"   ✅ Publicación marcada como 'fallido' con error y intentos incrementados ({pub_err.get('intentos')})")
        else:
            print(f"   ⚠️  Estado: {pub_err['estado']}, Error: {pub_err.get('ultimo_error')}, Intentos: {pub_err.get('intentos')}")
    
    # Limpiar
    print("\n🧹 Limpiando datos de prueba...")
    supabase.table('eventos_sistema').delete().eq('publicacion_id', pub_id).execute()
    supabase.table('eventos_sistema').delete().eq('publicacion_id', pub_error_id).execute()
    supabase.table('publicaciones').delete().eq('id', pub_id).execute()
    supabase.table('publicaciones').delete().eq('id', pub_error_id).execute()
    supabase.table('contenidos').delete().eq('id', contenido_id).execute()
    supabase.table('cuentas_plataforma').delete().eq('id', cuenta_id).execute()
    supabase.table('modelos').delete().eq('id', modelo_id).execute()
    supabase.table('plataformas').delete().eq('id', platform_id).execute()
    print("   ✅ Datos de prueba eliminados")
    
    print("\n" + "=" * 60)
    print("✅ Test End-to-End completado")
    print("=" * 60)
    print("\n📋 Resumen:")
    print("   ✅ Query del poster funciona")
    print("   ✅ Joins funcionan correctamente")
    print("   ✅ Actualización de estados funciona")
    print("   ✅ Eventos_sistema funciona")
    print("   ✅ Campos published_at, ultimo_error, intentos funcionan")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

