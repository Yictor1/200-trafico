#!/bin/bash
# Script de Verificación del Monitor de Descargas
# Verifica que todo esté listo para la primera prueba

echo "=========================================="
echo "🔍 VERIFICACIÓN DEL MONITOR DE DESCARGAS"
echo "=========================================="
echo ""

# Variables
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ERRORS=0
WARNINGS=0

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función de verificación
check() {
    local name="$1"
    local command="$2"
    local critical="${3:-false}"
    
    echo -n "Verificando $name... "
    
    if eval "$command" &>/dev/null; then
        echo -e "${GREEN}✅${NC}"
        return 0
    else
        if [ "$critical" = "true" ]; then
            echo -e "${RED}❌ CRÍTICO${NC}"
            ((ERRORS++))
        else
            echo -e "${YELLOW}⚠️  Advertencia${NC}"
            ((WARNINGS++))
        fi
        return 1
    fi
}

# Función para verificar archivo
check_file() {
    local name="$1"
    local file="$2"
    local critical="${3:-false}"
    
    check "$name" "test -f '$file'" "$critical"
    if [ $? -ne 0 ] && [ "$critical" = "true" ]; then
        echo "   Falta: $file"
    fi
}

# Función para verificar directorio
check_dir() {
    local name="$1"
    local dir="$2"
    
    check "$name" "test -d '$dir'" "false"
    if [ $? -ne 0 ]; then
        echo "   Creando: $dir"
        mkdir -p "$dir"
    fi
}

echo "📁 Verificando Estructura de Archivos..."
echo ""

# Archivos críticos
check_file "Monitor principal" "$BASE_DIR/workers/monitor_descarga.py" "true"
check_file "Script de inicio" "$BASE_DIR/scripts/start_prueba_con_monitor.py" "true"
check_file "main.py" "$BASE_DIR/main.py" "true"
check_file "bot_central.py" "$BASE_DIR/src/project/bot_central.py" "true"

# Archivos de configuración
check_file "archivo .env" "$BASE_DIR/src/.env" "true"

# Directorios
echo ""
echo "📂 Verificando Directorios..."
echo ""
check_dir "logs/" "$BASE_DIR/logs"
check_dir "modelos/" "$BASE_DIR/modelos"

# Python y dependencias
echo ""
echo "🐍 Verificando Python y Dependencias..."
echo ""

check "Python 3" "python3 --version"
check "Entorno virtual" "test -f '$BASE_DIR/../.venv/bin/python3'"

if [ -f "$BASE_DIR/../.venv/bin/python3" ]; then
    PYTHON_EXE="$BASE_DIR/../.venv/bin/python3"
else
    PYTHON_EXE="python3"
fi

check "python-telegram-bot" "$PYTHON_EXE -c 'import telegram'" "true"
check "python-dotenv" "$PYTHON_EXE -c 'import dotenv'" "true"
check "asyncio" "$PYTHON_EXE -c 'import asyncio'"

# Verificar variables de entorno
echo ""
echo "🔐 Verificando Variables de Entorno..."
echo ""

if [ -f "$BASE_DIR/src/.env" ]; then
    source "$BASE_DIR/src/.env"
    
    if [ -n "$TELEGRAM_TOKEN" ]; then
        echo -e "TELEGRAM_TOKEN: ${GREEN}✅ Configurado${NC}"
    else
        echo -e "TELEGRAM_TOKEN: ${RED}❌ NO configurado${NC}"
        ((ERRORS++))
    fi
    
    if [ -n "$ADMIN_ID" ]; then
        echo -e "ADMIN_ID: ${GREEN}✅ Configurado${NC}"
    else
        echo -e "ADMIN_ID: ${YELLOW}⚠️  NO configurado${NC} (notificaciones desactivadas)"
        ((WARNINGS++))
    fi
else
    echo -e "${RED}❌ Archivo .env no encontrado${NC}"
    ((ERRORS++))
fi

# Docker (servidor local Telegram)
echo ""
echo "🐳 Verificando Servidor Local de Telegram..."
echo ""

check "Docker instalado" "docker --version" "false"

if docker ps | grep -q telegram-bot-api; then
    echo -e "Servidor Telegram: ${GREEN}✅ Corriendo${NC}"
else
    echo -e "Servidor Telegram: ${YELLOW}⚠️  No corriendo${NC}"
    echo "   Para iniciarlo: ./scripts/start_local_bot_api.sh"
    ((WARNINGS++))
fi

# Permisos
echo ""
echo "🔒 Verificando Permisos..."
echo ""

check "Script monitor ejecutable" "test -x '$BASE_DIR/workers/monitor_descarga.py'" "false"
if [ $? -ne 0 ]; then
    echo "   Corrigiendo: chmod +x"
    chmod +x "$BASE_DIR/workers/monitor_descarga.py"
fi

check "Script inicio ejecutable" "test -x '$BASE_DIR/scripts/start_prueba_con_monitor.py'" "false"
if [ $? -ne 0 ]; then
    echo "   Corrigiendo: chmod +x"
    chmod +x "$BASE_DIR/scripts/start_prueba_con_monitor.py"
fi

# Verificar sudo (para corrección de permisos)
echo ""
echo -n "Verificando permisos sudo... "
if sudo -n true 2>/dev/null; then
    echo -e "${GREEN}✅ (sin contraseña)${NC}"
else
    echo -e "${YELLOW}⚠️  Requiere contraseña${NC}"
    echo "   El monitor puede necesitar sudo para corregir permisos"
    ((WARNINGS++))
fi

# Espacio en disco
echo ""
echo "💾 Verificando Espacio en Disco..."
echo ""

AVAILABLE_GB=$(df -BG "$BASE_DIR" | tail -1 | awk '{print $4}' | sed 's/G//')
echo -n "Espacio disponible: ${AVAILABLE_GB}GB "

if [ "$AVAILABLE_GB" -gt 10 ]; then
    echo -e "${GREEN}✅${NC}"
elif [ "$AVAILABLE_GB" -gt 5 ]; then
    echo -e "${YELLOW}⚠️  Bajo${NC}"
    ((WARNINGS++))
else
    echo -e "${RED}❌ CRÍTICO${NC}"
    echo "   Videos grandes (hasta 4GB) requieren más espacio"
    ((ERRORS++))
fi

# Resumen
echo ""
echo "=========================================="
echo "📊 RESUMEN DE VERIFICACIÓN"
echo "=========================================="
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ TODO LISTO PARA LA PRUEBA${NC}"
    echo ""
    echo "🚀 Para iniciar el sistema con monitor:"
    echo "   cd $BASE_DIR"
    echo "   source ../.venv/bin/activate"
    echo "   python scripts/start_prueba_con_monitor.py"
    echo ""
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Advertencias: $WARNINGS${NC}"
    echo ""
    echo "El sistema puede funcionar, pero revisa las advertencias."
    echo ""
    echo "Para continuar de todas formas:"
    echo "   cd $BASE_DIR"
    echo "   python scripts/start_prueba_con_monitor.py"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Errores críticos: $ERRORS${NC}"
    echo -e "${YELLOW}⚠️  Advertencias: $WARNINGS${NC}"
    echo ""
    echo "Soluciona los errores críticos antes de continuar."
    echo ""
    echo "Ayuda:"
    echo "   - Variables de entorno: edita src/.env"
    echo "   - Dependencias Python: pip install -r requirements.txt"
    echo "   - Documentación: docs/MONITOR_DESCARGAS.md"
    echo ""
    exit 1
fi


