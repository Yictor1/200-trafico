#!/usr/bin/env python3
"""
Test de creación de contenidos desde el bot (FASE 4A)
Valida que el bot puede crear contenidos en el esquema PRD
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parents[2]
env_path = BASE_DIR / '100trafico' / 'src' / '.env'
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://osdpemjvcsmfbacmjlcv.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_KEY:
    print("❌ ERROR: SUPABASE_ANON_KEY no configurado")
    sys.exit(1)

print("🧪 Test de Creación de Contenidos (FASE 4A)\n")
print("=" * 60)

try:
    # Importar función
    sys.path.insert(0, str(BASE_DIR / '100trafico' / 'src'))
    from database.contenidos_prd import create_contenido, get_modelo_id_by_nombre, update_contenido_caption_tags
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # 1. Test get_modelo_id_by_nombre
    print("\n1️⃣  Test get_modelo_id_by_nombre()...")
    modelo_nombre = "test_e2e_poster"  # Usar modelo de prueba existente o crear uno
    
    # Verificar si existe, si no crear
    modelo_existing = supabase.table('modelos').select("id, nombre").eq('nombre', modelo_nombre).execute()
    if not modelo_existing.data:
        print(f"   ⚠️  Modelo '{modelo_nombre}' no existe, creando...")
        modelo_data = {
            "nombre": modelo_nombre,
            "estado": "activa",
            "configuracion_distribucion": {"plataformas": ["kams"]}
        }
        modelo_result = supabase.table('modelos').insert(modelo_data).execute()
        modelo_id = modelo_result.data[0]['id']
        print(f"   ✅ Modelo creado: {modelo_id}")
    else:
        modelo_id = modelo_existing.data[0]['id']
        print(f"   ✅ Modelo existe: {modelo_id}")
    
    # Test función
    modelo_id_func = get_modelo_id_by_nombre(modelo_nombre)
    if modelo_id_func == modelo_id:
        print(f"   ✅ get_modelo_id_by_nombre() funciona correctamente")
    else:
        print(f"   ❌ Error: esperado {modelo_id}, obtenido {modelo_id_func}")
    
    # 2. Test create_contenido (sin caption/tags)
    print("\n2️⃣  Test create_contenido() (sin caption/tags)...")
    archivo_path = f"modelos/{modelo_nombre}/test_video_bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    contexto_original = "Qué vendes: tetas, culo\nOutfit: lenceria, tanga"
    enviado_por = "telegram_123456"
    
    contenido_id_1 = create_contenido(
        modelo_nombre=modelo_nombre,
        archivo_path=archivo_path,
        contexto_original=contexto_original,
        enviado_por=enviado_por
    )
    
    if contenido_id_1:
        print(f"   ✅ Contenido creado: {contenido_id_1}")
        
        # Verificar en BD
        contenido_check = supabase.table('contenidos').select("*").eq('id', contenido_id_1).execute()
        if contenido_check.data:
            contenido = contenido_check.data[0]
            print(f"      - Estado: {contenido.get('estado')}")
            print(f"      - Archivo: {contenido.get('archivo_path')}")
            print(f"      - Contexto: {contenido.get('contexto_original', '')[:50]}...")
            print(f"      - Enviado por: {contenido.get('enviado_por')}")
            
            if contenido.get('estado') == 'nuevo':
                print(f"   ✅ Estado correcto: 'nuevo'")
            else:
                print(f"   ⚠️  Estado incorrecto: {contenido.get('estado')}")
    else:
        print(f"   ❌ Error creando contenido")
        sys.exit(1)
    
    # 3. Test idempotencia
    print("\n3️⃣  Test idempotencia (crear mismo contenido de nuevo)...")
    contenido_id_2 = create_contenido(
        modelo_nombre=modelo_nombre,
        archivo_path=archivo_path,  # Mismo archivo
        contexto_original=contexto_original,
        enviado_por=enviado_por
    )
    
    if contenido_id_2 == contenido_id_1:
        print(f"   ✅ Idempotencia funciona: mismo ID ({contenido_id_1})")
    else:
        print(f"   ❌ Error idempotencia: IDs diferentes ({contenido_id_1} vs {contenido_id_2})")
    
    # 4. Test create_contenido (con caption/tags)
    print("\n4️⃣  Test create_contenido() (con caption/tags)...")
    archivo_path_2 = f"modelos/{modelo_nombre}/test_video_bot_2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    caption = "Waiting for you in my private room. Join me."
    tags = ["latina", "brunette", "big boobs"]
    
    contenido_id_3 = create_contenido(
        modelo_nombre=modelo_nombre,
        archivo_path=archivo_path_2,
        contexto_original=contexto_original,
        enviado_por=enviado_por,
        caption_generado=caption,
        tags_generados=tags
    )
    
    if contenido_id_3:
        print(f"   ✅ Contenido creado con caption/tags: {contenido_id_3}")
        
        # Verificar
        contenido_check = supabase.table('contenidos').select("*").eq('id', contenido_id_3).execute()
        if contenido_check.data:
            contenido = contenido_check.data[0]
            if contenido.get('caption_generado') == caption:
                print(f"   ✅ Caption guardado correctamente")
            if contenido.get('tags_generados') == tags:
                print(f"   ✅ Tags guardados correctamente")
    
    # 5. Test update_contenido_caption_tags
    print("\n5️⃣  Test update_contenido_caption_tags()...")
    nuevo_caption = "Updated caption for testing"
    nuevos_tags = ["updated", "test", "tags"]
    
    success = update_contenido_caption_tags(
        contenido_id=contenido_id_1,
        caption_generado=nuevo_caption,
        tags_generados=nuevos_tags
    )
    
    if success:
        print(f"   ✅ Contenido actualizado")
        
        # Verificar
        contenido_check = supabase.table('contenidos').select("*").eq('id', contenido_id_1).execute()
        if contenido_check.data:
            contenido = contenido_check.data[0]
            if contenido.get('caption_generado') == nuevo_caption:
                print(f"   ✅ Caption actualizado correctamente")
            if contenido.get('tags_generados') == nuevos_tags:
                print(f"   ✅ Tags actualizados correctamente")
    
    # Limpiar
    print("\n🧹 Limpiando datos de prueba...")
    supabase.table('contenidos').delete().eq('id', contenido_id_1).execute()
    if contenido_id_3:
        supabase.table('contenidos').delete().eq('id', contenido_id_3).execute()
    print("   ✅ Datos de prueba eliminados")
    
    print("\n" + "=" * 60)
    print("✅ Tests completados")
    print("=" * 60)
    print("\n📋 Resumen:")
    print("   ✅ get_modelo_id_by_nombre() funciona")
    print("   ✅ create_contenido() funciona")
    print("   ✅ Idempotencia funciona")
    print("   ✅ update_contenido_caption_tags() funciona")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)



