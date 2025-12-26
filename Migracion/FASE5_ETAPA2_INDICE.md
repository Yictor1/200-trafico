# FASE 5 - ETAPA 2: Índice Visual Post-Eliminación

**Fecha:** 2025-12-25

---

## 🗂️ MAPA DEL REPOSITORIO (POST-ETAPA 2)

```
100trafico/
├── src/
│   ├── project/
│   │   ├── ✅ bot_central.py (PRD - imports limpiados)
│   │   ├── ⚠️  caption.py (función generate_and_update deprecated)
│   │   ├── ⚠️  kpi_scheduler.py (WARNING - desactivado en main.py)
│   │   ├── ✅ poster_prd.py (PRD - activo en main.py)
│   │   └── ✅ scheduler_prd.py (PRD - disponible)
│   │
│   └── database/
│       ├── ✅ contenidos_prd.py (PRD - usado por bot)
│       └── ⚠️  supabase_client.py (9 funciones deprecated)
│
├── main.py ✅ (PRD - ejecuta bot_central.py + poster_prd.py)
└── admin_panel/ ⚠️ (usa funciones legacy de supabase_client.py)
```

---

## 🎯 ESTADO DEL SISTEMA

### ✅ RUNTIME PRD (ACTIVO)
```
main.py
├── Bot Central (bot_central.py)
│   └── contenidos_prd.create_contenido()
│       └── Tabla: contenidos
│
└── Poster PRD (poster_prd.py)
    └── Leer: publicaciones
    └── Ejecutar: workers/kams.js
```

### ❌ CÓDIGO LEGACY ELIMINADO
```
✅ poster.py (ELIMINADO - 188 líneas)
✅ scheduler.py (ELIMINADO - 214 líneas)
✅ create_model_table.js (ELIMINADO - 118 líneas)
```

### ⚠️ CÓDIGO LEGACY RESIDUAL (Funciones específicas)
```
supabase_client.py:
├── get_model_config() @deprecated
├── create_model_config() @deprecated
├── table_exists() @deprecated
├── create_model_table() @deprecated
├── ensure_model_exists() @deprecated
├── insert_schedule() @deprecated
├── get_all_schedules() @deprecated
├── get_pending_schedules() @deprecated
└── update_schedule_time() @deprecated

caption.py:
└── generate_and_update() @deprecated
```

---

## 📊 RESUMEN CUANTITATIVO

| Categoría | ANTES ETAPA 2 | DESPUÉS ETAPA 2 | Cambio |
|-----------|---------------|-----------------|--------|
| Archivos legacy completos | 3 | 0 | ✅ -3 |
| Funciones legacy | 10 | 10 | ⏸️ Sin cambio |
| Líneas legacy (aprox) | ~867 | ~347 | ✅ -520 (-60%) |
| Imports huérfanos | 4 | 0 | ✅ -4 |
| Archivos PRD activos | 5 | 5 | ✅ Intactos |
| Errores de lint | 0 | 0 | ✅ Cero |

---

## 🔍 BÚSQUEDA RÁPIDA

### Ver archivos PRD activos:
```bash
ls 100trafico/src/project/{bot_central,poster_prd,scheduler_prd}.py
ls 100trafico/src/database/contenidos_prd.py
ls 100trafico/main.py
```

### Verificar que archivos legacy fueron eliminados:
```bash
ls 100trafico/src/project/poster.py 2>&1        # Debe fallar
ls 100trafico/src/project/scheduler.py 2>&1      # Debe fallar
ls 100trafico/src/database/create_model_table.js 2>&1  # Debe fallar
```

### Ver funciones legacy restantes:
```bash
grep -n "@deprecated" 100trafico/src/database/supabase_client.py
grep -n "@deprecated" 100trafico/src/project/caption.py
```

---

## 🎯 PRÓXIMAS ETAPAS

### ETAPA 3: Limpiar funciones legacy
**Objetivo:** Eliminar/refactorizar funciones deprecated en archivos compartidos

**Archivos a procesar:**
- `supabase_client.py` (9 funciones)
- `caption.py` (1 función)
- `models_router.py` (refactorizar para no usar funciones legacy)

**Complejidad:** Media (requiere refactor de models_router.py)

---

### ETAPA 4: Eliminar tablas dinámicas
**Objetivo:** Limpiar base de datos de Supabase

**Tareas:**
- Backup completo
- Migrar datos pendientes
- Eliminar tablas dinámicas con SQL

**Complejidad:** Alta (requiere acceso a Supabase)

---

## ✅ VALIDACIÓN RÁPIDA

```bash
# Runtime PRD funcional
python3 100trafico/main.py  # Debe iniciar sin errores

# Sin errores de lint
pylint 100trafico/src/project/bot_central.py
pylint 100trafico/main.py

# Sin referencias huérfanas activas (solo docs y comentarios deprecated)
grep -r "poster\.py\|scheduler\.py\|create_model_table\.js" 100trafico/src/
```

---

## 📈 PROGRESO DE LIMPIEZA

```
ETAPA 1: ████████████████████ 100% (Marcado completo)
ETAPA 2: ████████████████████ 100% (Archivos eliminados)
ETAPA 3: ░░░░░░░░░░░░░░░░░░░░   0% (Pendiente)
ETAPA 4: ░░░░░░░░░░░░░░░░░░░░   0% (Pendiente)
```

**Progreso total:** 50% (2/4 etapas completadas)

---

**ÍNDICE ACTUALIZADO** ✅

El repositorio está significativamente más limpio.
Solo quedan funciones legacy específicas en archivos compartidos.



