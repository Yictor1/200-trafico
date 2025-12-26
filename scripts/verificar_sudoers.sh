#!/bin/bash
# Script de Verificación de Configuración Sudoers para 100-Tráfico
# Verifica que la configuración sin contraseña esté correcta

echo "=========================================="
echo "🔐 VERIFICACIÓN DE SUDOERS"
echo "=========================================="
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0

echo "1️⃣ Verificando archivo de configuración..."
if [ -f /etc/sudoers.d/100trafico ]; then
    echo -e "${GREEN}✅ Archivo existe: /etc/sudoers.d/100trafico${NC}"
    
    # Verificar permisos del archivo
    PERMS=$(stat -c '%a' /etc/sudoers.d/100trafico)
    if [ "$PERMS" = "440" ]; then
        echo -e "${GREEN}✅ Permisos correctos: 0440${NC}"
    else
        echo -e "${RED}❌ Permisos incorrectos: $PERMS (debe ser 0440)${NC}"
        echo "   Corrige con: sudo chmod 0440 /etc/sudoers.d/100trafico"
        ((ERRORS++))
    fi
else
    echo -e "${RED}❌ Archivo no encontrado: /etc/sudoers.d/100trafico${NC}"
    echo "   Instala con: sudo cp config/sudoers-100trafico /etc/sudoers.d/100trafico"
    ((ERRORS++))
fi

echo ""
echo "2️⃣ Verificando sintaxis de sudoers..."
if echo "0000" | sudo -S visudo -c &>/dev/null; then
    echo -e "${GREEN}✅ Sintaxis válida${NC}"
else
    echo -e "${RED}❌ Sintaxis inválida${NC}"
    echo "   Ejecuta: sudo visudo -c"
    ((ERRORS++))
fi

echo ""
echo "3️⃣ Probando chmod sin contraseña..."
# Crear archivo temporal
TEST_FILE=~/.telegram-bot-api/test_sudoers_verify.txt
touch "$TEST_FILE" 2>/dev/null

if sudo chmod 777 "$TEST_FILE" 2>/dev/null; then
    echo -e "${GREEN}✅ chmod funciona sin contraseña${NC}"
    rm -f "$TEST_FILE"
else
    echo -e "${RED}❌ chmod requiere contraseña o falló${NC}"
    echo "   Verifica configuración de sudoers"
    ((ERRORS++))
    rm -f "$TEST_FILE"
fi

echo ""
echo "4️⃣ Probando chown sin contraseña..."
touch "$TEST_FILE" 2>/dev/null

if sudo chown $USER:$USER "$TEST_FILE" 2>/dev/null; then
    echo -e "${GREEN}✅ chown funciona sin contraseña${NC}"
    rm -f "$TEST_FILE"
else
    echo -e "${RED}❌ chown requiere contraseña o falló${NC}"
    echo "   Verifica configuración de sudoers"
    ((ERRORS++))
    rm -f "$TEST_FILE"
fi

echo ""
echo "5️⃣ Verificando código Python..."
if grep -q "input=b'0000" /home/victor/100-trafico/100trafico/src/project/bot_central.py; then
    echo -e "${RED}❌ Contraseña hardcodeada encontrada en código${NC}"
    echo "   El código debe usar sudo sin -S ni contraseña"
    ((ERRORS++))
else
    echo -e "${GREEN}✅ Sin contraseña hardcodeada${NC}"
fi

echo ""
echo "=========================================="
echo "📊 RESUMEN"
echo "=========================================="
echo ""

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ CONFIGURACIÓN CORRECTA${NC}"
    echo ""
    echo "El sistema puede ejecutar chmod/chown sin contraseña"
    echo "en el directorio ~/.telegram-bot-api"
    echo ""
    echo "🚀 Listo para descargas automáticas"
else
    echo -e "${RED}❌ ERRORES ENCONTRADOS: $ERRORS${NC}"
    echo ""
    echo "Soluciona los errores arriba antes de continuar"
fi

echo "=========================================="

exit $ERRORS

