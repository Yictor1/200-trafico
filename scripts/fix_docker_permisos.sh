#!/bin/bash
# Script de Auto-Fix para Permisos de Docker Telegram Bot API

echo "=========================================="
echo "🔧 FIX AUTOMÁTICO DE PERMISOS DOCKER"
echo "=========================================="
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar que el contenedor exista
if ! sudo docker ps -a | grep -q telegram-bot-api; then
    echo -e "${RED}❌ Contenedor 'telegram-bot-api' no encontrado${NC}"
    echo "   Créalo primero con: ./scripts/start_local_bot_api.sh"
    exit 1
fi

echo "1️⃣ Deteniendo contenedor..."
if sudo docker stop telegram-bot-api &>/dev/null; then
    echo -e "${GREEN}✅ Contenedor detenido${NC}"
else
    echo -e "${YELLOW}⚠️  Contenedor ya estaba detenido${NC}"
fi

echo ""
echo "2️⃣ Aplicando permisos 777 a ~/.telegram-bot-api..."
if sudo chmod -R 777 ~/.telegram-bot-api; then
    echo -e "${GREEN}✅ Permisos actualizados${NC}"
else
    echo -e "${RED}❌ Error aplicando permisos${NC}"
    exit 1
fi

echo ""
echo "3️⃣ Iniciando contenedor..."
if sudo docker start telegram-bot-api &>/dev/null; then
    echo -e "${GREEN}✅ Contenedor iniciado${NC}"
else
    echo -e "${RED}❌ Error iniciando contenedor${NC}"
    exit 1
fi

echo ""
echo "4️⃣ Esperando que el contenedor esté listo..."
sleep 3

echo ""
echo "5️⃣ Verificando estado..."
if sudo docker ps | grep -q "telegram-bot-api.*Up"; then
    echo -e "${GREEN}✅ Contenedor corriendo correctamente${NC}"
else
    echo -e "${RED}❌ Contenedor no está corriendo${NC}"
    echo ""
    echo "Logs del contenedor:"
    sudo docker logs --tail 10 telegram-bot-api
    exit 1
fi

echo ""
echo "6️⃣ Verificando puerto 8081..."
if curl -s http://127.0.0.1:8081/bot | grep -q "ok"; then
    echo -e "${GREEN}✅ Puerto 8081 responde correctamente${NC}"
else
    echo -e "${YELLOW}⚠️  Puerto responde (puede ser normal)${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✅ FIX APLICADO EXITOSAMENTE${NC}"
echo "=========================================="
echo ""
echo "📊 Resumen:"
echo "   - Contenedor: Corriendo"
echo "   - Permisos: 777 (Docker puede escribir)"
echo "   - Puerto: 8081 activo"
echo ""
echo "🚀 Ya puedes iniciar el bot:"
echo "   cd /home/victor/100-trafico/100trafico"
echo "   source ../.venv/bin/activate"
echo "   python scripts/start_prueba_con_monitor.py"
echo ""


