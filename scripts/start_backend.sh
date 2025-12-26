#!/bin/bash
# Script para iniciar el backend de 100-trafico

# Cambiar al directorio raíz del proyecto
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Iniciando backend de 100-trafico..."
echo ""

# Ir al directorio del backend
cd "$SCRIPT_DIR/admin_panel/backend"

# Activar entorno virtual
echo "📦 Activando entorno virtual..."
source "$SCRIPT_DIR/.venv/bin/activate"

# Verificar si uvicorn está instalado
if ! command -v uvicorn &> /dev/null; then
    echo "❌ Error: uvicorn no está instalado"
    echo "   Ejecuta: pip install -r requirements.txt"
    exit 1
fi

# Verificar si el archivo .env existe
if [ ! -f "$SCRIPT_DIR/src/.env" ]; then
    echo "⚠️  Advertencia: Archivo .env no encontrado en src/"
    echo "   El backend puede no funcionar correctamente sin configuración"
fi

# Iniciar servidor
echo "✅ Iniciando servidor en http://localhost:8000"
echo ""
python -m uvicorn main:app --reload --port 8000





