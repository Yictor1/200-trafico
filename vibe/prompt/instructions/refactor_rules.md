# 🔧 Reglas de Refactor — 100-Tráfico

## 1. Antes de cualquier refactor
- Tener PRD de refactor aprobado.
- Entender qué módulo está afectado.
- Evitar tocar más de 3 archivos simultáneamente.

## 2. Código frontend
- Hooks deben ser puros.
- Services: solo fetch y transformaciones ligeras.
- Componentes sin lógica empresarial.
- No repetir UI.

## 3. Código backend
- Routers → solo rutas.
- Services → lógica y comunicación con Supabase.
- No incluir workers dentro del backend.
- Endpoints siempre deben validar inputs.

## 4. Workers
- Reutilizar funciones auxiliares.
- Manejar errores con try/catch.
- Esperas con `Promise.allSettled` si aplica.
- Cada worker debe tener logs claros.

## 5. Scheduler
- No mezclar lógica de scraping con scheduling.
- Cada tarea → función separada.
- Evitar tareas largas dentro del loop principal.

## 6. Eliminación de deuda técnica
- Comentarios TODO → convertirlos en PRDs.
- Eliminar funciones duplicadas.
- Crear módulos si un archivo tiene más de 500 líneas.
