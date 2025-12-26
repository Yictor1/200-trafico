# FASE 5 - ETAPA 1: Índice Visual de Archivos Marcados

**Fecha:** 2025-12-25

---

## 🗂️ MAPA DE CÓDIGO LEGACY

```
100trafico/
├── src/
│   ├── project/
│   │   ├── ❌ poster.py (DEPRECATED - archivo completo)
│   │   ├── ❌ scheduler.py (DEPRECATED - archivo completo)
│   │   ├── ⚠️  caption.py (función generate_and_update deprecated)
│   │   ├── ⚠️  bot_central.py (imports legacy no usados)
│   │   ├── ⚠️  kpi_scheduler.py (WARNING - desactivado en main.py)
│   │   ├── ✅ poster_prd.py (PRD - activo)
│   │   ├── ✅ scheduler_prd.py (PRD - activo)
│   │   └── ✅ bot_central.py (PRD - activo, solo imports legacy)
│   │
│   └── database/
│       ├── ❌ create_model_table.js (DEPRECATED - archivo completo)
│       ├── ⚠️  supabase_client.py (9 funciones deprecated)
│       └── ✅ contenidos_prd.py (PRD - activo)
│
├── admin_panel/backend/api/
│   ├── ⚠️  models_router.py (usa funciones legacy - advertencia al inicio)
│   ├── ⚠️  kpi_router.py (importa kpi_scheduler - ok)
│   └── ✅ [otros routers] (PRD - activos)
│
└── main.py ✅ (PRD - usa poster_prd.py desde ETAPA 0)
```

---

## 📊 LEYENDA

- ❌ **DEPRECATED** - Archivo completo obsoleto, no usar
- ⚠️  **WARNING** - Contiene código legacy o usa funciones legacy
- ✅ **PRD** - Código PRD puro, activo y funcional

---

## 🔍 BÚSQUEDA RÁPIDA

### Archivos completos deprecated:
```bash
find . -name "poster.py" -o -name "scheduler.py" -o -name "create_model_table.js"
```

### Funciones deprecated en supabase_client.py:
- `get_model_config()`
- `create_model_config()`
- `table_exists()`
- `create_model_table()`
- `ensure_model_exists()`
- `insert_schedule()`
- `get_all_schedules()`
- `get_pending_schedules()`
- `update_schedule_time()`

### Función deprecated en caption.py:
- `generate_and_update()`

### Imports legacy en bot_central.py:
- `from scheduler import plan` (NO USADA)
- `from caption import generate_and_update` (NO USADA)

---

## 🎯 RUNTIME ACTUAL (PRD)

```
main.py
├── Bot Central (bot_central.py) ✅
│   └── contenidos_prd.create_contenido() ✅
│
└── Poster PRD (poster_prd.py) ✅
    └── Lee publicaciones (esquema PRD) ✅
```

**KPI Scheduler:** ❌ DESACTIVADO (línea 11 en main.py comentada)

---

## 📝 VALIDACIÓN RÁPIDA

```bash
# Ver todos los marcados @deprecated
grep -r "@deprecated" 100trafico/src/ 100trafico/admin_panel/

# Ver todos los warnings
grep -r "WARNING.*LEGACY\|ADVERTENCIA" 100trafico/

# Verificar que no hay imports a archivos legacy en código PRD
grep -r "from.*poster import\|from.*scheduler import" 100trafico/src/project/bot_central.py
```

---

**ETAPA 1 COMPLETADA** ✅



