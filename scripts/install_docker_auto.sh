#!/bin/bash
# Script que intenta instalar Docker automáticamente

echo "🔧 Instalando Docker..."
echo ""

# Intentar con sudo -S (lee contraseña de stdin)
# Si no funciona, mostrar instrucciones

if command -v docker &> /dev/null && docker ps &> /dev/null 2>&1; then
    echo "✅ Docker ya está instalado y funcionando"
    exit 0
fi

echo "📦 Instalando Docker (se requiere contraseña de sudo)..."
echo ""

# Intentar instalación
sudo apt update && \
sudo apt install -y docker.io docker-compose && \
sudo systemctl start docker && \
sudo systemctl enable docker && \
sudo usermod -aG docker $USER && \
echo "" && \
echo "✅ Docker instalado exitosamente" && \
echo "" && \
echo "⚠️  IMPORTANTE: Ejecuta 'newgrp docker' o cierra sesión y vuelve a iniciar sesión"

