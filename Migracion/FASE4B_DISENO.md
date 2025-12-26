# FASE 4B: Diseño del Scheduler PRD

## Objetivo

Crear un scheduler que lee `contenidos` y crea `publicaciones` en el esquema PRD, sin tocar tablas antiguas ni publicar nada.

## Flujo General

```
1. Leer contenidos con estado IN ('nuevo', 'aprobado')
2. Para cada contenido:
   a. Obtener modelo y configuración
   b. Obtener cuentas_plataforma válidas
   c. Calcular scheduled_time distribuido
   d. Crear publicaciones (una por plataforma)
   e. Marcar contenido como 'aprobado' o 'reutilizable'
```

## Decisiones de Diseño

### 1. Estados de Contenido

**Decisión:** Marcar contenido como `'aprobado'` después de crear publicaciones.

**Razón:**
- `'nuevo'` → contenido recién recibido, no procesado
- `'aprobado'` → contenido procesado, publicaciones creadas
- `'reutilizable'` → se usará en FASE futura para reposts

**Implementación:**
- Después de crear publicaciones exitosamente → `estado = 'aprobado'`
- Si falla → mantener `estado = 'nuevo'` para reintento

### 2. Idempotencia

**Estrategia:** Verificar si ya existen publicaciones para un contenido antes de crear nuevas.

**Query de verificación:**
```sql
SELECT COUNT(*) FROM publicaciones 
WHERE contenido_id = ? 
AND estado IN ('programada', 'procesando', 'publicado')
```

**Regla:**
- Si ya existen publicaciones → saltar contenido (ya procesado)
- Si no existen → crear publicaciones

### 3. Obtención de Cuentas Plataforma

**Query:**
```sql
SELECT cp.id, cp.plataforma_id, p.nombre 
FROM cuentas_plataforma cp
JOIN plataformas p ON cp.plataforma_id = p.id
WHERE cp.modelo_id = ?
AND p.activa = true
AND p.nombre IN (plataformas_de_configuracion)
```

**Validación:**
- Solo usar cuentas de plataformas activas
- Solo usar plataformas que están en `configuracion_distribucion.plataformas`
- Si no hay cuentas válidas → saltar contenido (log error)

### 4. Cálculo de scheduled_time

**Lógica heredada del scheduler actual:**
- Usar `hora_inicio` y `ventana_horas` de `configuracion_distribucion`
- Distribuir slots en la ventana con gaps mínimos
- Buscar desde hoy hasta `MAX_DAYS_AHEAD` días
- Máximo 3 videos distintos por día
- Mínimo `MIN_GAP_MINUTES` entre publicaciones

**Adaptación para PRD:**
- En lugar de leer de tabla dinámica, leer de `publicaciones` existentes
- Agrupar por `scheduled_time::date` para contar videos distintos
- Agrupar por `contenido_id` para contar apariciones del mismo video

### 5. Límites y Reglas

**Heredados del scheduler actual:**
- `MAX_SAME_VIDEO = 6` (máximo 6 apariciones del mismo contenido)
- `MAX_DAYS_AHEAD = 30` (buscar hasta 30 días adelante)
- `MIN_GAP_MINUTES = 10` (mínimo 10 minutos entre publicaciones)
- Máximo 3 videos distintos por día

**Validaciones:**
- Si contenido ya tiene >= 6 publicaciones → saltar (tope_video)
- Si día ya tiene >= 3 contenidos distintos → buscar siguiente día
- Si no hay espacio en ventana → buscar siguiente día

## Orden Exacto de Queries

### Query 1: Obtener contenidos pendientes
```python
contenidos = supabase.table('contenidos')\
    .select("*, modelos(*)")\
    .in_('estado', ['nuevo', 'aprobado'])\
    .order('recibido_at', desc=False)\
    .execute()
```

### Query 2: Para cada contenido, obtener configuración
```python
# Ya viene en join: contenido['modelos']['configuracion_distribucion']
config = contenido['modelos']['configuracion_distribucion']
plataformas = config.get('plataformas', [])
hora_inicio = config.get('hora_inicio', '12:00')
ventana_horas = config.get('ventana_horas', 5)
```

### Query 3: Verificar idempotencia
```python
existing_pubs = supabase.table('publicaciones')\
    .select("id")\
    .eq('contenido_id', contenido_id)\
    .in_('estado', ['programada', 'procesando', 'publicado'])\
    .execute()

if existing_pubs.data:
    # Ya procesado, saltar
    continue
```

### Query 4: Obtener cuentas_plataforma válidas
```python
cuentas = supabase.table('cuentas_plataforma')\
    .select("id, plataforma_id, plataformas!inner(nombre, activa)")\
    .eq('modelo_id', modelo_id)\
    .eq('plataformas.activa', True)\
    .in_('plataformas.nombre', plataformas)\
    .execute()
```

### Query 5: Contar publicaciones existentes del contenido
```python
count_pubs = supabase.table('publicaciones')\
    .select("id", count="exact")\
    .eq('contenido_id', contenido_id)\
    .execute()

if count_pubs.count >= MAX_SAME_VIDEO:
    # Tope alcanzado, saltar
    continue
```

### Query 6: Obtener publicaciones existentes para calcular slots
```python
# Para cada día en rango [hoy, hoy + MAX_DAYS_AHEAD]:
publicaciones_dia = supabase.table('publicaciones')\
    .select("scheduled_time, contenido_id")\
    .gte('scheduled_time', fecha_inicio_dia)\
    .lt('scheduled_time', fecha_fin_dia)\
    .in_('estado', ['programada', 'procesando', 'publicado'])\
    .execute()
```

### Query 7: Crear publicaciones
```python
for cuenta_id, scheduled_time in zip(cuenta_ids, scheduled_times):
    supabase.table('publicaciones').insert({
        "contenido_id": contenido_id,
        "cuenta_plataforma_id": cuenta_id,
        "scheduled_time": scheduled_time.isoformat(),
        "caption_usado": contenido.get('caption_generado', ''),
        "tags_usados": contenido.get('tags_generados', []),
        "estado": "programada",
        "intentos": 0
    }).execute()
```

### Query 8: Actualizar estado del contenido
```python
supabase.table('contenidos')\
    .update({"estado": "aprobado"})\
    .eq('id', contenido_id)\
    .execute()
```

## Estructura del Código

### Funciones Principales

1. **`get_pending_contenidos()`** → Lista contenidos con estado 'nuevo' o 'aprobado'
2. **`get_modelo_config(contenido)`** → Extrae configuración del modelo
3. **`get_cuentas_plataforma(modelo_id, plataformas)`** → Obtiene cuentas válidas
4. **`check_idempotencia(contenido_id)`** → Verifica si ya tiene publicaciones
5. **`check_limits(contenido_id)`** → Verifica límites (MAX_SAME_VIDEO)
6. **`calculate_scheduled_times(modelo_id, n_plataformas)`** → Calcula slots distribuidos
7. **`create_publicaciones(contenido, cuentas, scheduled_times)`** → Crea publicaciones
8. **`update_contenido_estado(contenido_id, estado)`** → Marca contenido como aprobado
9. **`process_contenido(contenido)`** → Procesa un contenido completo
10. **`main()`** → Loop principal

### Lógica de Distribución de Slots

**Heredada de `_build_slots_for_day()`:**
1. Primer slot cerca de inicio (con jitter 0-5 min)
2. Segundo slot cerca de fin (con jitter 0-5 min)
3. Midpoint entre 1 y 2
4. Midpoints entre ocupados (si hay espacio >= 2×gap)
5. Relleno hacia adelante en pasos de gap

**Adaptación:**
- En lugar de leer de tabla dinámica, leer de `publicaciones`
- Agrupar por fecha para contar videos distintos
- Agrupar por `contenido_id` para contar apariciones

## Manejo de Errores

### Errores No Críticos (continuar con siguiente contenido)
- Modelo no tiene configuración válida
- No hay cuentas_plataforma para plataformas configuradas
- Contenido ya tiene publicaciones (idempotencia)
- Contenido alcanzó tope (MAX_SAME_VIDEO)
- No hay espacio en ventana (sin_espacio)

### Errores Críticos (log y continuar)
- Error de conexión a Supabase
- Error al crear publicaciones
- Error al actualizar estado

## Logging

**Niveles:**
- ✅ `logger.info()`: Contenido procesado exitosamente
- ℹ️  `logger.info()`: Contenido saltado (idempotencia, límites)
- ⚠️  `logger.warning()`: Advertencias (sin cuentas, sin espacio)
- ❌ `logger.error()`: Errores con traceback

## Variables de Entorno

```python
MIN_GAP_MINUTES = int(os.getenv("MIN_GAP_MINUTES", "10"))
MAX_DAYS_AHEAD = int(os.getenv("MAX_DAYS_AHEAD", "30"))
MAX_SAME_VIDEO = int(os.getenv("MAX_SAME_VIDEO", "6"))
```

## Tests Mínimos Requeridos

### Test 1: 1 contenido → N publicaciones
- Crear contenido con estado 'nuevo'
- Ejecutar scheduler
- Verificar: N publicaciones creadas (una por plataforma)
- Verificar: contenido marcado como 'aprobado'

### Test 2: No duplicación en doble ejecución
- Ejecutar scheduler dos veces
- Verificar: segunda ejecución no crea publicaciones duplicadas
- Verificar: contenido sigue en 'aprobado'

### Test 3: Límites respetados
- Crear contenido con 6 publicaciones existentes
- Ejecutar scheduler
- Verificar: contenido no procesado (tope_video)

### Test 4: Sin cuentas válidas
- Crear contenido con modelo sin cuentas_plataforma
- Ejecutar scheduler
- Verificar: contenido no procesado (log warning)

## Checklist de Validación Manual

1. [ ] Scheduler lee contenidos correctamente
2. [ ] Crea publicaciones (una por plataforma)
3. [ ] Calcula scheduled_time distribuido
4. [ ] Marca contenido como 'aprobado'
5. [ ] Idempotencia funciona (no duplica)
6. [ ] Límites respetados (MAX_SAME_VIDEO, 3 videos/día)
7. [ ] Poster puede leer y publicar las publicaciones creadas

---

**Diseño completado. Esperando aprobación para implementar.**



