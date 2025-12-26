# FASE 2: Migración de Datos

Script de migración de datos desde tablas dinámicas al esquema PRD.

## Características

✅ **Idempotencia real**: Puede ejecutarse múltiples veces sin duplicar datos  
✅ **Dry-run obligatorio**: Muestra conteos antes de modificar nada  
✅ **Validación de conteos**: Aborta si los conteos no cuadran  
✅ **Logging detallado**: Registra cada paso y error  

## Uso

### 1. Dry-run (obligatorio primero)

```bash
cd /home/victor/100-trafico
source .venv/bin/activate
python3 Migracion/scripts/migrate_fase2.py --dry-run
```

Esto muestra:
- Cuántos modelos se migrarán
- Cuántas plataformas se crearán
- Cuántos contenidos se crearán
- Cuántas publicaciones se migrarán
- Cuántas cuentas se crearán

**No modifica nada**, solo analiza.

### 2. Ejecutar migración

```bash
python3 Migracion/scripts/migrate_fase2.py --execute
```

Esto:
1. Muestra el dry-run primero
2. Pide confirmación (debes escribir 'SI')
3. Ejecuta la migración
4. Valida conteos
5. Muestra resumen final

### 3. Verificar idempotencia

Ejecuta de nuevo:

```bash
python3 Migracion/scripts/migrate_fase2.py --execute
```

Debería mostrar:
- `0 nuevos, X existentes` para cada entidad
- No debería crear duplicados

## Qué Migra

### Modelos
- Desde tabla antigua `modelos` (columna `modelo` como PK)
- A nueva tabla `modelos` (columna `nombre` con UUID PK)
- Configuración se mueve a `configuracion_distribucion` (JSONB)

### Plataformas
- Extrae plataformas únicas de `modelos.plataformas` (string separado por comas)
- Crea registros en tabla `plataformas`

### Cuentas Plataforma
- Lee archivos `.auth/[plataforma].json` de `modelos/[modelo]/.auth/`
- Crea registros en `cuentas_plataforma` con `datos_auth` (JSONB)

### Contenidos
- Agrupa videos únicos por modelo
- Crea un `contenido` por video único
- Estado: `pendiente` → `aprobado` (asumimos que si está programado, fue aprobado)

### Publicaciones
- Migra cada registro de tabla dinámica
- Mapea estados:
  - `pendiente` → `programada`
  - `procesando` → `procesando`
  - `publicado` → `publicado`
  - `fallido` → `fallido`
- Crea cuenta automáticamente si no existe

## Validación de Conteos

El script valida que:
- `publicaciones_creadas + publicaciones_existentes = total_registros`

Si no cuadran:
- Muestra diferencia
- Aborta la migración
- No modifica datos

## Idempotencia

El script verifica existencia antes de insertar:

- **Modelos**: Busca por `nombre`
- **Plataformas**: Busca por `nombre`
- **Cuentas**: Busca por `(modelo_id, plataforma_id)`
- **Contenidos**: Busca por `(modelo_id, archivo_path)`
- **Publicaciones**: Busca por `(contenido_id, cuenta_plataforma_id, scheduled_time)`

Si existe, marca como "existente" y no duplica.

## Manejo de Errores

- Registros inválidos (sin video o plataforma) se registran como errores
- Errores no detienen la migración (continúa con los demás)
- Todos los errores se muestran al final

## Logs

El script muestra:
- ✅ Operaciones exitosas
- ℹ️  Elementos que ya existen (idempotencia)
- ⚠️  Advertencias (datos faltantes)
- ❌ Errores (con detalles)

## Estructura de Datos Antigua

### Tabla `modelos` (antigua)
```sql
- modelo (TEXT, PK)
- plataformas (TEXT) -- separadas por comas
- hora_inicio (TEXT) -- formato "HH:MM"
- ventana_horas (INTEGER)
- striphours_url (TEXT, nullable)
- striphours_username (TEXT, nullable)
```

### Tabla `[modelo]` (dinámica)
```sql
- id (SERIAL, PK)
- video (TEXT)
- caption (TEXT)
- tags (TEXT) -- separados por comas
- plataforma (TEXT)
- estado (TEXT) -- pendiente, procesando, publicado, fallido
- scheduled_time (TEXT) -- formato "YYYY-MM-DD HH:MM:SS"
```

## Estructura de Datos Nueva (PRD)

Ver `Migracion/FASE1_COMPLETADA.md` para detalles del esquema PRD.

## Troubleshooting

### "No hay modelos en la tabla antigua"
- La tabla puede tener estructura nueva (PRD)
- Verifica con: `python3 Migracion/scripts/check_existing_tables.py`

### "Tabla dinámica no existe"
- Normal si no hay datos para ese modelo
- El script continúa con los demás modelos

### "Conteos no cuadran"
- Revisa los errores mostrados
- Puede haber registros inválidos (sin video o plataforma)
- La diferencia debe ser <= número de errores

## Próximos Pasos

Después de FASE 2:
- **FASE 3**: Migrar código (poster, bot) para usar nuevo esquema
- Eliminar dependencia de tablas dinámicas
- Actualizar queries para usar relaciones PRD



