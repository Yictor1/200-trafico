#!/bin/bash
# Script para verificar que los permisos estén correctamente configurados

echo "=========================================="
echo "🔍 VERIFICACIÓN DE PERMISOS (Post-Fix)"
echo "=========================================="
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar directorio Telegram Bot API
echo "📁 Verificando directorio Telegram Bot API..."
echo ""

if [ -d ~/.telegram-bot-api ]; then
    echo -e "${GREEN}✅ Directorio existe${NC}"
    
    # Verificar propietario
    OWNER=$(stat -c '%U' ~/.telegram-bot-api)
    if [ "$OWNER" = "$USER" ]; then
        echo -e "${GREEN}✅ Propietario correcto: $OWNER${NC}"
    else
        echo -e "${RED}❌ Propietario incorrecto: $OWNER (debería ser $USER)${NC}"
    fi
    
    # Verificar permisos
    PERMS=$(stat -c '%a' ~/.telegram-bot-api)
    if [ "$PERMS" = "777" ]; then
        echo -e "${GREEN}✅ Permisos correctos: $PERMS (lectura/escritura para Docker)${NC}"
    elif [ "$PERMS" = "755" ] || [ "$PERMS" = "775" ]; then
        echo -e "${YELLOW}⚠️  Permisos: $PERMS (puede causar problemas con Docker, recomendado: 777)${NC}"
    else
        echo -e "${YELLOW}⚠️  Permisos: $PERMS (puede funcionar, pero recomendado: 777)${NC}"
    fi
    
else
    echo -e "${RED}❌ Directorio no existe: ~/.telegram-bot-api${NC}"
fi

echo ""
echo "📝 Verificando código de bot_central.py..."
echo ""

# Verificar que el código usa shutil.copy2
if grep -q "shutil.copy2" /home/victor/100-trafico/100trafico/src/project/bot_central.py; then
    echo -e "${GREEN}✅ Código actualizado (usa shutil.copy2 sin sudo)${NC}"
else
    echo -e "${YELLOW}⚠️  Código puede no estar actualizado${NC}"
fi

echo ""
echo "🐳 Verificando contenedor Docker..."
echo ""

# Verificar si docker necesita sudo
if docker ps &>/dev/null; then
    CONTAINER=$(docker ps --filter "name=telegram-bot-api" --format "{{.Names}}")
    if [ -n "$CONTAINER" ]; then
        echo -e "${GREEN}✅ Contenedor corriendo: $CONTAINER${NC}"
    else
        echo -e "${YELLOW}⚠️  Contenedor no está corriendo${NC}"
        echo "   Iniciar con: ./scripts/start_local_bot_api.sh"
    fi
else
    echo -e "${YELLOW}⚠️  Docker requiere permisos (usa newgrp docker o reinicia sesión)${NC}"
fi

echo ""
echo "=========================================="
echo "📊 RESUMEN"
echo "=========================================="
echo ""

# Verificar todo
ALL_GOOD=true

if [ -d ~/.telegram-bot-api ]; then
    OWNER=$(stat -c '%U' ~/.telegram-bot-api)
    if [ "$OWNER" != "$USER" ]; then
        ALL_GOOD=false
    fi
    
    if ! grep -q "shutil.copy2" /home/victor/100-trafico/100trafico/src/project/bot_central.py; then
        ALL_GOOD=false
    fi
else
    ALL_GOOD=false
fi

if [ "$ALL_GOOD" = true ]; then
    echo -e "${GREEN}✅ TODO CONFIGURADO CORRECTAMENTE${NC}"
    echo ""
    echo "🚀 Puedes iniciar el bot sin problemas de sudo:"
    echo "   cd /home/victor/100-trafico/100trafico"
    echo "   source ../.venv/bin/activate"
    echo "   python scripts/start_prueba_con_monitor.py"
    echo ""
else
    echo -e "${YELLOW}⚠️  Algunos elementos necesitan atención${NC}"
    echo ""
    echo "Revisa los mensajes arriba y aplica las correcciones necesarias."
    echo ""
fi

echo "=========================================="

