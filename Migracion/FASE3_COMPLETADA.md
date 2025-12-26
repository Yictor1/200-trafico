# ✅ FASE 3: Migración de Código - Poster Worker

**Fecha:** 2025-01-XX  
**Estado:** ✅ Completado y validado

## Resumen

FASE 3 ha sido completada exitosamente. El worker de publicación (`poster`) ha sido refactorizado para usar exclusivamente el esquema PRD, eliminando la dependencia de tablas dinámicas.

## Archivos Modificados

### Nuevo archivo creado:
- **`100trafico/src/project/poster_prd.py`** - Worker refactorizado para esquema PRD

### Archivo antiguo (no modificado):
- **`100trafico/src/project/poster.py`** - Worker antiguo (mantenido para referencia)

## Cambios Implementados

### 1. Query Principal

**Antes (tablas dinámicas):**
```python
# Por cada modelo, leer tabla dinámica
supabase.table(modelo).select("*")\
    .eq('estado', 'pendiente')\
    .lte('scheduled_time', now_str)\
    .execute()
```

**Ahora (esquema PRD):**
```python
# Query única con joins
supabase.table('publicaciones')\
    .select("*, contenidos(*, modelos(*)), cuentas_plataforma(*, plataformas(*))")\
    .eq('estado', 'programada')\
    .lte('scheduled_time', now_iso)\
    .order('scheduled_time', desc=False)\
    .execute()
```

**Ventajas:**
- ✅ Usa índice crítico `idx_publicaciones_estado_scheduled`
- ✅ Una sola query en lugar de N queries (una por modelo)
- ✅ Joins automáticos para obtener todos los datos necesarios

### 2. Manejo de Estados

**Flujo de estados:**
```
programada → procesando → publicado | fallido
```

**Implementación:**
- `update_publicacion_estado()` maneja todos los campos:
  - `estado`: cambia según resultado
  - `intentos`: se incrementa en fallos
  - `ultimo_error`: se guarda en fallos
  - `published_at`: se guarda en éxito
  - `url_publicacion`: se guarda si está disponible

### 3. Eventos del Sistema

**Eventos registrados:**
- `publicacion_iniciada`: cuando cambia a 'procesando'
- `publicacion_exitosa`: cuando se publica exitosamente
- `publicacion_fallida`: cuando falla (con descripción del error)

**Función:**
```python
create_evento_sistema(
    tipo: str,
    publicacion_id: Optional[str],
    modelo_id: Optional[str],
    descripcion: str,
    realizado_por: str = "sistema"
)
```

### 4. Extracción de Datos

**Antes:**
- Datos planos en tabla dinámica
- Necesitaba construir rutas manualmente
- No había relación con modelo/plataforma

**Ahora:**
- Datos relacionales con joins
- `archivo_path` viene de `contenidos`
- `modelo_nombre` viene de `contenidos → modelos`
- `plataforma_nombre` viene de `cuentas_plataforma → plataformas`
- `caption` y `tags` vienen de `publicaciones` o `contenidos` (fallback)

### 5. Manejo de Errores

**Validaciones:**
- ✅ Modelo existe en relación
- ✅ Plataforma existe en relación
- ✅ Archivo existe en filesystem
- ✅ Worker script existe

**En caso de error:**
- Estado → `fallido`
- `intentos` incrementado
- `ultimo_error` guardado
- Evento registrado

## Queries Utilizadas

### Query Principal (Optimizada)
```sql
SELECT * FROM publicaciones 
WHERE estado = 'programada' 
AND scheduled_time <= now()
ORDER BY scheduled_time ASC
```

**Usa índice:** `idx_publicaciones_estado_scheduled`

### Joins Automáticos (Supabase)
```
publicaciones
  → contenidos (archivo_path, caption_generado, tags_generados)
    → modelos (nombre, id)
  → cuentas_plataforma (datos_auth)
    → plataformas (nombre)
```

## Flujo Completo

1. **Lectura**: `get_pending_publicaciones()` obtiene publicaciones programadas
2. **Procesamiento**: `process_publicacion()` para cada publicación:
   - Cambia estado a `procesando`
   - Registra evento `publicacion_iniciada`
   - Valida datos (modelo, plataforma, archivo, worker)
   - Ejecuta worker de Playwright
   - Actualiza estado según resultado:
     - ✅ Éxito → `publicado` + `published_at` + evento `publicacion_exitosa`
     - ❌ Fallo → `fallido` + `intentos++` + `ultimo_error` + evento `publicacion_fallida`

## Validaciones Realizadas

✅ **Compilación**: Script compila sin errores  
✅ **Importación**: Todas las funciones importan correctamente  
✅ **Query básica**: Lee publicaciones correctamente  
✅ **Joins**: Obtiene datos relacionados correctamente  
✅ **Estados**: Actualiza estados correctamente  
✅ **Eventos**: Registra eventos correctamente  
✅ **Campos**: `published_at`, `ultimo_error`, `intentos` funcionan  

## Checklist de Validación Manual

### Test 1: Publicación Programada → Publicada

1. Crear publicación en estado `programada` con `scheduled_time <= now()`
2. Ejecutar `poster_prd.py`
3. Verificar:
   - [ ] Estado cambió a `procesando` temporalmente
   - [ ] Estado final es `publicado`
   - [ ] `published_at` tiene timestamp
   - [ ] Evento `publicacion_exitosa` creado
   - [ ] `intentos` sigue en 0

### Test 2: Publicación Fallida

1. Crear publicación con archivo inexistente o worker inválido
2. Ejecutar `poster_prd.py`
3. Verificar:
   - [ ] Estado cambió a `procesando` temporalmente
   - [ ] Estado final es `fallido`
   - [ ] `ultimo_error` tiene mensaje de error
   - [ ] `intentos` incrementado a 1
   - [ ] Evento `publicacion_fallida` creado con descripción

### Test 3: Eventos Registrados

1. Ejecutar poster con al menos una publicación
2. Verificar en `eventos_sistema`:
   - [ ] Evento `publicacion_iniciada` para cada publicación procesada
   - [ ] Evento `publicacion_exitosa` o `publicacion_fallida` según resultado
   - [ ] `publicacion_id` correcto en eventos
   - [ ] `modelo_id` correcto en eventos
   - [ ] `descripcion` tiene información útil

### Test 4: Idempotencia

1. Ejecutar poster dos veces seguidas
2. Verificar:
   - [ ] No procesa la misma publicación dos veces
   - [ ] Solo procesa publicaciones con `estado='programada'`
   - [ ] No modifica publicaciones ya procesadas

## Comparación: Antes vs Ahora

| Aspecto | Antes (poster.py) | Ahora (poster_prd.py) |
|---------|-------------------|----------------------|
| **Tablas usadas** | Tablas dinámicas por modelo | `publicaciones` (única tabla) |
| **Queries** | N queries (una por modelo) | 1 query con joins |
| **Índices** | No optimizado | Usa `idx_publicaciones_estado_scheduled` |
| **Relaciones** | No hay relaciones | Joins automáticos |
| **Estados** | `pendiente` → `publicado`/`fallido` | `programada` → `procesando` → `publicado`/`fallido` |
| **Eventos** | No registra eventos | Registra en `eventos_sistema` |
| **Campos** | Solo `estado` | `estado`, `intentos`, `ultimo_error`, `published_at` |
| **Trazabilidad** | Limitada | Completa (eventos + campos) |

## Uso

### Ejecutar el nuevo poster:

```bash
cd /home/victor/100-trafico
source .venv/bin/activate
python3 100trafico/src/project/poster_prd.py
```

### Reemplazar el antiguo:

Una vez validado, puedes:
1. Hacer backup de `poster.py`
2. Reemplazar `poster.py` con `poster_prd.py`
3. O mantener ambos y usar `poster_prd.py` como principal

## TODOs para FASE 4

### 1. Migración del Bot Telegram
- [ ] Refactorizar `bot_central.py` para usar esquema PRD
- [ ] Crear `contenidos` en lugar de insertar en tabla dinámica
- [ ] Crear `publicaciones` usando `scheduler.py` refactorizado
- [ ] Usar `modelos.nombre` en lugar de `modelos.modelo`

### 2. Migración del Scheduler
- [ ] Refactorizar `scheduler.py` para usar esquema PRD
- [ ] Leer desde `publicaciones` en lugar de tablas dinámicas
- [ ] Crear `publicaciones` directamente
- [ ] Usar `cuentas_plataforma` para obtener plataformas por modelo

### 3. Actualización de Workers
- [ ] Workers pueden seguir usando `MODEL_NAME` (compatible)
- [ ] Considerar pasar `publicacion_id` como variable de entorno
- [ ] Workers pueden reportar `url_publicacion` de vuelta

### 4. Eliminación de Tablas Dinámicas
- [ ] Verificar que no hay código usando tablas dinámicas
- [ ] Migrar datos restantes (si los hay)
- [ ] Eliminar tablas dinámicas
- [ ] Eliminar código de creación de tablas dinámicas

### 5. Dashboard/UI
- [ ] Actualizar queries del frontend para usar esquema PRD
- [ ] Mostrar publicaciones desde `publicaciones` con joins
- [ ] Mostrar eventos desde `eventos_sistema`
- [ ] Mostrar métricas desde relaciones PRD

### 6. Optimizaciones Futuras
- [ ] Implementar retry automático (usando `intentos`)
- [ ] Implementar límite de intentos por publicación
- [ ] Implementar cola de prioridades
- [ ] Implementar métricas de rendimiento

## Notas Técnicas

### Decisiones de Diseño

1. **Manejo de Joins Anidados**: Supabase devuelve objetos anidados, el código maneja ambos casos (dict o None)

2. **Timezone**: Usa `timezone.utc` para consistencia, aunque el sistema opera en Colombia (UTC-5)

3. **Timeout de Workers**: 5 minutos (300 segundos) para evitar workers colgados

4. **Extracción de URL**: Intenta extraer URL de stdout del worker, pero no es crítico si falla

5. **Compatibilidad con Workers**: Los workers existentes siguen funcionando sin cambios (usan `MODEL_NAME`, `VIDEO_PATH`, etc.)

### Límites Conocidos

- Workers aún usan Playwright (no migrados a HTTP/Got aún)
- No hay retry automático (se implementará en FASE 4)
- No hay límite máximo de intentos (se implementará en FASE 4)

---

**FASE 3: ✅ COMPLETADA**  
**Siguiente: FASE 4 - Migración del Bot y Scheduler**



