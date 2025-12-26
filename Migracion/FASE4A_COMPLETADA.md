# ✅ FASE 4A: Migración del Bot Telegram - Completada

**Fecha:** 2025-01-XX  
**Estado:** ✅ Completado y validado

## Resumen

FASE 4A ha sido completada exitosamente. El bot de Telegram (`bot_central.py`) ha sido refactorizado para crear contenidos en el esquema PRD en lugar de usar tablas dinámicas.

## Objetivo Cumplido

✅ **El bot ahora crea registros en `contenidos`**  
✅ **NO crea publicaciones** (eso es FASE 4B)  
✅ **NO usa tablas dinámicas**  
✅ **Idempotencia básica implementada**  
✅ **Logging claro**  

## Archivos Modificados

### Nuevos archivos creados:
- **`100trafico/src/database/contenidos_prd.py`** - Módulo para crear y gestionar contenidos en PRD

### Archivos modificados:
- **`100trafico/src/project/bot_central.py`** - Refactorizado para usar esquema PRD

## Cambios Implementados

### 1. Nuevo Módulo: `contenidos_prd.py`

**Funciones principales:**

#### `get_modelo_id_by_nombre(modelo_nombre: str) -> Optional[str]`
- Obtiene el UUID del modelo por su nombre (slug)
- Retorna `None` si el modelo no existe

#### `create_contenido(...) -> Optional[str]`
- Crea un contenido en la tabla `contenidos`
- **Idempotencia**: Verifica si ya existe antes de crear
- Campos guardados:
  - `modelo_id` (FK a modelos)
  - `archivo_path` (ej: "modelos/{modelo}/{video}")
  - `contexto_original` (qué vendes, outfit, etc.)
  - `enviado_por` (telegram_user_id)
  - `estado` = 'nuevo'
  - `recibido_at` (timestamp automático)
  - `caption_generado` (opcional)
  - `tags_generados` (opcional, array)

#### `update_contenido_caption_tags(...) -> bool`
- Actualiza caption y tags de un contenido existente
- Útil cuando el caption se genera después de crear el contenido

### 2. Refactorización del Bot

**Flujo anterior:**
```
1. Recibir video
2. Guardar metadata JSON
3. generate_and_update() → inserta en tabla dinámica
4. plan() → scheduler
5. update_schedule_time() → actualiza tabla dinámica
```

**Flujo nuevo (FASE 4A):**
```
1. Recibir video
2. Guardar metadata JSON
3. create_contenido() → crea en tabla contenidos (PRD)
4. generate_caption_and_tags() → genera caption/tags
5. update_contenido_caption_tags() → actualiza contenido
6. NO crear publicaciones (FASE 4B)
7. NO llamar a scheduler (FASE 4B)
```

**Cambios específicos en `bot_central.py`:**

1. **Importación del nuevo módulo:**
```python
from database.contenidos_prd import create_contenido, update_contenido_caption_tags
```

2. **Creación de contenido antes de generar caption:**
```python
contenido_id = create_contenido(
    modelo_nombre=modelo,
    archivo_path=f"modelos/{modelo}/{video_nombre}",
    contexto_original=contexto_original,
    enviado_por=f"telegram_{user.id}"
)
```

3. **Generación de caption sin insertar en tabla dinámica:**
```python
from caption import generate_caption_and_tags  # Directo, sin generate_and_update
result = generate_caption_and_tags(modelo, meta_path)
```

4. **Actualización del contenido con caption/tags:**
```python
update_contenido_caption_tags(
    contenido_id=contenido_id,
    caption_generado=result.caption,
    tags_generados=result.tags
)
```

5. **Eliminación de código antiguo:**
   - ❌ Removido: `generate_and_update()` (insertaba en tabla dinámica)
   - ❌ Removido: `plan()` (scheduler)
   - ❌ Removido: `update_schedule_time()` (actualizaba tabla dinámica)

## Idempotencia

**Implementación:**
- Antes de crear, verifica si ya existe un contenido con mismo `modelo_id` + `archivo_path`
- Si existe, retorna el ID existente (no duplica)
- Si no existe, crea nuevo y retorna su ID

**Query de verificación:**
```python
existing = supabase.table('contenidos')\
    .select("id")\
    .eq('modelo_id', modelo_id)\
    .eq('archivo_path', archivo_path)\
    .execute()
```

## Logging

**Niveles de logging:**
- ✅ `logger.info()`: Operaciones exitosas
- ℹ️  `logger.info()`: Elementos que ya existen (idempotencia)
- ⚠️  `logger.warning()`: Advertencias (modelo no encontrado, etc.)
- ❌ `logger.error()`: Errores con traceback

**Ejemplos:**
```
✅ Contenido creado: modelos/test/video.mp4 (ID: uuid)
ℹ️  Contenido ya existe: modelos/test/video.mp4 (ID: uuid)
❌ Error creando contenido: ...
```

## Validaciones Realizadas

✅ **Compilación**: Scripts compilan sin errores  
✅ **Importación**: Funciones importan correctamente  
✅ **Creación de contenido**: Funciona correctamente  
✅ **Idempotencia**: No duplica contenidos  
✅ **Actualización**: Caption y tags se actualizan correctamente  
✅ **Campos**: Todos los campos se guardan correctamente  

## Test de Validación

**Archivo:** `Migracion/scripts/test_bot_contenidos.py`

**Tests incluidos:**
1. ✅ `get_modelo_id_by_nombre()` funciona
2. ✅ `create_contenido()` sin caption/tags funciona
3. ✅ Idempotencia funciona (no duplica)
4. ✅ `create_contenido()` con caption/tags funciona
5. ✅ `update_contenido_caption_tags()` funciona

**Resultado:** Todos los tests pasan ✅

## Comparación: Antes vs Ahora

| Aspecto | Antes | Ahora (FASE 4A) |
|---------|-------|-----------------|
| **Tabla usada** | Tabla dinámica `[modelo]` | `contenidos` (PRD) |
| **Relaciones** | No hay relaciones | FK a `modelos` |
| **Estado inicial** | `pendiente` | `nuevo` |
| **Publicaciones** | Se crean inmediatamente | NO se crean (FASE 4B) |
| **Scheduler** | Se llama inmediatamente | NO se llama (FASE 4B) |
| **Idempotencia** | No implementada | Implementada |
| **Trazabilidad** | Limitada | Completa (FKs, timestamps) |

## Flujo Completo del Bot (FASE 4A)

1. **Usuario envía video** → `video_handler()`
2. **Bot descarga video** → Guarda en `modelos/{modelo}/{timestamp}_{random}.mp4`
3. **Usuario selecciona qué vendes y outfit** → `callback_handler()`
4. **Bot procesa video:**
   - Guarda metadata JSON
   - **Crea contenido en PRD** (`create_contenido()`)
   - Genera caption y tags (`generate_caption_and_tags()`)
   - Actualiza contenido con caption/tags (`update_contenido_caption_tags()`)
5. **Bot confirma al usuario** → "Contenido creado. Las publicaciones se programarán después."

## Regla de Oro Cumplida

✅ **Un solo productor → una sola tabla PRD → un solo consumidor**

- **Productor**: Bot Telegram (`bot_central.py`)
- **Tabla PRD**: `contenidos`
- **Consumidor**: (FASE 4B - scheduler que creará publicaciones)

## Próximos Pasos (FASE 4B)

1. **Refactorizar Scheduler**
   - Leer contenidos con `estado='nuevo'` o `estado='aprobado'`
   - Crear `publicaciones` en lugar de actualizar tabla dinámica
   - Usar `cuentas_plataforma` para obtener plataformas por modelo

2. **Flujo completo:**
   ```
   Bot → contenidos (estado='nuevo')
   ↓
   Scheduler → lee contenidos → crea publicaciones
   ↓
   Poster → lee publicaciones → publica
   ```

## Checklist de Validación Manual

### Test 1: Enviar Video desde Telegram

1. Enviar video al bot
2. Seleccionar qué vendes y outfit
3. Procesar video
4. Verificar:
   - [ ] Contenido creado en tabla `contenidos`
   - [ ] `estado` = 'nuevo'
   - [ ] `archivo_path` correcto
   - [ ] `contexto_original` tiene qué vendes y outfit
   - [ ] `enviado_por` tiene telegram_user_id
   - [ ] `caption_generado` tiene caption
   - [ ] `tags_generados` tiene tags

### Test 2: Idempotencia

1. Enviar mismo video dos veces
2. Verificar:
   - [ ] No se crean dos contenidos
   - [ ] Se retorna el mismo ID
   - [ ] Log muestra "Contenido ya existe"

### Test 3: Modelo No Existe

1. Enviar video con modelo que no existe en PRD
2. Verificar:
   - [ ] Error claro en logs
   - [ ] Bot informa al usuario del error
   - [ ] No se crea contenido

## Notas Técnicas

### Decisiones de Diseño

1. **Crear contenido antes de generar caption**: Asegura que el contenido existe aunque falle la generación de caption

2. **Actualizar caption/tags después**: Permite generar caption de forma asíncrona si es necesario

3. **No crear publicaciones**: Separación de responsabilidades. El bot solo crea contenidos, el scheduler crea publicaciones

4. **Mantener metadata JSON local**: Compatibilidad con código existente y backup

### Límites Conocidos

- El bot aún guarda metadata JSON local (compatibilidad)
- No hay validación de que el archivo existe en filesystem (se asume que sí)
- No hay límite de tamaño de `contexto_original` (debería ser suficiente para texto)

---

**FASE 4A: ✅ COMPLETADA Y VALIDADA**  
**Siguiente: FASE 4B - Migración del Scheduler**



