#!/bin/bash
# Script de validación para ETAPA 0 de FASE 5

echo "🔍 Validando ETAPA 0: main.py usa poster_prd.py"
echo "================================================"

# 1. Verificar que poster_prd.py existe
echo ""
echo "1️⃣ Verificando que poster_prd.py existe..."
if [ -f "100trafico/src/project/poster_prd.py" ]; then
    echo "   ✅ poster_prd.py existe"
else
    echo "   ❌ poster_prd.py NO existe"
    exit 1
fi

# 2. Verificar que main.py referencia poster_prd.py
echo ""
echo "2️⃣ Verificando que main.py usa poster_prd.py..."
if grep -q "poster_prd.py" 100trafico/main.py; then
    echo "   ✅ main.py referencia poster_prd.py"
else
    echo "   ❌ main.py NO referencia poster_prd.py"
    exit 1
fi

# 3. Verificar que main.py NO referencia poster.py legacy
echo ""
echo "3️⃣ Verificando que main.py NO usa poster.py legacy..."
if grep -q "poster\.py[^_]" 100trafico/main.py; then
    echo "   ❌ main.py todavía referencia poster.py legacy"
    exit 1
else
    echo "   ✅ main.py NO referencia poster.py legacy"
fi

# 4. Verificar que poster_prd.py se puede importar
echo ""
echo "4️⃣ Verificando que poster_prd.py se puede importar..."
cd 100trafico
if python3 -c "import sys; sys.path.insert(0, 'src'); from project.poster_prd import get_pending_publicaciones; print('   ✅ Importación exitosa')" 2>&1; then
    echo "   ✅ poster_prd.py se puede importar correctamente"
else
    echo "   ❌ Error importando poster_prd.py"
    exit 1
fi
cd ..

# 5. Verificar que poster.py legacy todavía existe (no eliminado)
echo ""
echo "5️⃣ Verificando que poster.py legacy todavía existe (no eliminado)..."
if [ -f "100trafico/src/project/poster.py" ]; then
    echo "   ✅ poster.py legacy todavía existe (correcto, no se eliminó)"
else
    echo "   ⚠️  poster.py legacy NO existe (puede ser correcto si ya se eliminó)"
fi

echo ""
echo "================================================"
echo "✅ Todas las validaciones pasaron"
echo ""
echo "📋 Próximos pasos:"
echo "   1. Ejecutar main.py brevemente para verificar que arranca"
echo "   2. Verificar que procesa publicaciones PRD correctamente"
echo "   3. Verificar que no hay procesos ejecutando poster.py legacy"
