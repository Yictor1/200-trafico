# 🎬 Trafico Admin Panel

Panel de administración full-stack para gestionar modelos, plataformas y workers de automatización.

## 🎯 Características

- ✅ **Gestión de Modelos**: Crear, listar y eliminar modelos con Telegram ID
- ✅ **Gestión de Plataformas**: Agregar plataformas y capturar flujos de autenticación
- ✅ **Generación de Workers**: Genera workers de Playwright automáticamente
- ✅ **UI Premium**: Diseño moderno con Tailwind CSS y animaciones
- ✅ **Arquitectura Híbrida**: Feature-First (Frontend) + Clean Architecture (Backend)

## 📦 Tech Stack

**Frontend:**
- Next.js 15 + TypeScript
- Tailwind CSS
- React Query (data fetching)
- Zustand (state management)

**Backend:**
- FastAPI + Python 3.10+
- SQLModel (ORM)
- Supabase (PostgreSQL)
- Playwright (automation)

## 🚀 Quick Start

### 1. Instalar Dependencias

```bash
# Frontend
cd frontend
npm install

# Backend
cd ../backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

```bash
# Frontend: .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000

# Backend: .env (usa el .env de Trafico)
# Ya configurado en /home/victor/Escritorio/SkyFlow_Porn-master/Trafico/.env
```

### 3. Iniciar Servidores

```bash
# Terminal 1: Backend (auto-detecta puerto 8000-8006)
cd backend
python dev_server.py

# Terminal 2: Frontend (auto-detecta puerto 3000-3006)
cd frontend
npm run dev
```

## 🏗️ Arquitectura

### Frontend: Feature-First
```
frontend/src/
├── app/                    # Next.js App Router
├── features/               # Features organizadas
│   ├── models/            # Gestión de modelos
│   ├── platforms/         # Gestión de plataformas
│   └── workers/           # Gestión de workers
└── shared/                # Componentes reutilizables
```

### Backend: Clean Architecture
```
backend/
├── api/                   # Endpoints
├── application/           # Casos de uso
├── domain/                # Lógica de negocio
└── infrastructure/        # Implementaciones externas
```

## 📝 Funcionalidades Principales

### Gestión de Modelos
1. **Crear Modelo**: Solicita nombre y Telegram ID
2. **Listar Modelos**: Muestra todas las modelos con sus plataformas
3. **Eliminar Modelo**: Elimina modelo y sus datos

### Gestión de Plataformas
1. **Agregar Plataforma**: Captura flow de autenticación
2. **Navegador Automático**: Abre Playwright para login manual
3. **Generación de Worker**: Crea worker automáticamente desde network flow

### Gestión de Workers
1. **Listar Workers**: Muestra todos los workers en `/workers/`
2. **Ver Código**: Visualiza código del worker
3. **Editar Worker**: Permite edición manual

## 🎨 Diseño UI

- **Glassmorphism**: Cards con efecto de vidrio
- **Gradientes**: Colores vibrantes (índigo + rosa)
- **Dark Mode**: Tema oscuro por defecto
- **Animaciones**: Transiciones suaves
- **Responsive**: Mobile, tablet y desktop

## 📚 Integración con Trafico

El panel se integra con el proyecto Trafico existente:

- Lee/escribe en `Trafico/modelos/`
- Genera workers en `Trafico/workers/`
- Usa `src/database/supabase_client.py`

## 🔧 Desarrollo

### Comandos Útiles

```bash
# Frontend
npm run dev          # Servidor desarrollo
npm run build        # Build producción
npm run lint         # Linter
npm run typecheck    # TypeScript check

# Backend
python dev_server.py              # Servidor desarrollo
python -m pytest                  # Tests
python -m pytest --cov            # Coverage
```

## 📖 Documentación

- **Architecture**: Ver `docs/architecture.md`
- **API Reference**: `http://localhost:8000/docs` (Swagger)
- **Deployment**: Ver `docs/deployment.md`

---

**Trafico Admin Panel v1.0** | Built with ❤️ for content automation
