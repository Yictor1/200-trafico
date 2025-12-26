# 🧠 Memoria Persistente del Proyecto — 100-Tráfico

Este documento almacena el conocimiento estable y no volátil del proyecto.

## 1. Objetivos del sistema
- Automatizar publicación y métricas de modelos adultos sin contenido explícito.
- Gestionar workers Playwright para scraping y posting.
- Calcular KPIs avanzados.
- Mostrar datos en panel admin.
- Integrar todo con bot Telegram.

## 2. Convenciones de trabajo
- PRD → Router → Agente → Implementación
- Workers siempre a mano en /workers/
- Scheduler controla:
  - publicación
  - KPIs
  - ingestión de datos

## 3. Reglas del proyecto
- Código limpio
- Módulos pequeños
- Datos centralizados en Supabase
- Nada se implementa sin PRD aprobado

## 4. Límites del sistema
- Respeto de límites de API
- Playwright es sensible a perfiles rotos
- KPIs dependen de APIs externas

## 5. Información útil
- Cada modelo tiene su carpeta: modelos/NOMBRE
- Capturas van en /captures/
- Perfil de navegador persistente por modelo
