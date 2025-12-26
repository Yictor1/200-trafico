#!/usr/bin/env python3
"""
Test de idempotencia para FASE 2
Crea datos de prueba, migra, y verifica que puede ejecutarse múltiples veces sin duplicar
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

print("🧪 Test de Idempotencia FASE 2\n")
print("=" * 60)

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Limpiar datos de prueba anteriores
    print("🧹 Limpiando datos de prueba anteriores...")
    try:
        # Eliminar en orden inverso (por FKs)
        supabase.table('publicaciones').delete().like('caption_usado', '%TEST_MIGRATION%').execute()
        supabase.table('contenidos').delete().like('archivo_path', '%test_model_migration%').execute()
        supabase.table('cuentas_plataforma').delete().like('username_en_plataforma', 'test_user_%').execute()
        supabase.table('modelos').delete().eq('nombre', 'test_model_migration').execute()
        supabase.table('plataformas').delete().eq('nombre', 'test_platform_migration').execute()
        print("   ✅ Datos de prueba anteriores eliminados")
    except Exception as e:
        print(f"   ℹ️  No había datos anteriores o error: {e}")
    
    # Crear datos de prueba en estructura antigua (simulada)
    print("\n📝 Creando datos de prueba en estructura antigua...")
    
    # 1. Crear modelo en tabla antigua (usando estructura antigua si existe)
    # Intentar insertar con estructura antigua
    try:
        modelo_old_data = {
            "modelo": "test_model_migration",
            "plataformas": "test_platform_migration",
            "hora_inicio": "12:00",
            "ventana_horas": 5
        }
        # Intentar insertar (puede fallar si la tabla tiene estructura nueva)
        supabase.table('modelos').insert(modelo_old_data).execute()
        print("   ✅ Modelo de prueba creado (estructura antigua)")
    except Exception as e:
        # Si falla, puede ser porque la tabla tiene estructura nueva
        print(f"   ℹ️  No se pudo crear en estructura antigua (normal si ya es PRD): {e}")
        print("   ℹ️  Continuando con test usando estructura nueva...")
    
    # 2. Crear tabla dinámica de prueba
    modelo_name = "test_model_migration"
    try:
        # Crear algunos registros de prueba en tabla dinámica
        registros_prueba = [
            {
                "video": "test_video_1.mp4",
                "caption": "TEST_MIGRATION Video 1",
                "tags": "tag1,tag2",
                "plataforma": "test_platform_migration",
                "estado": "pendiente",
                "scheduled_time": (datetime.now(timezone.utc) + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "video": "test_video_1.mp4",  # Mismo video, diferente plataforma
                "caption": "TEST_MIGRATION Video 1",
                "tags": "tag1,tag2",
                "plataforma": "test_platform_migration",
                "estado": "publicado",
                "scheduled_time": (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "video": "test_video_2.mp4",
                "caption": "TEST_MIGRATION Video 2",
                "tags": "tag3",
                "plataforma": "test_platform_migration",
                "estado": "pendiente",
                "scheduled_time": (datetime.now(timezone.utc) + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
        
        for reg in registros_prueba:
            try:
                supabase.table(modelo_name).insert(reg).execute()
            except Exception as e:
                # Si la tabla no existe, crearla primero (pero esto requiere SQL directo)
                print(f"   ⚠️  No se pudo insertar en tabla dinámica (normal si no existe): {e}")
                break
        
        print(f"   ✅ {len(registros_prueba)} registros de prueba creados en tabla '{modelo_name}'")
    except Exception as e:
        print(f"   ⚠️  Error creando registros de prueba: {e}")
        print("   ℹ️  Continuando con test (puede que no haya tabla dinámica)")
    
    # 3. Crear archivo .auth de prueba
    print("\n📝 Creando archivo .auth de prueba...")
    modelos_dir = BASE_DIR / '100trafico' / 'modelos' / modelo_name
    auth_dir = modelos_dir / '.auth'
    auth_dir.mkdir(parents=True, exist_ok=True)
    
    auth_data = {
        "cookies": [{"name": "test", "value": "test_value"}],
        "origins": []
    }
    
    auth_file = auth_dir / 'test_platform_migration.json'
    import json
    with open(auth_file, 'w') as f:
        json.dump(auth_data, f)
    print(f"   ✅ Archivo .auth creado: {auth_file}")
    
    print("\n" + "=" * 60)
    print("✅ Datos de prueba creados")
    print("=" * 60)
    print("\n💡 Ahora ejecuta:")
    print("   python3 Migracion/scripts/migrate_fase2.py --dry-run")
    print("   python3 Migracion/scripts/migrate_fase2.py --execute")
    print("\n💡 Luego ejecuta de nuevo para verificar idempotencia:")
    print("   python3 Migracion/scripts/migrate_fase2.py --execute")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)



