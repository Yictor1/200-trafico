#!/usr/bin/env python3
"""
Script para ejecutar FASE 1: Crear esquema PRD en Supabase
Ejecuta el SQL de creación de tablas según el PRD
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Cargar variables de entorno
BASE_DIR = Path(__file__).resolve().parents[2]
env_path = BASE_DIR / '100trafico' / 'src' / '.env'
load_dotenv(dotenv_path=env_path)

# Configuración Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://osdpemjvcsmfbacmjlcv.supabase.co")
SUPABASE_DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")
SUPABASE_DB_HOST = os.getenv("SUPABASE_DB_HOST")

# Extraer información de conexión de la URL
if not SUPABASE_URL:
    print("❌ ERROR: SUPABASE_URL no configurado en .env")
    sys.exit(1)

# Parsear URL de Supabase para obtener host y database
# Formato: https://<project_ref>.supabase.co
if "supabase.co" in SUPABASE_URL:
    project_ref = SUPABASE_URL.split("//")[1].split(".")[0]
    db_host = f"{project_ref}.supabase.co"
    db_name = "postgres"
    db_user = "postgres"
else:
    print("❌ ERROR: No se pudo parsear SUPABASE_URL")
    sys.exit(1)

# Usar variables de entorno si están disponibles
if SUPABASE_DB_HOST:
    db_host = SUPABASE_DB_HOST
if not SUPABASE_DB_PASSWORD:
    SUPABASE_DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")

if not SUPABASE_DB_PASSWORD:
    print("❌ ERROR: SUPABASE_DB_PASSWORD no configurado en .env")
    print("   Necesitas la contraseña de la base de datos de Supabase")
    print("   Puedes obtenerla en: Supabase Dashboard > Settings > Database > Connection string")
    sys.exit(1)

# Leer script SQL
script_path = Path(__file__).parent / "fase1_create_prd_schema.sql"
if not script_path.exists():
    print(f"❌ ERROR: No se encuentra el script SQL: {script_path}")
    sys.exit(1)

with open(script_path, 'r', encoding='utf-8') as f:
    sql_script = f.read()

print("🚀 Iniciando FASE 1: Crear esquema PRD")
print(f"📂 Script: {script_path}")
print(f"🌐 Host: {db_host}")
print(f"📊 Database: {db_name}")
print()

try:
    # Conectar a Supabase
    print("🔌 Conectando a Supabase...")
    conn = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=SUPABASE_DB_PASSWORD,
        port=5432,
        sslmode='require'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    print("✅ Conexión exitosa")
    print()
    
    # Ejecutar script SQL
    print("📝 Ejecutando script SQL...")
    print("   (Esto puede tardar unos segundos)")
    print()
    
    cursor.execute(sql_script)
    
    print("✅ Script ejecutado exitosamente")
    print()
    
    # Verificar que las tablas se crearon
    print("🔍 Verificando tablas creadas...")
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('modelos', 'plataformas', 'cuentas_plataforma', 'contenidos', 'publicaciones', 'eventos_sistema')
        ORDER BY table_name;
    """)
    
    tables = cursor.fetchall()
    expected_tables = ['modelos', 'plataformas', 'cuentas_plataforma', 'contenidos', 'publicaciones', 'eventos_sistema']
    created_tables = [t[0] for t in tables]
    
    print()
    for table in expected_tables:
        if table in created_tables:
            print(f"  ✅ {table}")
        else:
            print(f"  ❌ {table} (NO ENCONTRADA)")
    
    print()
    
    # Verificar tipos ENUM
    print("🔍 Verificando tipos ENUM...")
    cursor.execute("""
        SELECT typname 
        FROM pg_type 
        WHERE typname IN ('estado_modelo', 'estado_contenido', 'estado_publicacion')
        ORDER BY typname;
    """)
    
    enums = cursor.fetchall()
    expected_enums = ['estado_modelo', 'estado_contenido', 'estado_publicacion']
    created_enums = [e[0] for e in enums]
    
    print()
    for enum in expected_enums:
        if enum in created_enums:
            print(f"  ✅ {enum}")
        else:
            print(f"  ❌ {enum} (NO ENCONTRADO)")
    
    print()
    
    if len(created_tables) == len(expected_tables) and len(created_enums) == len(expected_enums):
        print("🎉 FASE 1 completada exitosamente!")
        print()
        print("📋 Resumen:")
        print(f"   - {len(created_tables)} tablas creadas")
        print(f"   - {len(created_enums)} tipos ENUM creados")
        print()
        print("✅ El esquema PRD está listo para usar")
        print("   Las tablas antiguas permanecen intactas")
    else:
        print("⚠️  ADVERTENCIA: Algunas tablas o tipos no se crearon correctamente")
        print("   Revisa los errores arriba")
    
    cursor.close()
    conn.close()
    
except psycopg2.Error as e:
    print(f"❌ ERROR de base de datos: {e}")
    print()
    print("💡 Posibles soluciones:")
    print("   1. Verifica que SUPABASE_DB_PASSWORD esté correcto en .env")
    print("   2. Verifica que la conexión a Supabase esté disponible")
    print("   3. Revisa los logs de Supabase para más detalles")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ ERROR inesperado: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)



