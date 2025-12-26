# 📋 Documento Técnico - 100 Tráfico

**Versión:** 1.0.0  
**Fecha:** Noviembre 2025  
**Propósito:** Documentación técnica completa para auditoría del proyecto

---

## 📑 Índice

1. [Visión General](#visión-general)
2. [Estructura del Proyecto](#estructura-del-proyecto)
3. [Arquitectura del Sistema](#arquitectura-del-sistema)
4. [Módulos Principales](#módulos-principales)
5. [Flujos Clave del Sistema](#flujos-clave-del-sistema)
6. [Integraciones con APIs Externas](#integraciones-con-apis-externas)
7. [Dependencias](#dependencias)
8. [Decisiones Arquitectónicas](#decisiones-arquitectónicas)
9. [Problemas Potenciales y Code Smells](#problemas-potenciales-y-code-smells)
10. [Recomendaciones](#recomendaciones)

---

## 🎯 Visión General

**100 Tráfico** es un sistema de gestión automatizada de contenido para adultos que integra:

- **Bot de Telegram** para recepción de videos
- **Panel de administración web** (Next.js + FastAPI)
- **Automatización con Playwright** para publicación en múltiples plataformas
- **Inteligencia Artificial (Gemini)** para generación de captions y tags
- **Base de datos en la nube (Supabase)** para persistencia
- **Sistema de métricas (KPIs)** desde Striphours/CBHours
- **Navegadores persistentes** con sesiones guardadas por modelo

### Stack Tecnológico Principal

- **Backend:** Python 3.10+, FastAPI, python-telegram-bot
- **Frontend:** Next.js 14, TypeScript, Tailwind CSS, React Query
- **Automatización:** Playwright (Node.js)
- **Base de Datos:** Supabase (PostgreSQL)
- **IA:** Google Gemini API
- **Métricas:** CBHours API (Striphours)

---

## 📁 Estructura del Proyecto

```
100-trafico/
├── admin_panel/                    # Panel de administración web
│   ├── backend/                    # API FastAPI
│   │   ├── api/                    # Routers de la API
│   │   │   ├── auth_router.py      # Autenticación de plataformas
│   │   │   ├── capture_router.py   # Captura de network flows
│   │   │   ├── kpi_router.py       # Endpoints de métricas/KPIs
│   │   │   ├── models_router.py    # CRUD de modelos
│   │   │   ├── navegador_router.py # Gestión de navegadores
│   │   │   ├── platforms_router.py # Gestión de plataformas
│   │   │   └── workers_router.py   # Gestión de workers
│   │   ├── main.py                 # Punto de entrada FastAPI
│   │   └── requirements.txt        # Dependencias Python del backend
│   └── frontend/                   # Aplicación Next.js
│       ├── src/
│       │   ├── app/                # Páginas Next.js (App Router)
│       │   ├── features/           # Componentes por funcionalidad
│       │   │   ├── auth/           # Autenticación
│       │   │   ├── kpi/            # Dashboard de métricas
│       │   │   ├── models/         # Gestión de modelos
│       │   │   ├── platforms/      # Gestión de plataformas
│       │   │   └── workers/        # Gestión de workers
│       │   └── shared/             # Componentes compartidos
│       └── package.json            # Dependencias Node.js del frontend
│
├── src/                            # Lógica principal del sistema
│   ├── database/                   # Cliente Supabase
│   │   ├── supabase_client.py      # Cliente y funciones CRUD
│   │   └── create_model_table.js   # Script para crear tablas dinámicas
│   ├── project/                    # Módulos del bot de Telegram
│   │   ├── bot_central.py          # Bot principal de Telegram
│   │   ├── caption.py              # Generación de captions con Gemini
│   │   ├── kpi_scheduler.py        # Scheduler de métricas Striphours
│   │   ├── poster.py                # Scheduler de publicación
│   │   └── scheduler.py            # Planificación de slots de publicación
│   └── tags_disponibles.json       # Catálogo de tags para IA
│
├── modelos/                         # Perfiles de modelos
│   └── [nombre_modelo]/
│       ├── config.json              # Configuración del modelo
│       ├── profile_photo.jpg         # Foto de perfil (512x512)
│       ├── metrics.json              # Métricas sincronizadas (Striphours)
│       ├── browser_profile/          # Perfil de navegador persistente
│       └── [videos].mp4              # Videos subidos por el modelo
│
├── workers/                         # Workers de Playwright generados
│   ├── kams.js                      # Worker para Kams.com
│   ├── xxxfollow.js                 # Worker para XXXFollow
│   ├── fikfap.js                    # Worker para FikFap
│   └── [plataforma].js              # Workers generados automáticamente
│
├── kpi_stripchat/                   # Módulo de métricas Striphours
│   ├── api_wrapper.py               # Wrapper de CBHours API
│   └── enhanced_dashboard.html       # Dashboard HTML (legacy)
│
├── captures/                        # Capturas de network flows
│   └── [plataforma]_[timestamp].json
│
├── logs/                            # Logs del sistema
│
├── scripts/                         # Scripts de instalación/inicio
│   ├── start_backend.sh             # Inicia backend FastAPI
│   ├── start_frontend.sh            # Inicia frontend Next.js
│   └── start_local_bot_api.sh       # Inicia servidor local de Telegram Bot API
│
├── tests/                           # Tests (parcialmente implementado)
│   ├── test_credentials.py
│   ├── test_imports.py
│   └── playwright.config.js
│
├── docs/                            # Documentación
│
├── main.py                          # Launcher principal (inicia todos los servicios)
├── package.json                     # Dependencias Node.js (Playwright)
├── requirements.txt                 # Dependencias Python principales
└── README.md                        # Documentación principal
```

---

## 🏗️ Arquitectura del Sistema

### Componentes Principales

```
┌─────────────────────────────────────────────────────────────┐
│                    TELEGRAM BOT (bot_central.py)            │
│  - Recibe videos de modelos                                 │
│  - Procesa metadata (qué vendes, outfit)                     │
│  - Genera captions y tags con Gemini                        │
│  - Programa slots de publicación                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              SUPABASE (Base de Datos)                       │
│  - Tabla 'modelos': Configuración de modelos               │
│  - Tabla '[modelo]': Schedules de publicación por modelo    │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
┌──────────────────┐        ┌──────────────────┐
│ POSTER SCHEDULER │        │  KPI SCHEDULER   │
│   (poster.py)    │        │ (kpi_scheduler)  │
│                  │        │                  │
│ - Verifica posts │        │ - Sincroniza     │
│   pendientes     │        │   métricas desde │
│ - Ejecuta workers │        │   Striphours API │
│   Playwright      │        │ - Guarda en     │
│ - Actualiza      │        │   metrics.json   │
│   estado         │        │                  │
└──────────────────┘        └──────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│              WORKERS (Playwright)                           │
│  - kams.js, xxxfollow.js, fikfap.js, etc.                  │
│  - Usan browser_profile/ para sesiones persistentes        │
│  - Publican videos en plataformas                          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│         ADMIN PANEL (Next.js + FastAPI)                    │
│  - CRUD de modelos                                          │
│  - Gestión de plataformas                                   │
│  - Captura de network flows                                 │
│  - Visualización de métricas                                │
│  - Generación automática de workers con Gemini              │
└─────────────────────────────────────────────────────────────┘
```

### Flujo de Datos Principal

1. **Recepción de Video:**
   - Modelo envía video por Telegram → `bot_central.py`
   - Video se guarda en `modelos/[modelo]/[timestamp]_[random].mp4`
   - Metadata se guarda en `modelos/[modelo]/[video].json`

2. **Procesamiento:**
   - `caption.py` genera caption con Gemini
   - `caption.py` genera tags inteligentes desde `tags_disponibles.json`
   - `scheduler.py` planifica slots de publicación
   - Se insertan schedules en Supabase (tabla `[modelo]`)

3. **Publicación:**
   - `poster.py` verifica posts pendientes cada 60 segundos
   - Ejecuta worker Playwright correspondiente
   - Worker usa `browser_profile/` para sesión persistente
   - Actualiza estado en Supabase

4. **Métricas:**
   - `kpi_scheduler.py` sincroniza métricas desde Striphours API
   - Guarda en `modelos/[modelo]/metrics.json`
   - Panel admin visualiza métricas

---

## 🔧 Módulos Principales

### 1. Bot Central (`src/project/bot_central.py`)

**Propósito:** Bot de Telegram que recibe videos de modelos y coordina el procesamiento.

**Funcionalidades:**
- Mapeo de `telegram_user_id` → nombre de modelo
- Recepción de videos (hasta 4GB con servidor local)
- Interfaz interactiva con botones para seleccionar "qué vendes" y "outfit"
- Integración con `caption.py` y `scheduler.py`
- Actualización de schedules en Supabase

**Puntos Clave:**
- Usa servidor local de Telegram Bot API (`http://127.0.0.1:8081`) para archivos grandes
- Carga mapeo de modelos desde `config.json` de cada modelo
- Comando `/reload` para recargar mapeo sin reiniciar

**Dependencias:**
- `python-telegram-bot>=20.8`
- `scheduler.py`, `caption.py`

---

### 2. Generación de Captions (`src/project/caption.py`)

**Propósito:** Genera captions y tags usando Google Gemini y lógica inteligente.

**Funcionalidades:**
- Generación de captions con Gemini (`gemini-2.5-flash`)
- Selección inteligente de tags desde `tags_disponibles.json`
- Mapeo de características del modelo a tags relevantes
- Persistencia en JSON local y Supabase

**Lógica de Tags:**
- Basada en `que_vendes` (body_focus): tetas, culo, pies, cara, vagina, cuerpo completo
- Basada en `outfit`: lencería, tanga, topless, tacones, etc.
- Basada en `metadata` del modelo: tipo de cuerpo, color de cabello, tatuajes, etc.
- Política de máximo 6 tags

**Dependencias:**
- `google-generativeai>=0.3.0`
- `tags_disponibles.json`
- `supabase_client.py`

---

### 3. Scheduler de Publicación (`src/project/scheduler.py`)

**Propósito:** Planifica slots de publicación respetando reglas de negocio.

**Reglas:**
- Máximo 6 apariciones del mismo video
- Máximo 3 videos distintos por día
- Ventana de publicación: `hora_inicio` + `ventana_horas`
- Mínimo 10 minutos entre publicaciones (configurable)
- Búsqueda hasta 30 días adelante (configurable)

**Algoritmo:**
1. Obtiene configuración del modelo desde Supabase
2. Obtiene todos los schedules existentes
3. Busca día disponible con capacidad
4. Genera slots dentro de la ventana respetando gaps mínimos
5. Retorna lista `[(plataforma, scheduled_time)]`

**Dependencias:**
- `supabase_client.py`

---

### 4. Poster Scheduler (`src/project/poster.py`)

**Propósito:** Ejecuta workers de Playwright para publicar posts pendientes.

**Funcionalidades:**
- Consulta posts pendientes cada 60 segundos
- Filtra por `estado='pendiente'` y `scheduled_time <= ahora`
- Ejecuta worker Playwright correspondiente
- Actualiza estado: `pendiente` → `procesando` → `publicado`/`fallido`

**Ejecución de Workers:**
```bash
npx playwright test workers/[plataforma].js
```
Con variables de entorno:
- `VIDEO_PATH`: Ruta absoluta del video
- `VIDEO_TITLE`: Caption
- `VIDEO_TAGS`: Tags separados por comas
- `MODEL_NAME`: Nombre del modelo (para aislar sesión)

**Dependencias:**
- `supabase`
- Playwright (Node.js)

---

### 5. KPI Scheduler (`src/project/kpi_scheduler.py`)

**Propósito:** Sincroniza métricas desde Striphours/CBHours API.

**Funcionalidades:**
- Primera vez: descarga últimos 30 días
- Actualizaciones: sincroniza días faltantes desde `last_sync`
- Actualiza día actual cada 10 minutos
- Guarda en `modelos/[modelo]/metrics.json`

**Métricas Calculadas:**
- `best_rank`, `avg_rank`: Ranking global
- `best_gender_rank`, `avg_gender_rank`: Ranking por género
- `most_viewers`, `avg_viewers`: Espectadores
- `starting_followers`, `ending_followers`, `growth`: Crecimiento
- `total_segments`: Segmentos de 3 minutos

**Zona Horaria:**
- Todas las operaciones usan UTC para coincidir con la API
- Evita desfases entre hora local (Colombia UTC-5) y UTC

**Dependencias:**
- `kpi_stripchat/api_wrapper.py`
- `supabase_client.py`

---

### 6. Cliente Supabase (`src/database/supabase_client.py`)

**Propósito:** Cliente centralizado para operaciones con Supabase.

**Funcionalidades:**
- Conexión a Supabase
- CRUD de configuración de modelos (tabla `modelos`)
- CRUD de schedules (tabla `[modelo]`)
- Creación dinámica de tablas para nuevos modelos
- Verificación de existencia de tablas

**Estructura de Tablas:**

**Tabla `modelos`:**
```sql
- modelo (text, PK)
- plataformas (text) -- separadas por comas
- hora_inicio (text) -- formato "HH:MM"
- ventana_horas (int)
- striphours_url (text, nullable)
- striphours_username (text, nullable)
```

**Tabla `[modelo]` (dinámica por modelo):**
```sql
- id (serial, PK)
- video (text)
- caption (text)
- tags (text) -- separados por comas
- plataforma (text)
- estado (text) -- pendiente, procesando, publicado, fallido
- scheduled_time (timestamp)
```

**Creación de Tablas:**
- Se ejecuta `create_model_table.js` vía subprocess
- Requiere `SUPABASE_ACCESS_TOKEN` y `SUPABASE_PROJECT_REF`

---

### 7. Panel de Administración - Backend (`admin_panel/backend/`)

**Propósito:** API REST para gestión desde el frontend.

**Routers:**

- **`models_router.py`**: CRUD de modelos
  - `GET /api/models`: Lista todos los modelos
  - `POST /api/models`: Crea modelo nuevo
  - `PUT /api/models/{nombre}/editar`: Actualiza modelo
  - `DELETE /api/models/{nombre}`: Elimina modelo
  - `GET /api/models/{nombre}/profile-photo`: Obtiene foto de perfil

- **`capture_router.py`**: Captura de network flows
  - `POST /api/plataforma/capturar`: Inicia captura
  - `POST /api/plataforma/finalizar-captura`: Finaliza y genera worker
  - `POST /api/capture/start`: Inicia captura con Playwright
  - `GET /api/capture/status/{session_id}`: Estado de captura
  - `POST /api/capture/stop/{session_id}`: Detiene captura

- **`kpi_router.py`**: Métricas/KPIs
  - `GET /api/kpi/{modelo}`: Obtiene métricas desde JSON local
  - `POST /api/kpi/{modelo}/sync`: Sincroniza desde Striphours API

- **`auth_router.py`**: Autenticación en plataformas
- **`navegador_router.py`**: Gestión de navegadores persistentes
- **`platforms_router.py`**: Gestión de plataformas
- **`workers_router.py`**: Gestión de workers

**Configuración:**
- CORS habilitado para `localhost:3000-3006`
- Carga `.env` desde `src/.env`

---

### 8. Panel de Administración - Frontend (`admin_panel/frontend/`)

**Propósito:** Interfaz web para gestión del sistema.

**Stack:**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- React Query (gestión de estado del servidor)
- Axios (cliente HTTP)

**Estructura:**
- `app/`: Páginas (App Router)
  - `page.tsx`: Dashboard principal
  - `models/`: Gestión de modelos
  - `platforms/`: Gestión de plataformas
  - `workers/`: Gestión de workers
  - `models/[modelo]/metrics/`: Dashboard de métricas por modelo

- `features/`: Componentes por funcionalidad
  - Cada feature tiene: `components/`, `hooks/`, `services/`

- `shared/`: Componentes compartidos
  - `Button.tsx`, `Input.tsx`, `Modal.tsx`, `LoadingSpinner.tsx`, etc.

---

### 9. Workers de Playwright (`workers/`)

**Propósito:** Scripts de automatización para publicar en plataformas.

**Estructura Típica:**
```javascript
const { test } = require('@playwright/test');
const path = require('path');

const MODEL_NAME = process.env.MODEL_NAME;
const VIDEO_PATH = process.env.VIDEO_PATH;
const VIDEO_TITLE = process.env.VIDEO_TITLE;
const VIDEO_TAGS = process.env.VIDEO_TAGS;

// Ruta de autenticación
const authFile = path.join(__dirname, `../modelos/${MODEL_NAME}/.auth/[plataforma].json`);

test('Subida a [plataforma]', async ({ browser }) => {
  const context = await browser.newContext({ storageState: authFile });
  const page = await context.newPage();
  
  // Lógica de publicación...
});
```

**Características:**
- Usan `storageState` para sesiones persistentes
- Inyectan archivos vía input oculto
- Ejecutan lógica dentro del navegador (page.evaluate)
- Manejan autenticación desde localStorage/cookies

**Workers Existentes:**
- `kams.js`: Kams.com
- `xxxfollow.js`: XXXFollow
- `fikfap.js`: FikFap
- Generados automáticamente: `[plataforma].js`

---

### 10. API Wrapper de Striphours (`kpi_stripchat/api_wrapper.py`)

**Propósito:** Wrapper para la API de CBHours (Striphours).

**Funcionalidades:**
- Rate limiting automático (1.1s entre requests)
- Manejo de errores robusto
- Cálculo de métricas diarias
- Soporte para múltiples dominios (striphours, cbhours, sodahours)

**Clases:**
- `CBHoursAPI`: Cliente principal
- `APIError`: Excepción base
- `ModelNotInDatabaseError`: Modelo no encontrado

**Métodos Principales:**
- `get_activity()`: Obtiene datos de actividad
- `calculate_daily_metrics()`: Calcula métricas diarias
- `get_live_stats()`: Estadísticas en vivo (solo cbhours)

---

## 🔄 Flujos Clave del Sistema

### Flujo 1: Recepción y Procesamiento de Video

```
1. Modelo envía video por Telegram
   ↓
2. bot_central.py recibe video
   - Guarda en modelos/[modelo]/[timestamp]_[random].mp4
   - Muestra botones para "qué vendes" y "outfit"
   ↓
3. Usuario selecciona opciones
   - Guarda metadata en modelos/[modelo]/[video].json
   ↓
4. caption.py genera contenido
   - Llama a Gemini para caption
   - Genera tags inteligentes
   - Actualiza JSON local
   ↓
5. scheduler.py planifica slots
   - Busca días disponibles
   - Genera slots respetando reglas
   - Retorna [(plataforma, scheduled_time)]
   ↓
6. Se insertan schedules en Supabase
   - Una fila por plataforma
   - estado='pendiente'
   - scheduled_time asignado
```

### Flujo 2: Publicación Automática

```
1. poster.py verifica cada 60 segundos
   - Consulta posts con estado='pendiente'
   - Filtra por scheduled_time <= ahora
   ↓
2. Para cada post pendiente:
   - Actualiza estado='procesando'
   - Prepara variables de entorno
   ↓
3. Ejecuta worker Playwright
   npx playwright test workers/[plataforma].js
   ↓
4. Worker:
   - Carga sesión desde browser_profile/
   - Navega a plataforma
   - Sube video
   - Envía metadata (caption, tags)
   ↓
5. Actualiza estado en Supabase
   - 'publicado' si exitoso
   - 'fallido' si error
```

### Flujo 3: Captura y Generación de Worker

```
1. Usuario inicia captura desde panel admin
   POST /api/capture/start
   ↓
2. capture_router.py inicia Playwright
   - Abre navegador con DevTools
   - Registra TODOS los network events
   ↓
3. Usuario realiza flujo manual
   - Login
   - Sube video de prueba
   - Completa metadata
   ↓
4. Usuario finaliza captura
   POST /api/capture/stop/{session_id}
   ↓
5. Se analiza network flow
   - Identifica endpoints de login, upload, metadata
   - Extrae tokens de autenticación
   ↓
6. Se genera worker con Gemini
   - Usa workers de referencia (kams.js, xxxfollow.js)
   - Analiza network logs
   - Genera código JavaScript
   ↓
7. Se guarda worker en workers/[plataforma].js
```

### Flujo 4: Sincronización de Métricas

```
1. kpi_scheduler.py verifica cada minuto
   - Actualiza día actual cada 10 minutos
   - Verifica modelos nuevas cada hora
   ↓
2. Para modelo nueva (sin metrics.json):
   - Descarga últimos 30 días desde Striphours API
   - Calcula métricas diarias
   - Guarda en modelos/[modelo]/metrics.json
   ↓
3. Para modelo existente:
   - Sincroniza días faltantes desde last_sync hasta hoy
   - Solo agrega datos (no borra)
   - Actualiza last_sync
   ↓
4. Panel admin lee desde JSON local
   GET /api/kpi/{modelo}
   - Filtra por rango de fechas
   - Retorna métricas diarias
```

---

## 🔌 Integraciones con APIs Externas

### 1. Telegram Bot API

**Uso:**
- Bot de Telegram para recepción de videos
- Servidor local en `http://127.0.0.1:8081` para archivos >50MB

**Configuración:**
- `TELEGRAM_TOKEN`: Token del bot
- `ADMIN_ID`: ID del administrador

**Endpoints Usados:**
- `getFile`: Obtener archivo
- `sendMessage`: Enviar mensajes
- `answerCallbackQuery`: Responder botones

**Librería:**
- `python-telegram-bot>=20.8`

---

### 2. Google Gemini API

**Uso:**
- Generación de captions para videos
- Generación automática de workers desde network logs

**Modelos:**
- `gemini-2.5-flash`: Captions
- `gemini-2.0-flash-exp`: Generación de workers

**Configuración:**
- `GEMINI_API_KEY`: API key de Gemini

**Rate Limiting:**
- Retry con backoff exponencial
- Máximo 3 intentos

**Librería:**
- `google-generativeai>=0.3.0`

---

### 3. Supabase

**Uso:**
- Base de datos PostgreSQL en la nube
- Almacenamiento de configuración de modelos
- Almacenamiento de schedules de publicación

**Estructura:**
- Tabla `modelos`: Configuración global
- Tabla `[modelo]`: Schedules por modelo (dinámica)

**Configuración:**
- `SUPABASE_URL`: URL del proyecto
- `SUPABASE_ANON_KEY`: Clave anónima
- `SUPABASE_ACCESS_TOKEN`: Token de acceso (para crear tablas)

**Librería:**
- `supabase==2.0.0`

**Operaciones:**
- CRUD vía cliente Python
- Creación de tablas dinámicas vía script Node.js

---

### 4. CBHours/Striphours API

**Uso:**
- Obtención de métricas de modelos (ranking, viewers, followers)

**Endpoint:**
- `https://www.cbhours.com/api.php`

**Parámetros:**
- `action=get_activity`
- `domain=striphours` (o cbhours, sodahours)
- `username`: Username de la modelo
- `start_date`, `end_date`: Rango de fechas
- `tzo`: Timezone offset

**Rate Limiting:**
- 1.1 segundos entre requests
- Máximo 60 días por request

**Librería:**
- `requests>=2.31.0` (custom wrapper)

**Respuesta:**
- JSON con `details`: Segmentos de 3 minutos por fecha
- Se calculan métricas diarias: best_rank, avg_rank, viewers, followers, etc.

---

## 📦 Dependencias

### Python (Backend Principal)

**`requirements.txt`:**
```
python-telegram-bot>=20.8      # Bot de Telegram
python-dotenv>=1.0.0            # Variables de entorno
google-generativeai>=0.3.0      # Gemini API
requests>=2.31.0                 # HTTP requests
selenium>=4.15.0                 # Automatización (legacy, no usado)
webdriver-manager>=4.0.0         # Selenium (legacy)
pyautogui>=0.9.54                # Automatización GUI (legacy)
typing-extensions>=4.8.0         # Tipos
pillow>=10.1.0                   # Procesamiento de imágenes
python-dateutil>=2.8.2          # Manejo de fechas
```

**`admin_panel/backend/requirements.txt`:**
```
fastapi==0.104.1                 # Framework web
uvicorn[standard]==0.24.0        # ASGI server
python-dotenv==1.0.0             # Variables de entorno
supabase==2.0.0                  # Cliente Supabase
playwright==1.40.0               # Automatización (Python)
pydantic==2.5.0                  # Validación de datos
sqlmodel==0.0.14                 # ORM (no usado activamente)
python-multipart==0.0.6          # Upload de archivos
aiofiles==23.2.1                 # Archivos asíncronos
Pillow==10.1.0                   # Procesamiento de imágenes
google-generativeai>=0.3.0       # Gemini API
```

### Node.js

**`package.json` (raíz):**
```json
{
  "dependencies": {
    "playwright": "^1.57.0"
  },
  "devDependencies": {
    "@playwright/test": "^1.57.0"
  }
}
```

**`admin_panel/frontend/package.json`:**
```json
{
  "dependencies": {
    "next": "^14.0.4",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@tanstack/react-query": "^5.14.2",
    "axios": "^1.6.2",
    "zustand": "^4.4.7",
    "clsx": "^2.0.0",
    "lucide-react": "^0.294.0"
  },
  "devDependencies": {
    "typescript": "^5.3.3",
    "tailwindcss": "^3.3.6",
    "postcss": "^8.4.32",
    "autoprefixer": "^10.4.16"
  }
}
```

---

## 🎨 Decisiones Arquitectónicas

### 1. Separación de Responsabilidades

**Decisión:** Separar bot de Telegram, panel admin, y schedulers en procesos independientes.

**Razón:**
- Escalabilidad: Cada componente puede escalar independientemente
- Mantenibilidad: Código más organizado
- Resiliencia: Fallo en un componente no afecta a otros

**Implementación:**
- `main.py` lanza todos los procesos
- Cada proceso corre en su propio subprocess

---

### 2. Persistencia Híbrida (Supabase + Archivos Locales)

**Decisión:** Usar Supabase para schedules y configuración, archivos locales para videos y métricas.

**Razón:**
- Videos: Muy grandes para base de datos (hasta 4GB)
- Métricas: JSON local es más rápido para lectura frecuente
- Schedules: Supabase permite consultas complejas y sincronización

**Estructura:**
- Supabase: `modelos` (config), `[modelo]` (schedules)
- Local: `modelos/[modelo]/` (videos, config.json, metrics.json, browser_profile/)

---

### 3. Navegadores Persistentes por Modelo

**Decisión:** Cada modelo tiene su propio `browser_profile/` para aislar sesiones.

**Razón:**
- Múltiples modelos pueden usar la misma plataforma
- Sesiones no se mezclan
- Login una vez, usar siempre

**Implementación:**
- Playwright guarda cookies/localStorage/sessionStorage automáticamente
- Workers cargan `storageState` desde `modelos/[modelo]/browser_profile/`

---

### 4. Generación Automática de Workers con IA

**Decisión:** Usar Gemini para generar workers desde network logs capturados.

**Razón:**
- Acelera desarrollo de soporte para nuevas plataformas
- Reduce errores humanos
- Mantiene consistencia con workers existentes

**Flujo:**
1. Captura network flow con Playwright
2. Analiza endpoints y autenticación
3. Genera código usando workers de referencia
4. Guarda en `workers/[plataforma].js`

---

### 5. Scheduler de Publicación Inteligente

**Decisión:** Algoritmo que respeta reglas de negocio (gaps, límites, ventanas).

**Razón:**
- Evita spam en plataformas
- Distribuye contenido de forma natural
- Respeta horarios de mayor audiencia

**Reglas Implementadas:**
- Máximo 6 apariciones del mismo video
- Máximo 3 videos distintos por día
- Mínimo 10 minutos entre publicaciones
- Ventana de publicación configurable

---

### 6. Zona Horaria UTC para Métricas

**Decisión:** Todas las operaciones de fechas usan UTC.

**Razón:**
- La API de Striphours indexa por fecha en UTC
- Evita desfases entre hora local (Colombia UTC-5) y UTC
- Ejemplo: "Nov 25 00:00 UTC" = "Nov 24 19:00 Colombia", pero ambos son "Nov 25" en datos

**Implementación:**
- `datetime.now(timezone.utc)` en lugar de `datetime.now()`
- Fechas almacenadas en formato UTC (YYYY-MM-DD)

---

### 7. Servidor Local de Telegram Bot API

**Decisión:** Usar servidor local para archivos grandes (>50MB).

**Razón:**
- Telegram Bot API oficial limita a 50MB
- Servidor local permite hasta 2GB
- Videos pueden ser muy grandes

**Implementación:**
- Script `start_local_bot_api.sh` inicia servidor Docker
- Bot usa `base_url="http://127.0.0.1:8081/bot"` y `local_mode=True`

---

## ⚠️ Problemas Potenciales y Code Smells

### 1. **Manejo de Errores Inconsistente**

**Problema:**
- Algunos módulos usan `try/except` genérico
- Errores silenciados con `pass` o `continue`
- Falta logging estructurado

**Ejemplos:**
```python
# bot_central.py línea 77
except Exception as e:
    print(f"  ⚠️  Error cargando {config_path}: {e}")
    continue  # Silencia error
```

**Recomendación:**
- Usar logging estructurado (`logging.getLogger(__name__)`)
- No silenciar errores críticos
- Implementar retry con backoff para errores transitorios

---

### 2. **Dependencias Legacy No Usadas**

**Problema:**
- `requirements.txt` incluye `selenium`, `webdriver-manager`, `pyautogui`
- No se usan en el código (se usa Playwright)

**Ubicación:**
- `requirements.txt` líneas 8-10

**Recomendación:**
- Eliminar dependencias no usadas
- Reducir superficie de ataque y tamaño de instalación

---

### 3. **Hardcoded Values**

**Problema:**
- Valores hardcodeados en varios lugares
- Dificulta configuración y testing

**Ejemplos:**
```python
# poster.py línea 37
colombia_tz = pytz.timezone('America/Bogota')  # Hardcoded

# bot_central.py línea 411
TELEGRAM_BASE_URL = "http://127.0.0.1:8081/bot"  # Hardcoded
```

**Recomendación:**
- Mover a variables de entorno
- Usar valores por defecto razonables

---

### 4. **Falta de Validación de Input**

**Problema:**
- Algunos endpoints no validan input adecuadamente
- Puede causar errores en runtime

**Ejemplo:**
```python
# models_router.py - algunos campos opcionales no se validan
```

**Recomendación:**
- Usar Pydantic models para validación
- Validar en frontend y backend

---

### 5. **Race Conditions en Scheduler**

**Problema:**
- `poster.py` y `kpi_scheduler.py` pueden ejecutarse concurrentemente
- No hay locks para evitar condiciones de carrera

**Riesgo:**
- Múltiples instancias de `poster.py` podrían procesar el mismo post
- Estado inconsistente en Supabase

**Recomendación:**
- Usar locks (file locks o Redis)
- O usar `SELECT FOR UPDATE` en Supabase

---

### 6. **Manejo de Timeouts**

**Problema:**
- Algunas operaciones no tienen timeouts
- Pueden colgarse indefinidamente

**Ejemplo:**
```python
# capture_router.py - Playwright puede colgarse
await page.wait_for_timeout(600000)  # 10 min sin timeout real
```

**Recomendación:**
- Usar `asyncio.wait_for()` con timeout
- Implementar cancelación de tareas

---

### 7. **Caché en Memoria No Persistente**

**Problema:**
- `caption.py` usa caché global (`_TAGS_CACHE`, `_CONFIG_CACHE`)
- Se pierde al reiniciar
- No se invalida cuando cambian archivos

**Ubicación:**
- `caption.py` líneas 33-34

**Recomendación:**
- Usar caché con TTL
- Invalidar cuando cambian archivos (usar `mtime`)

---

### 8. **Falta de Tests**

**Problema:**
- Carpeta `tests/` existe pero casi vacía
- No hay tests unitarios ni de integración

**Recomendación:**
- Implementar tests para módulos críticos
- Tests de integración para flujos completos
- CI/CD para ejecutar tests automáticamente

---

### 9. **Manejo de Archivos Grandes**

**Problema:**
- Videos pueden ser muy grandes (hasta 4GB)
- No hay validación de espacio en disco
- No hay compresión o optimización

**Recomendación:**
- Validar espacio disponible antes de guardar
- Implementar limpieza de videos antiguos
- Considerar compresión o almacenamiento externo (S3)

---

### 10. **Seguridad de Credenciales**

**Problema:**
- Credenciales en `.env` (correcto)
- Pero algunos valores se loguean o imprimen

**Ejemplo:**
```python
# Puede exponer tokens en logs
logger.info(f"Token: {token[:30]}...")  # Aceptable
logger.info(f"Token: {token}")  # ❌ Peligroso
```

**Recomendación:**
- Nunca loguear credenciales completas
- Usar máscaras o truncar
- Revisar todos los logs antes de compartir

---

### 11. **Falta de Monitoreo**

**Problema:**
- No hay métricas de salud del sistema
- No hay alertas cuando fallan procesos
- Difícil diagnosticar problemas en producción

**Recomendación:**
- Implementar health checks
- Métricas de Prometheus o similar
- Alertas (email, Telegram) cuando fallan procesos

---

### 12. **Documentación de API Incompleta**

**Problema:**
- FastAPI genera docs automáticas (`/docs`)
- Pero algunos endpoints no tienen descripciones detalladas
- Falta documentación de errores posibles

**Recomendación:**
- Agregar docstrings detallados
- Documentar códigos de error
- Ejemplos de requests/responses

---

## 💡 Recomendaciones

### Corto Plazo (1-2 semanas)

1. **Eliminar dependencias no usadas**
   - Remover `selenium`, `webdriver-manager`, `pyautogui` de `requirements.txt`

2. **Mejorar logging**
   - Implementar logging estructurado en todos los módulos
   - Configurar niveles de log por ambiente

3. **Validación de input**
   - Agregar validación Pydantic en todos los endpoints
   - Validar en frontend también

4. **Manejo de errores**
   - No silenciar errores críticos
   - Implementar retry con backoff donde sea apropiado

### Mediano Plazo (1-2 meses)

1. **Tests**
   - Tests unitarios para `scheduler.py`, `caption.py`
   - Tests de integración para flujos completos
   - Tests E2E para workers de Playwright

2. **Monitoreo**
   - Health checks para todos los servicios
   - Métricas básicas (posts publicados, errores, etc.)
   - Alertas cuando fallan procesos

3. **Optimización**
   - Caché con TTL para tags y configs
   - Validación de espacio en disco
   - Limpieza automática de videos antiguos

4. **Seguridad**
   - Revisar todos los logs para credenciales
   - Implementar rate limiting en API
   - Validar permisos de archivos

### Largo Plazo (3-6 meses)

1. **Escalabilidad**
   - Considerar cola de mensajes (Redis/RabbitMQ) para posts
   - Separar workers en servicios independientes
   - Almacenamiento externo para videos (S3, etc.)

2. **Arquitectura**
   - Microservicios si el sistema crece
   - API Gateway para centralizar autenticación
   - Base de datos de solo lectura para métricas (replicación)

3. **Features**
   - Dashboard de analíticas avanzado
   - Programación avanzada (recurrencia, etc.)
   - Integración con más servicios de IA

---

## 📝 Notas Finales

Este documento técnico proporciona una visión completa del proyecto **100 Tráfico** para facilitar la auditoría y el mantenimiento futuro.

**Puntos Clave:**
- Sistema funcional y en producción
- Arquitectura modular y escalable
- Algunas áreas de mejora identificadas
- Recomendaciones priorizadas por impacto

**Contacto:**
Para preguntas o aclaraciones sobre este documento, consultar el código fuente o la documentación en `docs/`.

---

**Última actualización:** Noviembre 2025  
**Versión del documento:** 1.0.0






