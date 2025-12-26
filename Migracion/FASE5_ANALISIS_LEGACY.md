# FASE 5: Análisis de Código Legacy

**Fecha:** 2025-01-XX  
**Objetivo:** Identificar y planificar eliminación segura del sistema antiguo

## Resumen Ejecutivo

El sistema PRD está operativo (FASES 3, 4A, 4B completadas). Este documento identifica todo el código que usa tablas dinámicas o el sistema antiguo, analiza riesgos y propone orden de eliminación.

## Código Legacy Identificado

### 🔴 CRÍTICO - Usa Tablas Dinámicas Activamente

#### 1. `100trafico/src/project/poster.py` (188 líneas)
**Estado:** ❌ DEPRECATED - Reemplazado por `poster_prd.py`

**Uso de tablas dinámicas:**
- `get_all_models()`: Lee `modelos.modelo` (estructura antigua)
- `get_pending_posts(modelo)`: Lee `supabase.table(modelo)` (tabla dinámica)
- `process_post(modelo, post)`: Actualiza `supabase.table(modelo)` (tabla dinámica)

**Líneas específicas:**
- Línea 28: `supabase.table('modelos').select("modelo")` (estructura antigua)
- Línea 45: `supabase.table(modelo).select("*")` (tabla dinámica)
- Línea 52-56: Query a tabla dinámica con filtros
- Línea 67: `supabase.table(modelo).update({'estado': 'procesando'})`
- Línea 90: `supabase.table(modelo).update({'estado': 'fallido'})`
- Línea 149: `supabase.table(modelo).update({'estado': final_status})`
- Línea 159: `supabase.table(modelo).update({'estado': 'fallido'})`

**Riesgos:**
- ⚠️ **ALTO**: Si se ejecuta, procesará publicaciones de tablas dinámicas
- ⚠️ **MEDIO**: Puede interferir con `poster_prd.py` si ambos corren
- ✅ **BAJO**: No afecta datos PRD (solo lee/escribe tablas dinámicas)

**Reemplazo:**
- ✅ `poster_prd.py` cubre 100% de funcionalidad

**Acción recomendada:**
- Renombrar a `poster.py.legacy` o eliminar directamente
- Verificar que no hay procesos ejecutándolo

---

#### 2. `100trafico/src/project/scheduler.py` (214 líneas)
**Estado:** ❌ DEPRECATED - Reemplazado por `scheduler_prd.py`

**Uso de tablas dinámicas:**
- `_get_model_config(modelo)`: Lee `modelos` (estructura antigua)
- `_get_all_records(modelo)`: Lee `supabase.table(modelo)` (tabla dinámica)
- `plan(modelo, video_filename)`: Calcula slots basado en tablas dinámicas

**Líneas específicas:**
- Línea 15: `from database.supabase_client import get_model_config, get_all_schedules`
- Línea 41: `get_model_config(modelo)` (estructura antigua)
- Línea 67: `get_all_schedules(modelo)` (tabla dinámica)
- Línea 175: `records = _get_all_records(modelo)` (tabla dinámica)

**Riesgos:**
- ⚠️ **ALTO**: Si se ejecuta, creará schedules en tablas dinámicas
- ⚠️ **MEDIO**: Puede interferir con `scheduler_prd.py` si ambos corren
- ✅ **BAJO**: No afecta datos PRD (solo lee/escribe tablas dinámicas)

**Reemplazo:**
- ✅ `scheduler_prd.py` cubre 100% de funcionalidad

**Acción recomendada:**
- Renombrar a `scheduler.py.legacy` o eliminar directamente
- Verificar que no hay procesos ejecutándolo

---

#### 3. `100trafico/src/project/caption.py` - Función `generate_and_update()` (líneas 348-414)
**Estado:** ⚠️ PARCIALMENTE DEPRECATED - Solo función específica

**Uso de tablas dinámicas:**
- `ensure_model_exists(modelo)`: Crea tabla dinámica si no existe
- `insert_schedule(...)`: Inserta en tabla dinámica

**Líneas específicas:**
- Línea 375: `from database.supabase_client import get_model_config, insert_schedule, ensure_model_exists`
- Línea 378: `ensure_model_exists(modelo)` (crea tabla dinámica)
- Línea 394: `insert_schedule(...)` (inserta en tabla dinámica)

**Riesgos:**
- ⚠️ **MEDIO**: Si se llama `generate_and_update()`, creará schedules en tablas dinámicas
- ✅ **BAJO**: `generate_caption_and_tags()` (función pura) sigue siendo útil
- ✅ **BAJO**: `bot_central.py` ya NO usa `generate_and_update()` (FASE 4A)

**Reemplazo:**
- ✅ `bot_central.py` usa `generate_caption_and_tags()` directamente
- ✅ `contenidos_prd.py` crea contenidos en PRD

**Acción recomendada:**
- Marcar `generate_and_update()` como deprecated
- Agregar warning si se llama
- Mantener `generate_caption_and_tags()` (función pura)

---

#### 4. `100trafico/src/database/supabase_client.py` - Funciones Legacy (líneas 28-307)
**Estado:** ⚠️ PARCIALMENTE DEPRECATED - Funciones específicas

**Funciones que usan tablas dinámicas:**

##### `get_model_config(modelo)` (líneas 28-42)
- Lee `modelos.modelo` (estructura antigua con columna `modelo` como PK)
- **Riesgo:** ⚠️ MEDIO - Usado por código legacy
- **Reemplazo:** Usar `modelos.nombre` en esquema PRD

##### `create_model_config(...)` (líneas 45-70)
- Crea en `modelos` con estructura antigua
- **Riesgo:** ⚠️ MEDIO - Crea modelos con estructura antigua
- **Reemplazo:** Usar esquema PRD directamente

##### `create_model_table(modelo)` (líneas 86-158)
- Crea tabla dinámica para modelo
- **Riesgo:** 🔴 ALTO - Crea tablas dinámicas
- **Reemplazo:** No necesario en PRD

##### `ensure_model_exists(...)` (líneas 161-212)
- Crea modelo y tabla dinámica
- **Riesgo:** 🔴 ALTO - Crea tablas dinámicas
- **Reemplazo:** No necesario en PRD

##### `insert_schedule(...)` (líneas 215-247)
- Inserta en tabla dinámica
- **Riesgo:** 🔴 ALTO - Escribe en tablas dinámicas
- **Reemplazo:** `scheduler_prd.py` crea en `publicaciones`

##### `get_all_schedules(modelo)` (líneas 250-262)
- Lee tabla dinámica
- **Riesgo:** ⚠️ MEDIO - Usado por `scheduler.py` legacy
- **Reemplazo:** Leer de `publicaciones` con joins

##### `get_pending_schedules(...)` (líneas 265-286)
- Lee tabla dinámica con filtros
- **Riesgo:** ⚠️ MEDIO - Usado por código legacy
- **Reemplazo:** Leer de `publicaciones` con filtros

##### `update_schedule_time(...)` (líneas 289-307)
- Actualiza tabla dinámica
- **Riesgo:** 🔴 ALTO - Escribe en tablas dinámicas
- **Reemplazo:** `scheduler_prd.py` calcula `scheduled_time` al crear

**Riesgos generales:**
- 🔴 **ALTO**: Funciones de creación/escritura en tablas dinámicas
- ⚠️ **MEDIO**: Funciones de lectura (pueden usarse por código legacy)
- ✅ **BAJO**: No afecta datos PRD directamente

**Acción recomendada:**
- Marcar funciones legacy como deprecated
- Crear `supabase_client_prd.py` con funciones PRD
- Mantener funciones legacy temporalmente con warnings

---

#### 5. `100trafico/src/database/create_model_table.js` (118 líneas)
**Estado:** ❌ DEPRECATED - No necesario en PRD

**Uso:**
- Crea tablas dinámicas en Supabase
- Ejecutado por `create_model_table()` en Python

**Riesgos:**
- 🔴 **ALTO**: Crea tablas dinámicas
- ✅ **BAJO**: Solo se ejecuta si se llama `create_model_table()`

**Reemplazo:**
- ✅ No necesario en PRD (no hay tablas dinámicas)

**Acción recomendada:**
- Eliminar archivo
- Verificar que no se llama desde ningún lugar

---

#### 6. `100trafico/main.py` (81 líneas)
**Estado:** 🔴 CRÍTICO - Ejecuta `poster.py` legacy

**Uso de código legacy:**
- Línea 9: `POSTER_MAIN = BASE_DIR / "src" / "project" / "poster.py"`
- Línea 42: `p_poster = subprocess.Popen([python_exe, str(POSTER_MAIN)])`

**Riesgos:**
- 🔴 **CRÍTICO**: Si se ejecuta `main.py`, ejecutará `poster.py` legacy
- 🔴 **ALTO**: Procesará publicaciones de tablas dinámicas
- 🔴 **ALTO**: Puede interferir con `poster_prd.py`

**Reemplazo:**
- ✅ Cambiar a `poster_prd.py`
- ✅ Agregar `scheduler_prd.py` si es necesario

**Acción recomendada:**
- **URGENTE**: Actualizar `main.py` para usar `poster_prd.py`
- Verificar que no hay procesos ejecutando `main.py`

---

#### 7. `100trafico/admin_panel/backend/api/models_router.py` - Función `create_model()` (línea 288)
**Estado:** ⚠️ PARCIALMENTE DEPRECATED - Solo llamada específica

**Uso de tablas dinámicas:**
- Línea 288: `ensure_model_exists(...)` (crea tabla dinámica)

**Riesgos:**
- ⚠️ **MEDIO**: Al crear modelo desde admin panel, crea tabla dinámica
- ✅ **BAJO**: No afecta datos PRD (solo crea tabla dinámica vacía)

**Reemplazo:**
- ✅ Crear modelo directamente en esquema PRD
- ✅ No crear tabla dinámica

**Acción recomendada:**
- Refactorizar `create_model()` para usar esquema PRD
- Eliminar llamada a `ensure_model_exists()`

---

### 🟡 BAJO RIESGO - Solo Lectura o Uso Indirecto

#### 7. `100trafico/src/project/kpi_scheduler.py`
**Estado:** ✅ COMPATIBLE - Solo lee, no escribe en tablas dinámicas

**Análisis:**
- Solo importa `supabase` para leer métricas
- No usa tablas dinámicas
- No necesita cambios

**Acción recomendada:**
- ✅ Mantener sin cambios

---

## Confirmación de Cobertura PRD

### ✅ Bot Telegram
- **Antes:** `bot_central.py` → `generate_and_update()` → `insert_schedule()` → tabla dinámica
- **Ahora:** `bot_central.py` → `create_contenido()` → `contenidos` (PRD)
- **Estado:** ✅ COMPLETAMENTE MIGRADO (FASE 4A)

### ✅ Scheduler
- **Antes:** `scheduler.py` → lee tabla dinámica → crea schedules en tabla dinámica
- **Ahora:** `scheduler_prd.py` → lee `contenidos` → crea `publicaciones` (PRD)
- **Estado:** ✅ COMPLETAMENTE MIGRADO (FASE 4B)

### ✅ Poster
- **Antes:** `poster.py` → lee tabla dinámica → publica
- **Ahora:** `poster_prd.py` → lee `publicaciones` → publica
- **Estado:** ✅ COMPLETAMENTE MIGRADO (FASE 3)

### ✅ Caption
- **Antes:** `generate_and_update()` → `insert_schedule()` → tabla dinámica
- **Ahora:** `generate_caption_and_tags()` → usado por `bot_central.py` → `contenidos` (PRD)
- **Estado:** ✅ FUNCIÓN LEGACY NO SE USA (FASE 4A)

## Orden Seguro de Eliminación

### ETAPA 1: Marcar como Deprecated (Sin Eliminar)

**Objetivo:** Advertir sin romper nada

1. **Agregar warnings en funciones legacy:**
   - `supabase_client.py`: Agregar `@deprecated` a funciones legacy
   - `caption.py`: Agregar warning en `generate_and_update()`
   - `poster.py`: Agregar warning al inicio del archivo
   - `scheduler.py`: Agregar warning al inicio del archivo

2. **Verificar que no hay procesos ejecutando:**
   - Buscar procesos Python ejecutando `poster.py` o `scheduler.py`
   - Verificar logs del sistema
   - Confirmar que solo `poster_prd.py` y `scheduler_prd.py` están activos

**Riesgo:** ✅ BAJO - Solo agrega warnings

---

### ETAPA 2: Eliminar Archivos Completos Legacy

**Objetivo:** Eliminar código que ya no se usa

1. **`poster.py`** (188 líneas)
   - ✅ Reemplazado por `poster_prd.py`
   - ✅ No se usa en ningún lugar
   - **Acción:** Renombrar a `poster.py.legacy` o eliminar

2. **`scheduler.py`** (214 líneas)
   - ✅ Reemplazado por `scheduler_prd.py`
   - ✅ No se usa en ningún lugar
   - **Acción:** Renombrar a `scheduler.py.legacy` o eliminar

3. **`create_model_table.js`** (118 líneas)
   - ✅ No necesario en PRD
   - ✅ Solo usado por `create_model_table()` (deprecated)
   - **Acción:** Eliminar archivo

**Riesgo:** ⚠️ MEDIO - Verificar que no hay referencias

---

### ETAPA 3: Limpiar Funciones Legacy en Archivos Compartidos

**Objetivo:** Eliminar funciones específicas sin romper otros módulos

1. **`caption.py` - `generate_and_update()`** (líneas 348-414)
   - ✅ No se usa (bot usa `generate_caption_and_tags()` directamente)
   - **Acción:** Marcar como deprecated o eliminar función

2. **`supabase_client.py` - Funciones legacy:**
   - `create_model_table()` (líneas 86-158)
   - `ensure_model_exists()` (líneas 161-212)
   - `insert_schedule()` (líneas 215-247)
   - `get_all_schedules()` (líneas 250-262)
   - `get_pending_schedules()` (líneas 265-286)
   - `update_schedule_time()` (líneas 289-307)
   - **Acción:** Marcar como deprecated o mover a `supabase_client_legacy.py`

3. **`models_router.py` - Refactorizar `create_model()`:**
   - Eliminar llamada a `ensure_model_exists()`
   - Crear modelo directamente en esquema PRD
   - **Acción:** Refactorizar función

**Riesgo:** ⚠️ MEDIO - Verificar dependencias

---

### ETAPA 4: Eliminar Tablas Dinámicas de Supabase

**Objetivo:** Limpiar base de datos

1. **Verificar que no hay datos importantes:**
   - Ejecutar `migrate_fase2.py` si hay datos pendientes
   - Backup de tablas dinámicas

2. **Eliminar tablas dinámicas:**
   - Script SQL para eliminar todas las tablas dinámicas
   - Verificar que no hay FKs que dependan

**Riesgo:** 🔴 ALTO - Requiere backup y validación

---

## Checklist de Validación Pre-Eliminación

### Antes de ETAPA 1 (Marcar Deprecated)

- [ ] **CRÍTICO**: Actualizar `main.py` para usar `poster_prd.py` en lugar de `poster.py`
- [ ] Verificar que `poster_prd.py` está funcionando en producción
- [ ] Verificar que `scheduler_prd.py` está funcionando en producción
- [ ] Verificar que `bot_central.py` usa solo PRD (FASE 4A)
- [ ] Buscar procesos ejecutando `poster.py`, `scheduler.py` o `main.py`
- [ ] Verificar logs del sistema (últimos 7 días)
- [ ] Verificar que no hay servicios systemd o cron ejecutando código legacy

### Antes de ETAPA 2 (Eliminar Archivos)

- [ ] Buscar referencias a `poster.py` en código
- [ ] Buscar referencias a `scheduler.py` en código
- [ ] Buscar referencias a `create_model_table.js` en código
- [ ] Verificar que no hay imports de estos archivos
- [ ] Backup de archivos antes de eliminar

### Antes de ETAPA 3 (Limpiar Funciones)

- [ ] Buscar llamadas a `generate_and_update()` en código
- [ ] Buscar llamadas a funciones legacy de `supabase_client.py`
- [ ] Verificar que `models_router.py` puede refactorizarse
- [ ] Crear `supabase_client_prd.py` con funciones PRD si es necesario

### Antes de ETAPA 4 (Eliminar Tablas)

- [ ] Ejecutar `migrate_fase2.py` para migrar datos pendientes
- [ ] Backup completo de Supabase
- [ ] Listar todas las tablas dinámicas existentes
- [ ] Verificar que no hay FKs dependientes
- [ ] Crear script SQL de eliminación

---

## Archivos Legacy - Resumen

| Archivo | Líneas | Riesgo | Estado | Acción |
|---------|--------|--------|--------|--------|
| `poster.py` | 188 | 🔴 ALTO | ❌ DEPRECATED | Eliminar |
| `scheduler.py` | 214 | 🔴 ALTO | ❌ DEPRECATED | Eliminar |
| `caption.py` (función) | 67 | ⚠️ MEDIO | ⚠️ PARCIAL | Deprecar función |
| `supabase_client.py` (funciones) | ~280 | 🔴 ALTO | ⚠️ PARCIAL | Deprecar funciones |
| `create_model_table.js` | 118 | 🔴 ALTO | ❌ DEPRECATED | Eliminar |
| `models_router.py` (función) | 1 llamada | ⚠️ MEDIO | ⚠️ PARCIAL | Refactorizar |
| `main.py` | 2 líneas | 🔴 CRÍTICO | 🔴 CRÍTICO | Actualizar referencia |

**Total líneas legacy:** ~867 líneas + `main.py` (crítico)

---

## Confirmación de Cobertura PRD

### ✅ Flujo Completo Cubierto

1. **Entrada de datos:**
   - ✅ Bot Telegram → `contenidos` (PRD) - FASE 4A

2. **Procesamiento:**
   - ✅ Scheduler → lee `contenidos` → crea `publicaciones` (PRD) - FASE 4B

3. **Publicación:**
   - ✅ Poster → lee `publicaciones` → publica - FASE 3

4. **Trazabilidad:**
   - ✅ Eventos en `eventos_sistema` (PRD) - FASE 3

### ✅ Funcionalidades Cubiertas

- ✅ Crear contenidos
- ✅ Generar caption y tags
- ✅ Programar publicaciones
- ✅ Publicar contenido
- ✅ Registrar eventos
- ✅ Manejar errores
- ✅ Idempotencia

---

## Próximos Pasos

1. **Revisar este análisis** con el equipo
2. **Aprobar orden de eliminación**
3. **Ejecutar ETAPA 1** (marcar deprecated)
4. **Validar que no hay procesos legacy**
5. **Ejecutar ETAPAS 2-4** según aprobación

---

**Análisis completado. Esperando aprobación para proceder con eliminación.**

