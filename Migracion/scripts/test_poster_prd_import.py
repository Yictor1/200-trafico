#!/usr/bin/env python3
"""Test de importación y funciones del poster_prd"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR / '100trafico' / 'src' / 'project'))

print("🧪 Test de importación poster_prd\n")

try:
    # Intentar importar
    from poster_prd import (
        get_pending_publicaciones,
        create_evento_sistema,
        update_publicacion_estado,
        get_worker_script_path,
        process_publicacion
    )
    print("✅ Todas las funciones importadas correctamente")
    
    # Verificar que las funciones existen
    functions = [
        get_pending_publicaciones,
        create_evento_sistema,
        update_publicacion_estado,
        get_worker_script_path,
        process_publicacion
    ]
    
    print(f"\n📋 Funciones disponibles: {len(functions)}")
    for func in functions:
        print(f"   ✅ {func.__name__}")
    
    print("\n✅ Poster PRD está listo para usar")
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)



