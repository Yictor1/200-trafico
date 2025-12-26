#!/bin/bash
# Script para iniciar el frontend de 100-trafico

# Cambiar al directorio raíz del proyecto
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Iniciando frontend de 100-trafico..."
echo ""

# Ir al directorio del frontend
cd "$SCRIPT_DIR/admin_panel/frontend"

# Verificar si node_modules existe
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependencias..."
    npm install
fi

# Iniciar servidor de desarrollo
echo "✅ Iniciando servidor en http://localhost:3000"
echo ""
npm run dev





