# 📋 Guía de Instalación Completa para Agente de Cursor

Esta guía está diseñada para ser ejecutada por un agente de Cursor en un nuevo PC. Sigue los pasos en orden y verifica cada uno antes de continuar.

---

## 🎯 Objetivo

Instalar completamente el sistema **100 Tráfico** en un nuevo PC, incluyendo todas las dependencias, configuraciones y servicios necesarios.

---

## 📋 Checklist Pre-Instalación

Antes de comenzar, verifica que tengas acceso a:

- [ ] Credenciales de Supabase (URL y ANON_KEY)
- [ ] API Key de Google Gemini
- [ ] Token del bot de Telegram (si se usará)
- [ ] API_ID y API_HASH de Telegram (para servidor local de archivos grandes)
- [ ] Acceso a internet estable
- [ ] Permisos de sudo en el sistema

---

## PASO 1: Verificar Sistema Operativo y Versiones

### 1.1 Verificar Sistema Operativo

```bash
# Verificar que estamos en Linux
uname -a

# Verificar distribución
cat /etc/os-release
```

**Resultado esperado**: Sistema Linux (Ubuntu/Debian recomendado)

### 1.2 Verificar Versiones de Software Base

```bash
# Verificar Python (debe ser 3.10 o superior)
python3 --version

# Si no está instalado o es versión antigua, instalar Python 3.10+
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3-pip

# Verificar Node.js (debe ser 18 o superior)
node --version

# Si no está instalado, instalar Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Verificar npm
npm --version

# Verificar Git
git --version

# Si no está instalado
sudo apt install -y git
```

**Verificación**:
```bash
python3 --version  # Debe mostrar Python 3.10.x o superior
node --version     # Debe mostrar v18.x.x o superior
npm --version      # Debe mostrar versión compatible
git --version      # Debe mostrar cualquier versión de git
```

---

## PASO 2: Instalar Docker

### 2.1 Verificar si Docker ya está instalado

```bash
docker --version
docker ps
```

Si ambos comandos funcionan sin sudo, **saltar al PASO 3**.

### 2.2 Instalar Docker

```bash
# Actualizar paquetes
sudo apt update

# Instalar dependencias
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Agregar clave GPG oficial de Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Agregar repositorio de Docker
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Iniciar y habilitar Docker
sudo systemctl start docker
sudo systemctl enable docker

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Verificar instalación
sudo docker --version
sudo docker ps
```

**Verificación**:
```bash
docker --version  # Debe mostrar versión de Docker
docker ps         # Debe mostrar lista vacía o contenedores
```

**Nota**: Si `docker ps` requiere sudo, ejecutar `newgrp docker` o cerrar sesión y volver a iniciar.

---

## PASO 3: Clonar el Repositorio

### 3.1 Navegar al directorio de trabajo

```bash
# Crear directorio si no existe
mkdir -p ~/Escritorio
cd ~/Escritorio
```

### 3.2 Clonar el repositorio

```bash
# Clonar el repositorio (reemplazar con la URL real del repositorio)
git clone https://github.com/Yictor1/100-trafico.git SkyFlow_Porn-master

# Navegar al directorio del proyecto
cd SkyFlow_Porn-master/100-trafico
```

**Verificación**:
```bash
pwd  # Debe mostrar: /home/[usuario]/Escritorio/SkyFlow_Porn-master/100-trafico
ls -la  # Debe mostrar estructura del proyecto
```

---

## PASO 4: Configurar Entorno Virtual de Python

### 4.1 Crear entorno virtual

```bash
# Crear entorno virtual
python3 -m venv .venv

# Verificar que se creó
ls -la .venv
```

### 4.2 Activar entorno virtual

```bash
# Activar entorno virtual
source .venv/bin/activate

# Verificar activación (debe mostrar (.venv) al inicio del prompt)
which python  # Debe apuntar a .venv/bin/python
```

**Verificación**:
```bash
python --version  # Debe mostrar Python 3.10.x o superior
which python      # Debe mostrar: .../100-trafico/.venv/bin/python
```

---

## PASO 5: Instalar Dependencias de Python

### 5.1 Actualizar pip

```bash
# Asegurar que pip está actualizado
pip install --upgrade pip
```

### 5.2 Instalar dependencias principales

```bash
# Instalar dependencias del proyecto principal
pip install -r requirements.txt

# Verificar instalación
pip list | grep -E "(python-telegram-bot|python-dotenv|google-generativeai|playwright)"
```

### 5.3 Instalar dependencias del backend

```bash
# Instalar dependencias del backend FastAPI
pip install -r admin_panel/backend/requirements.txt

# Verificar instalación
pip list | grep -E "(fastapi|uvicorn|supabase|playwright)"
```

### 5.4 Instalar navegadores de Playwright

```bash
# Instalar Chromium para Playwright
playwright install chromium

# Verificar instalación
playwright --version
```

**Verificación**:
```bash
python -c "import telegram; import fastapi; import playwright; print('✅ Todas las dependencias principales instaladas')"
```

---

## PASO 6: Instalar Dependencias de Node.js

### 6.1 Instalar dependencias en la raíz

```bash
# Asegurar que estamos en el directorio raíz del proyecto
cd ~/Escritorio/SkyFlow_Porn-master/100-trafico

# Instalar dependencias de Node.js (raíz)
npm install

# Verificar instalación
ls -la node_modules | head -5
```

### 6.2 Instalar dependencias del frontend

```bash
# Navegar al frontend
cd admin_panel/frontend

# Instalar dependencias
npm install

# Verificar instalación
ls -la node_modules | head -5

# Volver a la raíz
cd ../../..
```

**Verificación**:
```bash
cd admin_panel/frontend
npm list --depth=0 | grep -E "(next|react|typescript)"  # Debe mostrar paquetes instalados
cd ../../..
```

---

## PASO 7: Configurar Variables de Entorno

### 7.1 Crear archivo .env

```bash
# Navegar a src/
cd ~/Escritorio/SkyFlow_Porn-master/100-trafico/src

# Crear archivo .env
touch .env

# Verificar que se creó
ls -la .env
```

### 7.2 Configurar variables de entorno

**IMPORTANTE**: El agente debe solicitar al usuario las siguientes credenciales antes de continuar:

1. `SUPABASE_URL`
2. `SUPABASE_ANON_KEY`
3. `GEMINI_API_KEY`
4. `TELEGRAM_BOT_TOKEN` (opcional)
5. `TELEGRAM_CHAT_ID` (opcional)
6. `API_ID` (para Telegram Bot API local)
7. `API_HASH` (para Telegram Bot API local)

```bash
# Crear archivo .env con plantilla
cat > ~/Escritorio/SkyFlow_Porn-master/100-trafico/src/.env << 'EOF'
# === SUPABASE ===
SUPABASE_URL=REEMPLAZAR_CON_URL_REAL
SUPABASE_ANON_KEY=REEMPLAZAR_CON_ANON_KEY_REAL

# === GEMINI AI ===
GEMINI_API_KEY=REEMPLAZAR_CON_API_KEY_REAL

# === TELEGRAM (Opcional) ===
TELEGRAM_BOT_TOKEN=REEMPLAZAR_CON_TOKEN_REAL
TELEGRAM_CHAT_ID=REEMPLAZAR_CON_CHAT_ID_REAL

# === TELEGRAM BOT API LOCAL (Para archivos grandes) ===
API_ID=REEMPLAZAR_CON_API_ID_REAL
API_HASH=REEMPLAZAR_CON_API_HASH_REAL

# === CONFIGURACIÓN DEL SISTEMA ===
TZ=America/Bogota
DEBUG=False
EOF
```

**⚠️ ACCIÓN REQUERIDA**: El agente debe reemplazar todos los valores `REEMPLAZAR_CON_*` con los valores reales proporcionados por el usuario.

**Verificación**:
```bash
# Verificar que el archivo existe y tiene contenido
cat ~/Escritorio/SkyFlow_Porn-master/100-trafico/src/.env

# Verificar que no hay valores de placeholder
grep -i "REEMPLAZAR" ~/Escritorio/SkyFlow_Porn-master/100-trafico/src/.env
# Si encuentra "REEMPLAZAR", significa que faltan valores reales
```

---

## PASO 8: Configurar Supabase

### 8.1 Verificar conexión a Supabase

```bash
# Activar entorno virtual
cd ~/Escritorio/SkyFlow_Porn-master/100-trafico
source .venv/bin/activate

# Probar conexión (crear script temporal)
python3 << 'PYEOF'
import os
from dotenv import load_dotenv

load_dotenv('src/.env')
from supabase import create_client, Client

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")

if not url or not key:
    print("❌ ERROR: SUPABASE_URL o SUPABASE_ANON_KEY no configurados")
    exit(1)

try:
    supabase: Client = create_client(url, key)
    print("✅ Conexión a Supabase exitosa")
except Exception as e:
    print(f"❌ ERROR conectando a Supabase: {e}")
    exit(1)
PYEOF
```

### 8.2 Crear tabla de modelos en Supabase

**INSTRUCCIÓN PARA EL USUARIO**: El agente debe indicar al usuario que ejecute este SQL en la consola SQL de Supabase:

```sql
-- Crear tabla de modelos
CREATE TABLE IF NOT EXISTS modelos (
  modelo TEXT PRIMARY KEY,
  plataformas TEXT NOT NULL DEFAULT '',
  hora_inicio VARCHAR(5) NOT NULL DEFAULT '12:00',
  ventana_horas INTEGER NOT NULL DEFAULT 5,
  striphours_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Habilitar Row Level Security (opcional)
ALTER TABLE modelos ENABLE ROW LEVEL SECURITY;

-- Crear política para acceso público (desarrollo)
CREATE POLICY "Enable all access for all users" ON modelos
  FOR ALL USING (true);
```

**Verificación**: El usuario debe confirmar que la tabla se creó correctamente en Supabase.

---

## PASO 9: Configurar Servidor Local de Telegram Bot API

### 9.1 Verificar que Docker está funcionando

```bash
# Verificar Docker
docker ps

# Si requiere sudo, usar sudo
sudo docker ps
```

### 9.2 Iniciar servidor local de Telegram Bot API

```bash
# Navegar al directorio del proyecto
cd ~/Escritorio/SkyFlow_Porn-master/100-trafico

# Hacer el script ejecutable
chmod +x scripts/start_local_bot_api.sh

# Ejecutar script (puede requerir sudo)
sudo bash scripts/start_local_bot_api.sh
```

**Verificación**:
```bash
# Verificar que el contenedor está corriendo
docker ps | grep telegram-bot-api

# Verificar que el servidor responde
curl http://localhost:8081

# Debe mostrar respuesta del servidor (no error de conexión)
```

---

## PASO 10: Verificar Instalación Completa

### 10.1 Verificar estructura de directorios

```bash
cd ~/Escritorio/SkyFlow_Porn-master/100-trafico

# Verificar estructura
ls -la
ls -la docs/
ls -la scripts/
ls -la src/
ls -la admin_panel/backend/
ls -la admin_panel/frontend/
```

### 10.2 Verificar que todos los servicios pueden iniciar

#### 10.2.1 Probar Backend

```bash
# Activar entorno virtual
source .venv/bin/activate

# Iniciar backend en segundo plano (solo para prueba)
cd admin_panel/backend
python -m uvicorn main:app --port 8000 &
BACKEND_PID=$!

# Esperar 3 segundos
sleep 3

# Verificar que responde
curl http://localhost:8000/docs

# Detener backend de prueba
kill $BACKEND_PID
cd ../../..
```

**Resultado esperado**: Debe mostrar HTML de la documentación de FastAPI.

#### 10.2.2 Probar Frontend

```bash
# Navegar al frontend
cd admin_panel/frontend

# Verificar que puede compilar
npm run build

# Si hay errores, mostrarlos
cd ../../..
```

**Resultado esperado**: Build exitoso sin errores críticos.

---

## PASO 11: Crear Scripts de Inicio

### 11.1 Verificar que los scripts existen y son ejecutables

```bash
cd ~/Escritorio/SkyFlow_Porn-master/100-trafico

# Verificar scripts
ls -la scripts/

# Hacer ejecutables si no lo son
chmod +x scripts/*.sh
```

### 11.2 Probar scripts de inicio

```bash
# Probar script de backend (debe iniciar correctamente)
timeout 5 bash scripts/start_backend.sh || true

# Probar script de frontend (debe iniciar correctamente)
timeout 5 bash scripts/start_frontend.sh || true
```

---

## PASO 12: Verificación Final

### 12.1 Checklist de verificación

Ejecutar cada comando y verificar el resultado:

```bash
# 1. Python y entorno virtual
python3 --version
source .venv/bin/activate && python --version && deactivate

# 2. Node.js
node --version
npm --version

# 3. Docker
docker --version
docker ps

# 4. Dependencias Python
source .venv/bin/activate
python -c "import telegram; import fastapi; import playwright; import supabase; print('✅ Python OK')"
deactivate

# 5. Dependencias Node.js
cd admin_panel/frontend
npm list --depth=0 > /dev/null && echo "✅ Node.js OK"
cd ../../..

# 6. Archivo .env
test -f src/.env && echo "✅ .env existe" || echo "❌ .env NO existe"
grep -q "SUPABASE_URL" src/.env && echo "✅ .env configurado" || echo "❌ .env incompleto"

# 7. Servidor Telegram Bot API
curl -s http://localhost:8081 > /dev/null && echo "✅ Telegram Bot API local OK" || echo "⚠️  Telegram Bot API local no responde"

# 8. Estructura de directorios
test -d docs && echo "✅ docs/ existe" || echo "❌ docs/ NO existe"
test -d scripts && echo "✅ scripts/ existe" || echo "❌ scripts/ NO existe"
test -d src && echo "✅ src/ existe" || echo "❌ src/ NO existe"
test -d admin_panel/backend && echo "✅ admin_panel/backend/ existe" || echo "❌ admin_panel/backend/ NO existe"
test -d admin_panel/frontend && echo "✅ admin_panel/frontend/ existe" || echo "❌ admin_panel/frontend/ NO existe"
```

### 12.2 Resumen de instalación

```bash
echo "═══════════════════════════════════════════════════════════════"
echo "  RESUMEN DE INSTALACIÓN"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "✅ Python: $(python3 --version)"
echo "✅ Node.js: $(node --version)"
echo "✅ Docker: $(docker --version 2>/dev/null || echo 'No disponible')"
echo "✅ Directorio del proyecto: $(pwd)"
echo ""
echo "Para iniciar el sistema:"
echo "  1. Terminal 1: ./scripts/start_backend.sh"
echo "  2. Terminal 2: ./scripts/start_frontend.sh"
echo "  3. Abrir navegador: http://localhost:3000"
echo ""
echo "═══════════════════════════════════════════════════════════════"
```

---

## 🚀 Iniciar el Sistema

Una vez completada la instalación, el sistema se inicia con:

### Terminal 1: Backend
```bash
cd ~/Escritorio/SkyFlow_Porn-master/100-trafico
./scripts/start_backend.sh
```

### Terminal 2: Frontend
```bash
cd ~/Escritorio/SkyFlow_Porn-master/100-trafico
./scripts/start_frontend.sh
```

### Terminal 3: Bot de Telegram (opcional)
```bash
cd ~/Escritorio/SkyFlow_Porn-master/100-trafico
source .venv/bin/activate
python3 main.py
```

### Acceder al Panel
Abrir navegador en: **http://localhost:3000**

---

## 🔧 Solución de Problemas Comunes

### Problema: Docker requiere sudo

**Solución**:
```bash
sudo usermod -aG docker $USER
newgrp docker
# O cerrar sesión y volver a iniciar
```

### Problema: Puerto 8000 o 3000 ocupado

**Solución**:
```bash
# Ver qué está usando el puerto
lsof -i :8000
lsof -i :3000

# Matar el proceso
kill -9 [PID]
```

### Problema: Playwright no encuentra Chromium

**Solución**:
```bash
source .venv/bin/activate
playwright install chromium
```

### Problema: Backend no conecta a Supabase

**Solución**:
1. Verificar que `src/.env` tiene `SUPABASE_URL` y `SUPABASE_ANON_KEY` correctos
2. Verificar que la tabla `modelos` existe en Supabase
3. Verificar conexión a internet

### Problema: Frontend no compila

**Solución**:
```bash
cd admin_panel/frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

## ✅ Checklist Final

Antes de considerar la instalación completa, verificar:

- [ ] Python 3.10+ instalado y funcionando
- [ ] Node.js 18+ instalado y funcionando
- [ ] Docker instalado y funcionando
- [ ] Repositorio clonado correctamente
- [ ] Entorno virtual creado y activado
- [ ] Todas las dependencias Python instaladas
- [ ] Todas las dependencias Node.js instaladas
- [ ] Playwright Chromium instalado
- [ ] Archivo `.env` creado y configurado con valores reales
- [ ] Tabla `modelos` creada en Supabase
- [ ] Servidor local de Telegram Bot API corriendo
- [ ] Backend puede iniciar sin errores
- [ ] Frontend puede compilar sin errores
- [ ] Scripts de inicio son ejecutables

---

## 📝 Notas Importantes

1. **Credenciales**: Nunca subir el archivo `.env` al repositorio. Está en `.gitignore`.

2. **Docker**: El servidor local de Telegram Bot API debe estar corriendo para manejar archivos grandes (hasta 2GB).

3. **Supabase**: La tabla `modelos` debe crearse manualmente en la consola SQL de Supabase.

4. **Permisos**: Si Docker requiere sudo constantemente, agregar el usuario al grupo docker y reiniciar sesión.

5. **Puertos**: Asegurar que los puertos 3000 (frontend), 8000 (backend) y 8081 (Telegram Bot API local) estén libres.

---

**¡Instalación Completa!** 🎉

El sistema está listo para usar. Consulta `docs/INICIO_RAPIDO.md` para comenzar a usar el sistema.

