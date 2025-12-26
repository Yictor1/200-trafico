# 📁 Estructura Completa del Proyecto - 100 Tráfico

**Generado:** Noviembre 2025  
**Propósito:** Documentación exhaustiva de la estructura del proyecto para configuración de fábrica de prompts y reglas del sistema

---

## 🌳 Árbol Completo de Directorios y Archivos

```
/home/victor/100-trafico/
│
├── .git/                                    # Repositorio Git
│   ├── branches/
│   ├── config                              # Configuración de Git
│   ├── description
│   ├── HEAD
│   ├── hooks/                              # Git hooks (muestras)
│   │   ├── applypatch-msg.sample
│   │   ├── commit-msg.sample
│   │   ├── fsmonitor-watchman.sample
│   │   ├── post-update.sample
│   │   ├── pre-applypatch.sample
│   │   ├── pre-commit.sample
│   │   ├── pre-merge-commit.sample
│   │   ├── prepare-commit-msg.sample
│   │   ├── pre-push.sample
│   │   ├── pre-rebase.sample
│   │   ├── pre-receive.sample
│   │   ├── push-to-checkout.sample
│   │   ├── sendemail-validate.sample
│   │   └── update.sample
│   ├── index                               # Índice de Git
│   ├── info/
│   │   └── exclude                        # Archivos excluidos de Git
│   ├── logs/                               # Logs de Git
│   │   ├── HEAD
│   │   └── refs/
│   │       ├── heads/
│   │       │   └── main
│   │       └── remotes/
│   │           └── origin/
│   │               ├── HEAD
│   │               └── main
│   ├── objects/                            # Objetos de Git
│   │   ├── info/
│   │   └── pack/
│   │       ├── pack-c8005eb92b2077f7812ef72b2997e501b76e6c37.idx
│   │       ├── pack-c8005eb92b2077f7812ef72b2997e501b76e6c37.pack
│   │       └── pack-c8005eb92b2077f7812ef72b2997e501b76e6c37.rev
│   ├── packed-refs
│   └── refs/
│       ├── heads/
│       │   └── main
│       ├── remotes/
│       │   └── origin/
│       │       └── HEAD
│       └── tags/
│
├── .gitignore                              # Archivos ignorados por Git
│
├── admin_panel/                            # Panel de Administración Web
│   ├── .gitignore                          # Gitignore específico del panel
│   ├── README.md                           # Documentación del panel admin
│   │
│   ├── backend/                            # Backend FastAPI
│   │   ├── api/                            # Routers de la API
│   │   │   ├── __init__.py
│   │   │   ├── auth_router.py              # Router de autenticación
│   │   │   ├── capture_router.py           # Router de captura de network flows
│   │   │   ├── kpi_router.py                # Router de métricas/KPIs
│   │   │   ├── models_router.py            # Router CRUD de modelos
│   │   │   ├── navegador_router.py         # Router de navegadores persistentes
│   │   │   ├── platforms_router.py         # Router de plataformas
│   │   │   └── workers_router.py           # Router de workers
│   │   ├── dev_server.py                   # Servidor de desarrollo
│   │   ├── main.py                         # Punto de entrada FastAPI
│   │   └── requirements.txt                # Dependencias Python del backend
│   │
│   └── frontend/                           # Frontend Next.js
│       ├── next.config.js                  # Configuración de Next.js
│       ├── next-env.d.ts                   # Tipos de Next.js
│       ├── package.json                     # Dependencias Node.js
│       ├── package-lock.json               # Lock file de dependencias
│       ├── postcss.config.js               # Configuración de PostCSS
│       ├── tailwind.config.js              # Configuración de Tailwind CSS
│       ├── tsconfig.json                    # Configuración de TypeScript
│       │
│       └── src/                            # Código fuente del frontend
│           ├── app/                        # App Router de Next.js
│           │   ├── globals.css             # Estilos globales
│           │   ├── layout.tsx              # Layout principal
│           │   ├── page.tsx                # Página principal (dashboard)
│           │   ├── providers.tsx           # Providers de React Query
│           │   │
│           │   ├── models/                 # Páginas de modelos
│           │   │   └── [modelo]/           # Ruta dinámica por modelo
│           │   │       └── metrics/        # Métricas del modelo
│           │   │           └── page.tsx
│           │   │
│           │   ├── platforms/              # Páginas de plataformas
│           │   │   └── page.tsx
│           │   │
│           │   └── workers/                # Páginas de workers
│           │       └── page.tsx
│           │
│           ├── features/                   # Features organizadas por dominio
│           │   │
│           │   ├── auth/                   # Feature de autenticación
│           │   │   ├── components/
│           │   │   │   └── PlatformAuthModal.tsx
│           │   │   ├── hooks/
│           │   │   │   └── useAuth.ts
│           │   │   └── services/
│           │   │       └── authService.ts
│           │   │
│           │   ├── kpi/                    # Feature de métricas/KPIs
│           │   │   ├── components/
│           │   │   │   └── MetricsDashboard.tsx
│           │   │   ├── hooks/
│           │   │   │   └── useKpi.ts
│           │   │   └── services/
│           │   │       └── kpiService.ts
│           │   │
│           │   ├── models/                # Feature de modelos
│           │   │   ├── components/
│           │   │   │   ├── CreateModelModal.tsx
│           │   │   │   ├── EditModelModal.tsx
│           │   │   │   ├── ModelCard.tsx
│           │   │   │   └── ModelList.tsx
│           │   │   ├── hooks/
│           │   │   │   └── useModels.ts
│           │   │   └── services/
│           │   │       └── modelService.ts
│           │   │
│           │   ├── platforms/             # Feature de plataformas
│           │   │   ├── components/
│           │   │   │   ├── AddPlatformModal.tsx
│           │   │   │   └── PlatformCard.tsx
│           │   │   ├── hooks/
│           │   │   │   └── usePlatforms.ts
│           │   │   └── services/
│           │   │       └── platformService.ts
│           │   │
│           │   └── workers/               # Feature de workers
│           │       ├── components/
│           │       │   └── WorkerCard.tsx
│           │       ├── hooks/
│           │       │   └── useWorkers.ts
│           │       └── services/
│           │           └── workerService.ts
│           │
│           └── shared/                    # Componentes y utilidades compartidas
│               ├── components/
│               │   ├── Button.tsx
│               │   ├── Input.tsx
│               │   ├── LoadingSpinner.tsx
│               │   ├── Modal.tsx
│               │   └── StatsCard.tsx
│               └── types/
│                   └── api.ts              # Tipos TypeScript para API
│
├── docs/                                   # Documentación del proyecto
│   ├── CHANGELOG_ORGANIZACION.md           # Changelog de organización
│   ├── DOCUMENTO_TECNICO.md                # Documento técnico completo
│   ├── ESTRUCTURA_COMPLETA.md              # Este archivo
│   ├── INICIO_RAPIDO.md                    # Guía de inicio rápido
│   ├── INSTALACION_AGENTE_CURSOR.md        # Instalación automatizada para Cursor
│   ├── INSTALACION.md                      # Guía de instalación completa
│   ├── INSTRUCCIONES_DOCKER.txt            # Instrucciones para Docker
│   ├── README.md                           # Índice de documentación
│   ├── TELEGRAM_ARCHIVOS_GRANDES.md       # Documentación de servidor local Telegram
│   └── VERIFICACION_BOT.md                 # Guía de verificación del bot
│
├── kpi_stripchat/                          # Módulo de métricas Striphours/CBHours
│   ├── api_cbhours                         # Script ejecutable de API (sin extensión)
│   ├── api_wrapper.py                      # Wrapper de la API de CBHours
│   ├── enhanced_dashboard.html              # Dashboard HTML (legacy)
│   └── requirements.txt                    # Dependencias del módulo KPI
│
├── main.py                                 # Launcher principal (inicia todos los servicios)
│
├── modelos/                                # Perfiles y datos de modelos
│   └── demo/                               # Modelo de demostración
│       ├── config.json                      # Configuración del modelo
│       ├── metrics.json                     # Métricas sincronizadas (Striphours)
│       └── profile_photo.jpg                # Foto de perfil (512x512)
│       # Nota: browser_profile/ se crea dinámicamente y está en .gitignore
│       # Nota: Videos (.mp4) se guardan aquí pero están en .gitignore
│
├── node_modules/                           # Dependencias Node.js (Playwright)
│   ├── .package-lock.json                  # Lock file interno
│   ├── @playwright/
│   │   └── test/                           # Playwright Test
│   ├── playwright/                         # Playwright core
│   └── playwright-core/                    # Playwright core engine
│
├── package.json                            # Dependencias Node.js principales
├── package-lock.json                       # Lock file de dependencias Node.js
│
├── prompt/                                 # Prompts y PRDs para desarrollo
│   ├── auditoria.prd.md                    # PRD para auditorías
│   ├── bot.prd.md                          # PRD del bot de Telegram
│   ├── feature_nueva.prd.md                # Template para nuevas features
│   ├── kpis.prd.md                         # PRD de métricas/KPIs
│   ├── panel_admin.prd.md                  # PRD del panel de administración
│   ├── refactor.prd.md                     # PRD para refactorizaciones
│   ├── router.prompt.md                     # Prompt para creación de routers
│   ├── scheduler.prd.md                    # PRD del scheduler
│   └── worker_nuevo.prd.md                # PRD para nuevos workers
│
├── README.md                               # Documentación principal del proyecto
│
├── requirements.txt                        # Dependencias Python principales
│
├── scripts/                                # Scripts de instalación e inicio
│   ├── install_docker_auto.sh              # Instalación automática de Docker
│   ├── start_backend.sh                    # Inicia backend FastAPI
│   ├── start_frontend.sh                   # Inicia frontend Next.js
│   └── start_local_bot_api.sh              # Inicia servidor local de Telegram Bot API
│
├── src/                                    # Código fuente principal
│   │
│   ├── database/                          # Cliente de base de datos (Supabase)
│   │   ├── __init__.py
│   │   ├── create_model_table.js           # Script Node.js para crear tablas dinámicas
│   │   └── supabase_client.py              # Cliente y funciones CRUD de Supabase
│   │
│   ├── project/                            # Módulos del bot y lógica principal
│   │   ├── __init__.py
│   │   ├── bot_central.py                  # Bot principal de Telegram
│   │   ├── caption.py                      # Generación de captions con Gemini
│   │   ├── kpi_scheduler.py                # Scheduler de métricas Striphours
│   │   ├── poster.py                       # Scheduler de publicación automática
│   │   └── scheduler.py                     # Planificación de slots de publicación
│   │
│   └── tags_disponibles.json               # Catálogo de tags para generación inteligente
│
├── tests/                                  # Tests del proyecto
│   ├── playwright.config.js                # Configuración de Playwright para tests
│   ├── test_credentials.py                 # Tests de credenciales
│   └── test_imports.py                     # Tests de imports
│
└── workers/                                # Workers de Playwright para automatización
    ├── dump_html.js                        # Worker de utilidad (dump HTML)
    ├── fikfap.js                           # Worker para FikFap
    ├── kams.js                             # Worker para Kams.com
    ├── page.html                           # HTML de prueba/utilidad
    └── xxxfollow.js                        # Worker para XXXFollow
    # Nota: Workers adicionales se generan automáticamente en esta carpeta
```

---

## 📋 Archivos de Configuración y Herramientas

### Archivos de Configuración Principales

1. **`.gitignore`** - Archivos ignorados por Git
   - Entornos virtuales (`.venv/`, `venv/`, `env/`)
   - Credenciales (`.env`, `*.key`, `*.pem`)
   - Archivos Python compilados (`__pycache__/`, `*.pyc`)
   - Logs (`*.log`, `logs/`)
   - Perfiles de navegador (`modelos/*/browser_profile/`)
   - Videos (`*.mp4`, `*.mov`, `*.avi`, `*.mkv`)
   - Capturas temporales (`captures/*.json`)

2. **`package.json`** (raíz) - Dependencias Node.js principales
   - `playwright`: ^1.57.0
   - `@playwright/test`: ^1.57.0 (dev)

3. **`requirements.txt`** (raíz) - Dependencias Python principales
   - `python-telegram-bot>=20.8`
   - `google-generativeai>=0.3.0`
   - `requests>=2.31.0`
   - `selenium>=4.15.0` (legacy, no usado)
   - `pillow>=10.1.0`
   - Y más...

4. **`admin_panel/backend/requirements.txt`** - Dependencias del backend
   - `fastapi==0.104.1`
   - `uvicorn[standard]==0.24.0`
   - `supabase==2.0.0`
   - `playwright==1.40.0`
   - Y más...

5. **`admin_panel/frontend/package.json`** - Dependencias del frontend
   - `next`: ^14.0.4
   - `react`: ^18.2.0
   - `@tanstack/react-query`: ^5.14.2
   - `tailwindcss`: ^3.3.6
   - Y más...

6. **`admin_panel/frontend/tsconfig.json`** - Configuración TypeScript
7. **`admin_panel/frontend/tailwind.config.js`** - Configuración Tailwind CSS
8. **`admin_panel/frontend/next.config.js`** - Configuración Next.js
9. **`admin_panel/frontend/postcss.config.js`** - Configuración PostCSS
10. **`tests/playwright.config.js`** - Configuración Playwright para tests

### Archivos de Entorno (No versionados, pero mencionados)

Los siguientes archivos pueden existir pero están en `.gitignore`:

- **`src/.env`** - Variables de entorno principales
  - `TELEGRAM_TOKEN`
  - `ADMIN_ID`
  - `GEMINI_API_KEY`
  - `SUPABASE_URL`
  - `SUPABASE_ANON_KEY`
  - `SUPABASE_ACCESS_TOKEN`
  - `SUPABASE_PROJECT_REF`

- **`.venv/`** o **`venv/`** - Entorno virtual de Python (si existe)

- **`modelos/[modelo]/.auth/`** - Archivos de autenticación por plataforma
  - `[plataforma].json` - Storage state de Playwright

- **`modelos/[modelo]/browser_profile/`** - Perfil de navegador persistente
  - Cookies, localStorage, sessionStorage

- **`captures/`** - Capturas de network flows (JSON)
- **`logs/`** - Logs del sistema

---

## 🔍 Estructura por Módulos

### 1. Bot de Telegram (`src/project/`)
- **`bot_central.py`**: Bot principal que recibe videos
- **`caption.py`**: Generación de captions con IA
- **`scheduler.py`**: Planificación de slots
- **`poster.py`**: Scheduler de publicación
- **`kpi_scheduler.py`**: Scheduler de métricas

### 2. Panel de Administración (`admin_panel/`)
- **Backend**: FastAPI con 7 routers
- **Frontend**: Next.js 14 con App Router
- **Features**: 5 features organizadas (auth, kpi, models, platforms, workers)

### 3. Workers de Automatización (`workers/`)
- Scripts Playwright para publicar en plataformas
- Generados automáticamente o manualmente

### 4. Base de Datos (`src/database/`)
- Cliente Supabase
- Script para crear tablas dinámicas

### 5. Métricas (`kpi_stripchat/`)
- Wrapper de API de CBHours/Striphours
- Dashboard HTML (legacy)

### 6. Prompts (`prompt/`)
- PRDs y prompts para desarrollo
- Templates para nuevas features

---

## 📊 Estadísticas del Proyecto

- **Total de archivos Python**: ~20
- **Total de archivos TypeScript/TSX**: ~30
- **Total de archivos JavaScript**: ~10
- **Total de workers**: 4 (kams, xxxfollow, fikfap, dump_html)
- **Total de routers API**: 7
- **Total de features frontend**: 5
- **Total de documentación**: 10 archivos

---

## 🎯 Notas Importantes para Fábrica de Prompts

1. **Estructura de Features**: Cada feature tiene `components/`, `hooks/`, `services/`
2. **Routers API**: Todos en `admin_panel/backend/api/`
3. **Workers**: Todos en `workers/`, siguen patrón similar
4. **Configuración**: Archivos `.env` en `src/` (no versionados)
5. **Modelos**: Cada modelo tiene su carpeta en `modelos/[nombre]/`
6. **Prompts**: Templates en `prompt/` para guiar desarrollo

---

**Última actualización:** Noviembre 2025  
**Versión:** 1.0.0

