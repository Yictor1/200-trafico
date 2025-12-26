# 📐 Arquitectura Oficial del Proyecto 100-Tráfico

Este documento define cómo está estructurado el proyecto y cómo deben integrarse todas las nuevas funcionalidades.

## 1. Módulos principales
- **Bot (src/project/bot_central.py)**
- **Workers Playwright (workers/)**
- **Scheduler (src/project/scheduler.py)**
- **Caption Engine (src/project/caption.py)**
- **KPIs (kpi_stripchat/)**
- **Backend FastAPI (admin_panel/backend/)**
- **Frontend Next.js (admin_panel/frontend/)**
- **Base de Datos Supabase (src/database/)**

## 2. Comunicación entre módulos
- Workers → generan datos → backend → Supabase
- Scheduler → dispara procesos → workers / kpi_scheduler / poster
- Bot → ingesta de videos → BD + scheduler
- Panel Admin → lectura + operaciones administrativas
- KPIs → se calculan por scheduler → BD → dashboard

## 3. Reglas de arquitectura
1. **Nunca mezclar lógica de negocio con UI.**
2. **Cada feature debe tener su propio servicio** (frontend/services/).
3. Los workers siempre van en `/workers/`.
4. Cada tabla nueva requiere un PRD de BD.
5. Si una funcionalidad requiere más de 3 pasos → crear un módulo dedicado.

## 4. Patrones recomendados
- Backend: "router + service"
- Front: "component + hook + service"
- Workers: patrón “task runner” multipaso
- KPIs: separar “captura”, “transformación”, “visualización”

## 5. Convención crucial
Todo lo nuevo debe pasar por PRD → router → agente.
