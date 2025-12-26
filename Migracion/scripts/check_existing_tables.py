#!/usr/bin/env python3
"""Script para verificar qué tablas existen en Supabase"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

BASE_DIR = Path(__file__).resolve().parents[2]
env_path = BASE_DIR / '100trafico' / 'src' / '.env'
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://osdpemjvcsmfbacmjlcv.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_KEY:
    print("❌ ERROR: SUPABASE_ANON_KEY no configurado")
    sys.exit(1)

print("🔍 Verificando tablas existentes en Supabase...\n")

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Intentar leer tabla modelos (antigua)
    print("📋 Tabla 'modelos' (antigua):")
    try:
        result = supabase.table('modelos').select("*").limit(5).execute()
        if result.data:
            print(f"   ✅ Existe con {len(result.data)} registros (mostrando primeros 5)")
            for m in result.data:
                print(f"      - {m}")
        else:
            print("   ✅ Existe pero está vacía")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Intentar leer algunas tablas dinámicas conocidas
    print("\n📋 Tablas dinámicas conocidas:")
    posibles_modelos = ['yic', 'demo', 'test']
    for modelo in posibles_modelos:
        try:
            result = supabase.table(modelo).select("*").limit(1).execute()
            if result.data:
                print(f"   ✅ Tabla '{modelo}': {len(result.data)} registros")
                print(f"      Estructura: {list(result.data[0].keys())}")
            else:
                print(f"   ✅ Tabla '{modelo}': existe pero vacía")
        except Exception as e:
            print(f"   ❌ Tabla '{modelo}': {str(e)[:50]}")
    
    # Verificar tabla modelos nueva (PRD)
    print("\n📋 Tabla 'modelos' (nueva PRD):")
    try:
        result = supabase.table('modelos').select("id, nombre").limit(5).execute()
        if result.data:
            print(f"   ✅ Existe con estructura PRD: {len(result.data)} registros")
            for m in result.data:
                print(f"      - {m.get('nombre', 'N/A')}")
        else:
            print("   ✅ Existe pero está vacía")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()



