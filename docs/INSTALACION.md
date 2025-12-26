# 📦 Manual de Instalación - 100 Tráfico

Sistema de gestión automatizada de contenido para adultos con IA y automatización web.

---

## 📋 Tabla de Contenidos

- [Requisitos Previos](#requisitos-previos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Ejecución](#ejecución)
- [Uso del Sistema](#uso-del-sistema)
- [Solución de Problemas](#solución-de-problemas)

---

## 🔧 Requisitos Previos

### Software Necesario

1. **Python 3.10 o superior**
   ```bash
   python3 --version
   # Debe mostrar Python 3.10.x o superior
   ```

2. **Node.js 18 o superior**
   ```bash
   node --version
   # Debe mostrar v18.x.x o superior
   ```

3. **npm (viene con Node.js)**
   ```bash
   npm --version
   ```

4. **Git**
   ```bash
   git --version
   ```

### Cuentas y Credenciales Necesarias

1. **Supabase** (Base de datos)
   - Crear cuenta en [https://supabase.com](https://supabase.com)
   - Crear un nuevo proyecto
   - Obtener:
     - URL del proyecto
     - Clave anónima (anon key)

2. **Google Gemini API** (Inteligencia Artificial)
   - Crear cuenta en [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
   - Generar API Key

3. **Telegram Bot** (Opcional, para notificaciones)
   - Hablar con [@BotFather](https://t.me/BotFather) en Telegram
   - Crear un nuevo bot con `/newbot`
   - Obtener el token del bot

---

## 📥 Instalación

### 1. Clonar el Repositorio

```bash
cd ~/Escritorio
git clone [URL_DEL_REPOSITORIO] SkyFlow_Porn-master
cd SkyFlow_Porn-master/100-trafico
```

### 2. Configurar Entorno Virtual de Python

```bash
# Crear entorno virtual
python3 -m venv .venv

# Activar entorno virtual
source .venv/bin/activate

# Deberías ver (.venv) al inicio de tu terminal
```

### 3. Instalar Dependencias de Python

```bash
# Instalar dependencias principales
pip install --upgrade pip
pip install -r requirements.txt

# Instalar dependencias del backend
pip install -r admin_panel/backend/requirements.txt

# Instalar navegadores de Playwright
playwright install chromium
```

### 4. Instalar Dependencias de Node.js

```bash
# Instalar Playwright (raíz del proyecto)
npm install

# Instalar dependencias del frontend
cd admin_panel/frontend
npm install
cd ../..
```

---

## ⚙️ Configuración

### 1. Crear Archivo de Configuración

Crea el archivo `.env` en la carpeta `src/`:

```bash
touch src/.env
```

### 2. Configurar Variables de Entorno

Edita `src/.env` con tus credenciales:

```bash
# === SUPABASE ===
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=tu_clave_anonima_aqui

# === GEMINI AI ===
GEMINI_API_KEY=tu_api_key_de_gemini_aqui

# === TELEGRAM (Opcional) ===
TELEGRAM_BOT_TOKEN=tu_token_del_bot_aqui
TELEGRAM_CHAT_ID=tu_chat_id_aqui

# === CONFIGURACIÓN DEL SISTEMA ===
# Zona horaria
TZ=America/Bogota

# Modo debug (True/False)
DEBUG=False
```

### 3. Configurar Supabase

#### Crear Tabla de Modelos

En la consola SQL de Supabase, ejecuta:

```sql
-- Crear tabla de modelos
CREATE TABLE IF NOT EXISTS modelos (
  modelo TEXT PRIMARY KEY,
  plataformas TEXT NOT NULL DEFAULT '',
  hora_inicio VARCHAR(5) NOT NULL DEFAULT '12:00',
  ventana_horas INTEGER NOT NULL DEFAULT 5,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Habilitar Row Level Security (opcional)
ALTER TABLE modelos ENABLE ROW LEVEL SECURITY;

-- Crear política para acceso público (desarrollo)
CREATE POLICY "Enable all access for all users" ON modelos
  FOR ALL USING (true);
```

### 4. Verificar Estructura de Carpetas

El proyecto debe tener esta estructura:

```
100-trafico/
├── .venv/                    # Entorno virtual Python
├── node_modules/             # Dependencias Node.js
├── docs/                     # 📚 Documentación
├── scripts/                  # 🔧 Scripts de inicio
├── tests/                    # ✅ Pruebas
├── admin_panel/              
│   ├── backend/              # API FastAPI
│   └── frontend/             # Panel Next.js
├── src/                      # Código fuente principal
│   ├── .env                  # ⚠️ Configuración (CREAR)
│   ├── database/             # Cliente Supabase
│   └── project/              # Lógica del bot
├── modelos/                  # Perfiles de modelos (se crea automático)
├── workers/                  # Workers generados (se crea automático)
├── logs/                     # Logs del sistema
└── captures/                 # Capturas de red
```

---

## 🚀 Ejecución

### Opción 1: Ejecución Manual (Desarrollo)

#### Terminal 1: Backend

```bash
cd ~/Escritorio/SkyFlow_Porn-master/100-trafico/admin_panel/backend
source ../../.venv/bin/activate
python -m uvicorn main:app --reload --port 8000
```

Deberías ver:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
✅ .env cargado desde: /home/victor/Escritorio/SkyFlow_Porn-master/100-trafico/src/.env
```

#### Terminal 2: Frontend

```bash
cd ~/Escritorio/SkyFlow_Porn-master/100-trafico/admin_panel/frontend
npm run dev
```

Deberías ver:
```
  ▲ Next.js 14.0.4
  - Local:        http://localhost:3000
  ✓ Ready in 2.3s
```

### Opción 2: Ejecución con Scripts (Recomendado)

Los scripts ya están disponibles en la carpeta `scripts/`:

**`scripts/start_backend.sh`:**
```bash
#!/bin/bash
cd "$(dirname "$0")/../admin_panel/backend"
source ../../.venv/bin/activate
python -m uvicorn main:app --reload --port 8000
```

**`scripts/start_frontend.sh`:**
```bash
#!/bin/bash
cd "$(dirname "$0")/../admin_panel/frontend"
npm run dev
```

Ejecutar:
```bash
# Terminal 1
./scripts/start_backend.sh

# Terminal 2
./scripts/start_frontend.sh
```

---

## 🎯 Uso del Sistema

### 1. Acceder al Panel de Administración

Abre tu navegador en: **http://localhost:3000**

### 2. Crear una Modelo

1. En la sección **"Modelos"**, haz clic en **"+ Crear Modelo"**
2. Completa el formulario:
   - **Nombre**: Nombre único de la modelo (ej: "maria")
   - **Foto de perfil**: Sube una imagen (se recorta automático a 1:1)
   - **Telegram username**: Usuario de Telegram (con @)
   - **Hora de inicio**: Hora para iniciar publicaciones (ej: 12:00)
   - **Ventana de horas**: Duración de la ventana de publicación (ej: 5 horas)
   - **Características físicas**: Completa los campos descriptivos
3. Haz clic en **"Crear Modelo"**

### 3. Abrir Navegador y Guardar Sesiones

1. En la tarjeta de la modelo, haz clic en **"🌐 Abrir Navegador"**
2. Se abrirá un navegador Chromium con perfil persistente
3. **Inicia sesión** en las plataformas que necesites (OnlyFans, Fansly, etc.)
4. Navega y verifica que las sesiones funcionan
5. **Cierra el navegador** cuando termines
6. ✅ Todas las sesiones se guardan automáticamente en `modelos/[nombre]/browser_profile/`

### 4. Verificar Sesiones Guardadas

La próxima vez que abras el navegador:
- Estarás **automáticamente logueado** en todas las plataformas
- No necesitas volver a introducir credenciales
- Todas las cookies, localStorage y sessionStorage persisten

### 5. Editar una Modelo

1. Haz clic en **"✏️ Editar"** en la tarjeta de la modelo
2. Modifica los campos que necesites
3. Haz clic en **"Guardar Cambios"**

### 6. Eliminar una Modelo

1. Haz clic en **"🗑️ Eliminar"** en la tarjeta de la modelo
2. Confirma la acción
3. Se eliminarán:
   - El registro en Supabase
   - La carpeta local con el perfil del navegador
   - La foto de perfil

---

## 🔧 Solución de Problemas

### Problema: Backend no responde

**Síntoma**: Frontend muestra "Network Error" o se queda cargando

**Solución**:
```bash
# 1. Verificar si el backend está corriendo
ps aux | grep uvicorn

# 2. Verificar puerto
lsof -i :8000

# 3. Matar procesos colgados
pkill -f "uvicorn main:app"

# 4. Reiniciar backend
cd admin_panel/backend
source ../../.venv/bin/activate
python -m uvicorn main:app --reload --port 8000
```

### Problema: No carga las modelos

**Síntoma**: Sección "Modelos" se queda en "Cargando..."

**Solución**:
1. Verificar que Supabase esté configurado correctamente en `src/.env`
2. Verificar que la tabla `modelos` existe en Supabase
3. Revisar logs del backend para errores de conexión
4. Refrescar el navegador (F5)

### Problema: Error al crear modelo

**Síntoma**: "Error creando modelo" después de completar el formulario

**Soluciones**:
1. **Timeout**: Aumenta el timeout si tienes conexión lenta
2. **Permisos**: Verifica permisos en la carpeta `modelos/`
   ```bash
   ls -la modelos/
   chmod 755 modelos/
   ```
3. **Foto muy grande**: Usa una imagen más pequeña (< 5MB)

### Problema: Navegador no guarda sesiones

**Síntoma**: Al reabrir el navegador, no estás logueado

**Causa**: El navegador usa `launch_persistent_context` que guarda TODO automáticamente

**Verificar**:
```bash
# Debe tener archivos de Chromium
ls -la modelos/[nombre_modelo]/browser_profile/

# Deberías ver:
# - Default/
# - first_party_sets.db
# - Local State
```

**Solución**: Las sesiones SÍ se guardan. Si no funcionan, puede ser que:
- La plataforma requiere 2FA
- La sesión expiró (algunas plataformas expiran sesiones)

### Problema: Playwright no instalado

**Síntoma**: `playwright._impl._driver.DriverException: Executable doesn't exist`

**Solución**:
```bash
source .venv/bin/activate
playwright install chromium
```

### Problema: Puerto 8000 o 3000 ocupado

**Síntoma**: `Address already in use`

**Solución**:
```bash
# Ver qué está usando el puerto
lsof -i :8000
lsof -i :3000

# Matar el proceso
kill -9 [PID]
```

### Logs útiles

**Backend**:
```bash
tail -f /tmp/backend_fresh.log
```

**Frontend (consola del navegador)**:
- Abre DevTools (F12)
- Ve a la pestaña "Console"
- Busca errores en rojo

---

## 📚 Recursos Adicionales

### Documentación

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)
- [Playwright Docs](https://playwright.dev/python/)
- [Supabase Docs](https://supabase.com/docs)
- [Gemini API Docs](https://ai.google.dev/docs)

### Estructura de Archivos Importantes

- `admin_panel/backend/main.py` - Punto de entrada del backend
- `admin_panel/backend/api/` - Routers de la API
- `admin_panel/frontend/src/app/page.tsx` - Página principal del frontend
- `src/database/supabase_client.py` - Cliente de Supabase
- `modelos/` - Perfiles de navegador de las modelos

### Comandos Útiles

```bash
# Activar entorno virtual
source .venv/bin/activate

# Ver logs en tiempo real
tail -f logs/*.log

# Limpiar cache de Python
find . -type d -name __pycache__ -exec rm -r {} +

# Verificar conexión a Supabase
curl http://localhost:8000/api/models/test-supabase
```

---

## 🆘 Soporte

Si encuentras problemas no cubiertos en esta guía:

1. Revisa los logs del backend y frontend
2. Verifica que todas las dependencias estén instaladas
3. Asegúrate de que las variables de entorno estén correctas
4. Verifica que Supabase esté accesible

---

## ✅ Checklist de Instalación

- [ ] Python 3.10+ instalado
- [ ] Node.js 18+ instalado
- [ ] Repositorio clonado
- [ ] Entorno virtual creado y activado
- [ ] Dependencias Python instaladas
- [ ] Dependencias Node.js instaladas
- [ ] Playwright navegadores instalados
- [ ] Archivo `.env` creado en `src/`
- [ ] Variables de entorno configuradas
- [ ] Tabla `modelos` creada en Supabase
- [ ] Backend corriendo en http://localhost:8000
- [ ] Frontend corriendo en http://localhost:3000
- [ ] Primera modelo creada exitosamente
- [ ] Navegador abre y guarda sesiones

---

**¡Listo!** Tu sistema 100 Tráfico está instalado y funcionando. 🎉





