#!/bin/bash

# Cambiar al directorio raíz del proyecto (donde está este script)
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SCRIPT_DIR"

# Cargar variables desde src/.env
ENV_FILE="$SCRIPT_DIR/src/.env"

if [ -f "$ENV_FILE" ]; then
    # Exportar variables automáticamente
    export $(grep -v '^#' "$ENV_FILE" | xargs)
else
    echo "❌ ERROR: No se encontró el archivo $ENV_FILE"
    echo "   Asegúrate de que el archivo existe en: $ENV_FILE"
    exit 1
fi

# Detectar usuario real si se ejecuta con sudo
if [ -n "$SUDO_USER" ]; then
    REAL_USER="$SUDO_USER"
    REAL_HOME=$(getent passwd "$SUDO_USER" | cut -d: -f6)
else
    REAL_USER="$USER"
    REAL_HOME="$HOME"
fi

# Configuración
LOCAL_PORT=8081
WORK_DIR="${REAL_HOME}/.telegram-bot-api"

# Verificar si se configuraron las credenciales
if [ -z "$API_ID" ] || [ -z "$API_HASH" ]; then
    echo "❌ ERROR: API_ID y API_HASH no encontrados en $ENV_FILE"
    exit 1
fi

# Crear directorio de trabajo para el servidor local
mkdir -p "$WORK_DIR"

# Detectar si necesitamos usar sudo para docker
DOCKER_CMD="docker"
if ! docker ps &>/dev/null; then
    if sudo docker ps &>/dev/null; then
        DOCKER_CMD="sudo docker"
        echo "ℹ️  Usando sudo para ejecutar Docker (usuario no está en grupo docker)"
    else
        echo "❌ ERROR: No se puede acceder a Docker"
        echo "   Soluciones:"
        echo "   1. Agregar usuario al grupo docker: sudo usermod -aG docker $USER"
        echo "   2. Luego cerrar sesión y volver a iniciar sesión"
        echo "   3. O ejecutar este script con sudo: sudo $0"
        exit 1
    fi
fi

# Detener y eliminar contenedor existente si existe
if $DOCKER_CMD ps -a --format '{{.Names}}' | grep -q "^telegram-bot-api$"; then
    echo "🛑 Deteniendo contenedor existente..."
    $DOCKER_CMD stop telegram-bot-api &>/dev/null
    $DOCKER_CMD rm telegram-bot-api &>/dev/null
fi

echo "🚀 Iniciando servidor local de Telegram Bot API..."
echo "📂 Directorio de datos: $WORK_DIR"
echo "🔌 Puerto: $LOCAL_PORT"

# Ejecutar contenedor Docker
# Usamos aiogram/telegram-bot-api que es una imagen mantenida y ligera
# Con --local para eliminar límites de tamaño
$DOCKER_CMD run -d \
  --name=telegram-bot-api \
  --restart=always \
  -p $LOCAL_PORT:8081 \
  -v "$WORK_DIR":/var/lib/telegram-bot-api \
  -e TELEGRAM_API_ID=$API_ID \
  -e TELEGRAM_API_HASH=$API_HASH \
  -e TELEGRAM_LOCAL=1 \
  aiogram/telegram-bot-api:latest \
  --api-id=$API_ID \
  --api-hash=$API_HASH \
  --local

if [ $? -eq 0 ]; then
    echo "✅ Servidor iniciado correctamente en http://localhost:$LOCAL_PORT"
    echo "   Ahora tu bot puede descargar archivos de hasta 2GB."
else
    echo "❌ Error al iniciar el contenedor Docker."
    exit 1
fi
