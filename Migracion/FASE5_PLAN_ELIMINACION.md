# FASE 5: Plan de Eliminación Segura

## Resumen Ejecutivo

Este documento propone un plan de eliminación segura del código legacy en 4 etapas, con validaciones en cada paso.

## Archivos Legacy Identificados

### 🔴 CRÍTICO - Ejecución Activa

1. **`100trafico/main.py`** - Ejecuta `poster.py` legacy
2. **`100trafico/src/project/poster.py`** - Poster legacy (188 líneas)
3. **`100trafico/src/project/scheduler.py`** - Scheduler legacy (214 líneas)

### ⚠️ MEDIO - Uso Indirecto

4. **`100trafico/src/project/caption.py`** - Función `generate_and_update()` (67 líneas)
5. **`100trafico/src/database/supabase_client.py`** - Funciones legacy (~280 líneas)
6. **`100trafico/admin_panel/backend/api/models_router.py`** - Llamada a `ensure_model_exists()`

### 🔴 ALTO - Creación de Tablas Dinámicas

7. **`100trafico/src/database/create_model_table.js`** - Script de creación (118 líneas)

---

## ETAPA 0: URGENTE - Actualizar main.py

**Prioridad:** 🔴 CRÍTICA - Debe hacerse ANTES de cualquier otra eliminación

**Objetivo:** Evitar que se ejecute código legacy

**Cambios:**
```python
# ANTES (línea 9):
POSTER_MAIN = BASE_DIR / "src" / "project" / "poster.py"

# DESPUÉS:
POSTER_MAIN = BASE_DIR / "src" / "project" / "poster_prd.py"
```

**Adicional:**
- Considerar agregar `scheduler_prd.py` si se necesita ejecutar desde `main.py`

**Riesgo:** ✅ BAJO - Solo cambia referencia

**Validación:**
- [ ] `main.py` actualizado
- [ ] Verificar que `poster_prd.py` existe
- [ ] Probar ejecución de `main.py` (sin dejar corriendo)

---

## ETAPA 1: Marcar como Deprecated

**Objetivo:** Advertir sin romper nada

### 1.1 Agregar Warnings en Archivos Legacy

#### `poster.py`
```python
# Agregar al inicio del archivo:
import warnings
warnings.warn(
    "⚠️ DEPRECATED: poster.py está deprecated. Usa poster_prd.py en su lugar.",
    DeprecationWarning,
    stacklevel=2
)
```

#### `scheduler.py`
```python
# Agregar al inicio del archivo:
import warnings
warnings.warn(
    "⚠️ DEPRECATED: scheduler.py está deprecated. Usa scheduler_prd.py en su lugar.",
    DeprecationWarning,
    stacklevel=2
)
```

#### `caption.py` - Función `generate_and_update()`
```python
def generate_and_update(modelo: str, form_path: str):
    """
    ⚠️ DEPRECATED: Esta función está deprecated.
    Usa generate_caption_and_tags() directamente y crea contenidos con contenidos_prd.py
    """
    import warnings
    warnings.warn(
        "generate_and_update() está deprecated. Usa generate_caption_and_tags() + contenidos_prd.py",
        DeprecationWarning,
        stacklevel=2
    )
    # ... resto del código
```

#### `supabase_client.py` - Funciones Legacy
```python
def create_model_table(modelo: str) -> bool:
    """
    ⚠️ DEPRECATED: Esta función está deprecated.
    No se necesitan tablas dinámicas en el esquema PRD.
    """
    import warnings
    warnings.warn(
        "create_model_table() está deprecated. No se necesitan tablas dinámicas en PRD.",
        DeprecationWarning,
        stacklevel=2
    )
    # ... resto del código
```

**Riesgo:** ✅ BAJO - Solo agrega warnings

**Validación:**
- [ ] Warnings agregados
- [ ] Verificar que código PRD no muestra warnings
- [ ] Verificar que código legacy muestra warnings

---

## ETAPA 2: Eliminar Archivos Completos Legacy

**Objetivo:** Eliminar código que ya no se usa

### 2.1 Renombrar/Eliminar `poster.py`

**Opción A: Renombrar (más seguro)**
```bash
mv 100trafico/src/project/poster.py 100trafico/src/project/poster.py.legacy
```

**Opción B: Eliminar directamente**
```bash
rm 100trafico/src/project/poster.py
```

**Validación pre-eliminación:**
- [ ] Buscar referencias: `grep -r "poster.py" . --exclude-dir=.git`
- [ ] Verificar que `main.py` ya no lo referencia
- [ ] Verificar que no hay imports: `grep -r "from.*poster import\|import.*poster" .`

**Riesgo:** ⚠️ MEDIO - Verificar referencias primero

---

### 2.2 Renombrar/Eliminar `scheduler.py`

**Opción A: Renombrar (más seguro)**
```bash
mv 100trafico/src/project/scheduler.py 100trafico/src/project/scheduler.py.legacy
```

**Opción B: Eliminar directamente**
```bash
rm 100trafico/src/project/scheduler.py
```

**Validación pre-eliminación:**
- [ ] Buscar referencias: `grep -r "scheduler.py" . --exclude-dir=.git`
- [ ] Verificar que no hay imports: `grep -r "from.*scheduler import\|import.*scheduler" .`
- [ ] Verificar que `caption.py` no lo importa (ya no debería)

**Riesgo:** ⚠️ MEDIO - Verificar referencias primero

---

### 2.3 Eliminar `create_model_table.js`

```bash
rm 100trafico/src/database/create_model_table.js
```

**Validación pre-eliminación:**
- [ ] Buscar referencias: `grep -r "create_model_table.js" .`
- [ ] Verificar que `create_model_table()` en Python no se llama

**Riesgo:** ✅ BAJO - Solo se usa si se llama `create_model_table()`

---

## ETAPA 3: Limpiar Funciones Legacy en Archivos Compartidos

**Objetivo:** Eliminar funciones específicas sin romper otros módulos

### 3.1 `caption.py` - Eliminar `generate_and_update()`

**Opción A: Eliminar función completa**
- Eliminar líneas 348-414

**Opción B: Mantener con warning fuerte**
- Agregar `raise DeprecationWarning` al inicio

**Validación:**
- [ ] Buscar llamadas: `grep -r "generate_and_update" .`
- [ ] Verificar que `bot_central.py` NO la llama (FASE 4A)

**Riesgo:** ✅ BAJO - Ya no se usa

---

### 3.2 `supabase_client.py` - Funciones Legacy

**Opción A: Mover a archivo separado**
```bash
# Crear archivo legacy
mv funciones_legacy → supabase_client_legacy.py

# Mantener solo funciones PRD en supabase_client.py
```

**Opción B: Marcar como deprecated y mantener**
- Agregar `@deprecated` a todas las funciones legacy
- Mantener código por compatibilidad temporal

**Funciones a deprecar:**
- `get_model_config()` (estructura antigua)
- `create_model_config()` (estructura antigua)
- `create_model_table()`
- `ensure_model_exists()`
- `insert_schedule()`
- `get_all_schedules()`
- `get_pending_schedules()`
- `update_schedule_time()`

**Validación:**
- [ ] Buscar llamadas a cada función
- [ ] Verificar que código PRD no las usa
- [ ] Documentar funciones que aún se usan (si las hay)

**Riesgo:** ⚠️ MEDIO - Verificar dependencias

---

### 3.3 `models_router.py` - Refactorizar `create_model()`

**Cambios necesarios:**
1. Eliminar llamada a `ensure_model_exists()` (línea 288)
2. Crear modelo directamente en esquema PRD:
   ```python
   # En lugar de:
   ensure_model_exists(...)
   
   # Hacer:
   supabase.table('modelos').insert({
       "nombre": nombre_normalizado,
       "estado": "activa",
       "configuracion_distribucion": {
           "plataformas": plataformas_list,
           "hora_inicio": hora_inicio,
           "ventana_horas": ventana_horas
       }
   }).execute()
   ```

**Validación:**
- [ ] Probar creación de modelo desde admin panel
- [ ] Verificar que se crea en esquema PRD
- [ ] Verificar que NO se crea tabla dinámica

**Riesgo:** ⚠️ MEDIO - Requiere testing del admin panel

---

## ETAPA 4: Eliminar Tablas Dinámicas de Supabase

**Objetivo:** Limpiar base de datos

### 4.1 Preparación

1. **Backup completo de Supabase**
   ```bash
   # Exportar todas las tablas dinámicas
   # Usar pg_dump o herramienta de Supabase
   ```

2. **Listar tablas dinámicas existentes**
   ```sql
   SELECT table_name 
   FROM information_schema.tables 
   WHERE table_schema = 'public' 
   AND table_name NOT IN (
       'modelos', 'plataformas', 'cuentas_plataforma', 
       'contenidos', 'publicaciones', 'eventos_sistema'
   )
   AND table_name NOT LIKE 'pg_%'
   AND table_name NOT LIKE '_prisma%';
   ```

3. **Verificar datos pendientes**
   - Ejecutar `migrate_fase2.py` si hay datos
   - Verificar que no hay datos importantes

### 4.2 Script de Eliminación

```sql
-- Script para eliminar tablas dinámicas
-- ⚠️ EJECUTAR SOLO DESPUÉS DE BACKUP Y VALIDACIÓN

-- Lista de tablas dinámicas (obtener del paso 4.1)
-- Ejemplo:
-- DROP TABLE IF EXISTS yic CASCADE;
-- DROP TABLE IF EXISTS demo CASCADE;
-- ... (una por cada modelo)

-- Verificar que se eliminaron:
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name NOT IN (
    'modelos', 'plataformas', 'cuentas_plataforma', 
    'contenidos', 'publicaciones', 'eventos_sistema'
)
AND table_name NOT LIKE 'pg_%';
-- Debe retornar 0 filas
```

**Riesgo:** 🔴 ALTO - Requiere backup y validación

**Validación:**
- [ ] Backup completo realizado
- [ ] Datos migrados (si los hay)
- [ ] Lista de tablas confirmada
- [ ] Script SQL revisado
- [ ] Ejecutar en entorno de prueba primero

---

## Orden de Ejecución Recomendado

### Fase 0: URGENTE (Hacer primero)
1. ✅ Actualizar `main.py` para usar `poster_prd.py`

### Fase 1: Marcar Deprecated (Sin riesgo)
2. ✅ Agregar warnings en archivos legacy
3. ✅ Validar que warnings se muestran

### Fase 2: Eliminar Archivos (Riesgo medio)
4. ✅ Renombrar `poster.py` → `poster.py.legacy`
5. ✅ Renombrar `scheduler.py` → `scheduler.py.legacy`
6. ✅ Eliminar `create_model_table.js`
7. ✅ Validar que no hay referencias

### Fase 3: Limpiar Funciones (Riesgo medio)
8. ✅ Eliminar `generate_and_update()` de `caption.py`
9. ✅ Deprecar funciones legacy en `supabase_client.py`
10. ✅ Refactorizar `create_model()` en `models_router.py`
11. ✅ Validar que admin panel funciona

### Fase 4: Eliminar Tablas (Riesgo alto)
12. ✅ Backup completo de Supabase
13. ✅ Migrar datos pendientes (si los hay)
14. ✅ Crear script SQL de eliminación
15. ✅ Ejecutar en entorno de prueba
16. ✅ Ejecutar en producción
17. ✅ Validar que tablas se eliminaron

---

## Checklist de Validación Final

### Antes de Comenzar
- [ ] Sistema PRD funcionando en producción
- [ ] `poster_prd.py` validado
- [ ] `scheduler_prd.py` validado
- [ ] `bot_central.py` validado (FASE 4A)
- [ ] No hay procesos ejecutando código legacy
- [ ] Backup completo realizado

### Después de Cada Etapa
- [ ] Validar que sistema PRD sigue funcionando
- [ ] Verificar logs (sin errores nuevos)
- [ ] Probar flujo completo: Bot → Contenidos → Scheduler → Publicaciones → Poster

---

**Plan completado. Esperando aprobación para ejecutar ETAPA 0 (crítica).**



