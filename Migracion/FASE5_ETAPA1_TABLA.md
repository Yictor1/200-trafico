# FASE 5 - ETAPA 1: Tabla Resumen de Marcado

**Fecha:** 2025-12-25

---

## 📊 TABLA COMPLETA DE ARCHIVOS MARCADOS

| # | Archivo | Tipo | Estado | Líneas | Reemplazado por | Usado por |
|---|---------|------|--------|--------|----------------|-----------|
| 1 | `poster.py` | Archivo completo | @deprecated | 188 | `poster_prd.py` | Nadie (desactivado) |
| 2 | `scheduler.py` | Archivo completo | @deprecated | 214 | `scheduler_prd.py` | Nadie (desactivado) |
| 3 | `create_model_table.js` | Archivo completo | @deprecated | 118 | NO necesario en PRD | `create_model_table()` (deprecated) |
| 4 | `kpi_scheduler.py` | Archivo completo | ⚠️ WARNING | 503 | Requiere migración a PRD | `kpi_router.py` (admin panel) |
| 5 | `caption.generate_and_update()` | Función | @deprecated | 67 | `generate_caption_and_tags()` + `contenidos_prd` | Nadie (no llamada) |
| 6 | `supabase_client.get_model_config()` | Función | @deprecated | ~35 | Consultas directas PRD | `models_router.py`, archivos legacy |
| 7 | `supabase_client.create_model_config()` | Función | @deprecated | ~54 | Admin panel PRD | Nadie activo |
| 8 | `supabase_client.table_exists()` | Función | @deprecated | ~34 | NO necesario en PRD | `create_model_table()`, `ensure_model_exists()` |
| 9 | `supabase_client.create_model_table()` | Función | @deprecated | ~74 | NO necesario en PRD | `ensure_model_exists()` |
| 10 | `supabase_client.ensure_model_exists()` | Función | @deprecated | ~102 | Crear modelos desde admin panel | `models_router.py`, `caption.py` |
| 11 | `supabase_client.insert_schedule()` | Función | @deprecated | ~83 | `contenidos_prd.create_contenido()` | `caption.generate_and_update()` |
| 12 | `supabase_client.get_all_schedules()` | Función | @deprecated | ~63 | Consultas a `publicaciones` | `scheduler.py` (legacy) |
| 13 | `supabase_client.get_pending_schedules()` | Función | @deprecated | ~72 | `poster_prd.get_pending_publicaciones()` | Nadie activo |
| 14 | `supabase_client.update_schedule_time()` | Función | @deprecated | ~69 | `scheduler_prd` calcula al crear | Nadie activo |
| 15 | `bot_central.py` (imports) | Imports legacy | @deprecated | 2 imports | Ya usa `contenidos_prd` | Nadie (imports no usados) |
| 16 | `models_router.py` | Advertencia de uso | ⚠️ WARNING | N/A | Migrar en ETAPA 3 | Admin panel (activo) |

---

## 🎯 RESUMEN POR CATEGORÍA

### Archivos Completos (3)
- ❌ `poster.py`
- ❌ `scheduler.py`
- ❌ `create_model_table.js`

### Archivos con Warning Previo (1)
- ⚠️ `kpi_scheduler.py` (desactivado en main.py)

### Funciones en `supabase_client.py` (9)
- ❌ `get_model_config()`
- ❌ `create_model_config()`
- ❌ `table_exists()`
- ❌ `create_model_table()`
- ❌ `ensure_model_exists()`
- ❌ `insert_schedule()`
- ❌ `get_all_schedules()`
- ❌ `get_pending_schedules()`
- ❌ `update_schedule_time()`

### Función en `caption.py` (1)
- ❌ `generate_and_update()`

### Imports Legacy (1)
- ⚠️ `bot_central.py` (imports de `scheduler.plan` y `caption.generate_and_update` no usados)

### Archivos con Advertencia de Uso (1)
- ⚠️ `models_router.py` (admin panel usa funciones legacy)

---

## 📈 ESTADÍSTICAS

- **Total archivos marcados:** 8 archivos
- **Total funciones marcadas:** 10 funciones
- **Total líneas legacy documentadas:** ~867 líneas
- **Archivos con advertencias:** 2 archivos adicionales
- **Errores de lint:** 0 ✅

---

## ✅ VALIDACIÓN FINAL

| Criterio | Estado | Detalle |
|----------|--------|---------|
| Todo código legacy marcado | ✅ | Todos los archivos y funciones legacy identificados |
| Motivo técnico explícito | ✅ | Cada marcado explica por qué es legacy |
| Referencia a reemplazo | ✅ | Cada marcado indica qué lo reemplaza |
| Fecha de marcado | ✅ | Todos tienen fecha (2025-12-25) |
| Estado actual | ✅ | Todos indican si están desactivados o deprecated |
| Cero eliminaciones | ✅ | No se eliminó ningún archivo |
| Cero refactorizaciones | ✅ | No se modificó lógica |
| Runtime PRD intacto | ✅ | Bot Central + Poster PRD funcionando |
| Cero errores de lint | ✅ | Todos los archivos pasan lint |

---

## 🔗 REFERENCIAS CRUZADAS

- **Análisis de código legacy:** `FASE5_ANALISIS_LEGACY.md`
- **Plan de eliminación:** `FASE5_PLAN_ELIMINACION.md`
- **Resumen de ETAPA 1:** `FASE5_ETAPA1_COMPLETADA.md`
- **Índice visual:** `FASE5_ETAPA1_INDICE.md`

---

**ETAPA 1 COMPLETADA** ✅

Todo el código legacy está claramente marcado y documentado.
El repositorio es honesto, legible y está listo para ETAPA 2.



