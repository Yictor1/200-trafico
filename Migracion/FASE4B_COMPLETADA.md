# ✅ FASE 4B: Scheduler PRD - Completada

**Fecha:** 2025-01-XX  
**Estado:** ✅ Completado y validado

## Resumen

FASE 4B ha sido completada exitosamente. El scheduler PRD lee contenidos y crea publicaciones en el esquema PRD, completando el flujo: Bot → Contenidos → Scheduler → Publicaciones → Poster.

## Objetivo Cumplido

✅ **Lee contenidos desde tabla `contenidos`**  
✅ **Crea publicaciones en tabla `publicaciones`**  
✅ **NO usa tablas dinámicas**  
✅ **NO publica nada (solo crea publicaciones)**  
✅ **Idempotencia estricta implementada**  
✅ **Procesa solo contenidos con estado = 'nuevo'**  
✅ **Marca contenido como 'aprobado' solo si todas las publicaciones se crean correctamente**  

## Archivos Creados

### Nuevo archivo:
- **`100trafico/src/project/scheduler_prd.py`** - Scheduler refactorizado para esquema PRD

### Tests:
- **`Migracion/scripts/test_scheduler_prd.py`** - Tests mínimos
- **`Migracion/scripts/test_scheduler_poster_e2e.py`** - Test end-to-end

## Cambios Implementados

### 1. Lectura de Contenidos

**Query:**
```python
contenidos = supabase.table('contenidos')\
    .select("*, modelos(*)")\
    .eq('estado', 'nuevo')\
    .order('recibido_at', desc=False)\
    .execute()
```

**Características:**
- Solo procesa contenidos con `estado = 'nuevo'`
- Join automático con `modelos` para obtener configuración
- Ordenado por `recibido_at` (más antiguos primero)

### 2. Idempotencia Estricta

**Verificación:**
```python
existing = supabase.table('publicaciones')\
    .select("id")\
    .eq('contenido_id', contenido_id)\
    .in_('estado', ['programada', 'procesando', 'publicado'])\
    .execute()
```

**Regla:**
- Si ya existen publicaciones → saltar contenido (ya procesado)
- Si no existen → continuar con procesamiento

### 3. Obtención de Cuentas Plataforma

**Query:**
```python
cuentas = supabase.table('cuentas_plataforma')\
    .select("id, plataforma_id, plataformas!inner(nombre, activa)")\
    .eq('modelo_id', modelo_id)\
    .execute()
```

**Filtros:**
- Solo plataformas activas
- Solo plataformas en `configuracion_distribucion.plataformas`
- Si no hay cuentas válidas → saltar contenido (log warning)

### 4. Cálculo de Scheduled Time

**Lógica heredada del scheduler antiguo:**
- Usa `_build_slots_for_day()` para distribuir slots
- Respeta `MIN_GAP_MINUTES = 10`
- Busca desde hoy hasta `MAX_DAYS_AHEAD = 30` días
- Máximo 3 videos distintos por día
- Máximo 6 apariciones del mismo contenido (`MAX_SAME_VIDEO`)

**Adaptación para PRD:**
- Lee de `publicaciones` en lugar de tabla dinámica
- Agrupa por fecha para contar videos distintos
- Agrupa por `contenido_id` para contar apariciones

### 5. Creación de Publicaciones

**Por cada cuenta_plataforma:**
```python
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

### 6. Actualización de Estado

**Solo si todas las publicaciones se crean exitosamente:**
```python
supabase.table('contenidos')\
    .update({"estado": "aprobado"})\
    .eq('id', contenido_id)\
    .execute()
```

**Regla:**
- Si hay cualquier error parcial → NO cambiar estado
- Contenido permanece en `'nuevo'` para reintento

## Funciones Principales

1. **`get_pending_contenidos()`** → Lista contenidos con estado 'nuevo'
2. **`check_idempotencia(contenido_id)`** → Verifica si ya tiene publicaciones
3. **`check_limits(contenido_id)`** → Verifica límites (MAX_SAME_VIDEO)
4. **`get_cuentas_plataforma(modelo_id, plataformas)`** → Obtiene cuentas válidas
5. **`calculate_scheduled_times(...)`** → Calcula slots distribuidos
6. **`create_publicaciones(...)`** → Crea publicaciones
7. **`update_contenido_estado(...)`** → Marca contenido como aprobado
8. **`process_contenido(contenido)`** → Procesa un contenido completo
9. **`main()`** → Loop principal

## Validaciones Realizadas

✅ **Compilación**: Script compila sin errores  
✅ **Tests mínimos**: Todos los tests pasan  
✅ **Idempotencia**: No duplica publicaciones  
✅ **Límites**: Respeta MAX_SAME_VIDEO  
✅ **Sin cuentas**: No crea publicaciones si no hay cuentas válidas  
✅ **Flujo completo**: Scheduler → Poster funciona end-to-end  

## Tests Implementados

### Test 1: 1 contenido → N publicaciones
- ✅ Crea N publicaciones (una por plataforma)
- ✅ Marca contenido como 'aprobado'

### Test 2: Idempotencia
- ✅ Doble ejecución no duplica publicaciones
- ✅ Contenido sigue en 'aprobado'

### Test 3: Límites
- ✅ Respeta MAX_SAME_VIDEO
- ✅ No procesa si alcanzó tope

### Test 4: Sin cuentas válidas
- ✅ No crea publicaciones
- ✅ Contenido sigue en 'nuevo'

### Test 5: End-to-End
- ✅ Scheduler crea publicaciones
- ✅ Poster puede leer publicaciones
- ✅ Joins funcionan correctamente

## Flujo Completo

```
1. Bot Telegram → crea contenido (estado='nuevo')
   ↓
2. Scheduler PRD → lee contenidos (estado='nuevo')
   ↓
3. Scheduler PRD → crea publicaciones (estado='programada')
   ↓
4. Scheduler PRD → marca contenido (estado='aprobado')
   ↓
5. Poster PRD → lee publicaciones (estado='programada', scheduled_time <= now())
   ↓
6. Poster PRD → publica → marca publicación (estado='publicado')
```

## Comparación: Antes vs Ahora

| Aspecto | Antes (scheduler.py) | Ahora (scheduler_prd.py) |
|---------|---------------------|-------------------------|
| **Tabla fuente** | Tabla dinámica `[modelo]` | `contenidos` (PRD) |
| **Tabla destino** | Tabla dinámica `[modelo]` | `publicaciones` (PRD) |
| **Relaciones** | No hay relaciones | FKs a modelos, contenidos, cuentas |
| **Idempotencia** | No implementada | Implementada |
| **Estados** | `pendiente` → `publicado` | `nuevo` → `aprobado` (contenido) |
| **Cuentas** | No valida cuentas | Valida cuentas_plataforma |
| **Configuración** | Lee de tabla modelos antigua | Lee de modelos.configuracion_distribucion |

## Uso

### Ejecutar scheduler:

```bash
cd /home/victor/100-trafico
source .venv/bin/activate
python3 100trafico/src/project/scheduler_prd.py
```

### Variables de entorno:

```bash
MIN_GAP_MINUTES=10      # Mínimo entre publicaciones
MAX_DAYS_AHEAD=30       # Días a buscar adelante
MAX_SAME_VIDEO=6        # Máximo apariciones del mismo contenido
```

## Checklist de Validación Manual

### Test 1: Crear Contenido → Publicaciones

1. [ ] Crear contenido con estado 'nuevo' (vía bot o manualmente)
2. [ ] Ejecutar `scheduler_prd.py`
3. [ ] Verificar:
   - [ ] Se crearon N publicaciones (una por plataforma)
   - [ ] Publicaciones tienen `estado='programada'`
   - [ ] Publicaciones tienen `scheduled_time` calculado
   - [ ] Contenido marcado como `estado='aprobado'`

### Test 2: Idempotencia

1. [ ] Ejecutar scheduler dos veces seguidas
2. [ ] Verificar:
   - [ ] Segunda ejecución no crea publicaciones duplicadas
   - [ ] Contenido sigue en `estado='aprobado'`
   - [ ] Log muestra "Contenido ya tiene publicaciones"

### Test 3: Límites

1. [ ] Crear contenido con 6 publicaciones existentes
2. [ ] Ejecutar scheduler
3. [ ] Verificar:
   - [ ] Contenido no procesado
   - [ ] Log muestra "alcanzó tope (MAX_SAME_VIDEO=6)"

### Test 4: Sin Cuentas Válidas

1. [ ] Crear contenido con modelo sin cuentas_plataforma
2. [ ] Ejecutar scheduler
3. [ ] Verificar:
   - [ ] No se crearon publicaciones
   - [ ] Contenido sigue en `estado='nuevo'`
   - [ ] Log muestra warning "No hay cuentas_plataforma válidas"

### Test 5: Flujo Completo con Poster

1. [ ] Crear contenido (estado='nuevo')
2. [ ] Ejecutar scheduler → crear publicaciones
3. [ ] Actualizar `scheduled_time` a pasado
4. [ ] Ejecutar `poster_prd.py`
5. [ ] Verificar:
   - [ ] Poster encuentra publicaciones
   - [ ] Poster puede procesar publicaciones
   - [ ] Joins funcionan correctamente

## Notas Técnicas

### Decisiones de Diseño

1. **Solo procesa estado='nuevo'**: Evita reprocesar contenidos ya procesados
2. **Idempotencia estricta**: Verifica publicaciones existentes antes de crear
3. **Actualización condicional**: Solo marca 'aprobado' si todo fue exitoso
4. **Reutilización de lógica**: Hereda `_build_slots_for_day()` del scheduler antiguo
5. **Adaptación a PRD**: Lee de `publicaciones` en lugar de tabla dinámica

### Límites Conocidos

- No hay retry automático si falla creación de publicaciones
- No hay límite de tiempo para buscar slots (busca hasta MAX_DAYS_AHEAD)
- No valida que el archivo existe en filesystem (se asume que sí)

## Próximos Pasos

Una vez validado FASE 4B:

1. **Eliminar código antiguo**: Remover `scheduler.py` y código relacionado
2. **Actualizar documentación**: Actualizar flujos en docs
3. **Monitoreo**: Agregar métricas y alertas
4. **Optimizaciones**: Considerar procesamiento en batch

---

**FASE 4B: ✅ COMPLETADA Y VALIDADA**  
**Flujo completo: Bot → Contenidos → Scheduler → Publicaciones → Poster**



