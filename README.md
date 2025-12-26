# 🚀 100 Tráfico - Sistema de Gestión Automatizada de Contenido

Sistema profesional de gestión, automatización y programación de contenido para adultos con Inteligencia Artificial (Gemini) y persistencia de sesiones.

---

## ✨ Características Principales

### 🎯 Gestión de Modelos
- ✅ Crear, editar y eliminar perfiles de modelos
- ✅ Fotos de perfil con recorte automático 1:1
- ✅ Características físicas detalladas para IA
- ✅ Configuración de horarios de publicación

### 🌐 Navegador Persistente
- ✅ Perfil de navegador independiente por modelo
- ✅ **Sesiones guardadas automáticamente** (cookies, localStorage, sessionStorage)
- ✅ Login una vez, usar siempre
- ✅ Compatible con todas las plataformas de contenido para adultos

### 🤖 Automatización con IA
- ✅ Generación de captions con Google Gemini
- ✅ Análisis de flujos de plataformas
- ✅ Generación automática de workers Playwright
- ✅ Captura de tráfico de red para reverse engineering

### 💾 Base de Datos en la Nube
- ✅ Supabase para persistencia de datos
- ✅ Sincronización automática
- ✅ Escalable y seguro

---

## 📖 Documentación

- **[📚 Índice Completo](docs/README.md)** - Navegación de toda la documentación
- **[🚀 Inicio Rápido](docs/INICIO_RAPIDO.md)** - Comienza en 5 minutos
- **[📦 Instalación Completa](docs/INSTALACION.md)** - Guía detallada de instalación
- **[📡 Telegram Bot API Local](docs/TELEGRAM_ARCHIVOS_GRANDES.md)** - Soporte para archivos grandes (hasta 2GB)
- **[✅ Verificación del Bot](docs/VERIFICACION_BOT.md)** - Diagnóstico y solución de problemas

---

## 🛠️ Stack Tecnológico

### Backend
- **FastAPI** - Framework web moderno y rápido
- **Playwright** - Automatización web con navegadores reales
- **Supabase** - Base de datos PostgreSQL en la nube
- **Google Gemini** - IA para generación de contenido
- **Python 3.10+** - Lenguaje principal

### Frontend
- **Next.js 14** - Framework React con SSR
- **TypeScript** - Tipado estático
- **Tailwind CSS** - Estilos utility-first
- **React Query** - Gestión de estado del servidor
- **Axios** - Cliente HTTP

---

## 🚦 Inicio Rápido

```bash
# 1. Instalar dependencias
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r admin_panel/backend/requirements.txt
playwright install chromium

npm install
cd admin_panel/frontend && npm install && cd ../..

# 2. Configurar .env
cp src/.env.example src/.env
# Edita src/.env con tus credenciales

# 3. Iniciar servidor local de Telegram (para archivos grandes)
./scripts/start_local_bot_api.sh

# 4. Iniciar servicios
./scripts/start_backend.sh   # Terminal 1
./scripts/start_frontend.sh  # Terminal 2

# 5. Abrir panel
# http://localhost:3000
```

---

## 📁 Estructura del Proyecto

```
100-trafico/
├── admin_panel/          # Panel de administración web
│   ├── backend/          # API FastAPI
│   │   ├── api/          # Routers
│   │   └── main.py       # Punto de entrada
│   └── frontend/         # Aplicación Next.js
│       └── src/
│           ├── app/      # Páginas
│           ├── features/ # Componentes por funcionalidad
│           └── shared/   # Componentes compartidos
├── docs/                 # 📚 Documentación completa
├── scripts/              # 🔧 Scripts de instalación e inicio
├── tests/                # ✅ Archivos de prueba
├── src/                  # Lógica del sistema principal
│   ├── database/         # Cliente Supabase
│   ├── project/          # Bot de Telegram
│   └── .env              # Configuración (CREAR)
├── modelos/              # Perfiles de navegador por modelo
│   └── [nombre]/
│       ├── profile_photo.jpg
│       ├── config.json
│       └── browser_profile/    # Sesiones persistentes
├── workers/              # Workers generados automáticamente
├── logs/                 # Logs del sistema
├── captures/             # Capturas de tráfico de red
└── main.py               # 🚀 Bot de Telegram (punto de entrada)
```

---

## 🎯 Casos de Uso

### 1. Gestión de Múltiples Modelos
Administra perfiles de múltiples modelos desde un solo panel, cada una con su propio perfil de navegador independiente.

### 2. Automatización de Publicaciones
- Configura horarios de publicación
- Genera captions con IA
- Publica automáticamente en múltiples plataformas

### 3. Persistencia de Sesiones
- Inicia sesión una vez en cada plataforma
- El sistema mantiene las sesiones indefinidamente
- No necesitas volver a loguearte

### 4. Reverse Engineering de Plataformas
- Captura el tráfico de red de cualquier plataforma
- Analiza las peticiones HTTP
- Genera workers Playwright automáticamente con IA

---

## 🔐 Seguridad

- ✅ Credenciales en `.env` (no se suben a git)
- ✅ Perfiles de navegador aislados por modelo
- ✅ Conexión segura con Supabase
- ✅ Variables de entorno separadas por ambiente

---

## 📊 Requisitos del Sistema

- **Python**: 3.10 o superior
- **Node.js**: 18 o superior
- **Sistema Operativo**: Linux / macOS / Windows (WSL)
- **RAM**: 4GB mínimo (8GB recomendado)
- **Disco**: 2GB de espacio libre

---

## 🤝 Contribuir

Este proyecto está en desarrollo activo. Algunas áreas de mejora:

- [ ] Workers para más plataformas
- [ ] Programación avanzada de publicaciones
- [ ] Dashboard de analíticas
- [ ] Integración con más servicios de IA
- [ ] Sistema de notificaciones mejorado

---

## 📝 Licencia

Este proyecto es de uso privado. No redistribuir sin autorización.

---

## 🆘 Soporte

¿Problemas? Revisa:
1. **[docs/INSTALACION.md](docs/INSTALACION.md)** - Solución de problemas
2. **[docs/VERIFICACION_BOT.md](docs/VERIFICACION_BOT.md)** - Diagnóstico del bot
3. Logs del backend: `tail -f /tmp/backend_fresh.log`
4. Consola del navegador (F12)

---

## ✅ Estado del Proyecto

**Versión**: 1.0.0  
**Estado**: ✅ Funcional y en producción  
**Última actualización**: Noviembre 2025

### Funcionalidades Completadas
- ✅ Panel de administración completo
- ✅ CRUD de modelos
- ✅ Navegador persistente con sesiones
- ✅ Integración con Supabase
- ✅ Integración con Gemini AI
- ✅ Sistema de captura de plataformas
- ✅ Generación automática de workers

---

**Desarrollado con ❤️ para automatización de contenido**
