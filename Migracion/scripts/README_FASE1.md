# FASE 1: Ejecutar Creación de Esquema PRD

Este directorio contiene los scripts para crear el esquema de base de datos según el PRD.

## Archivos

- `fase1_create_prd_schema.sql` - Script SQL completo con todas las tablas, índices y triggers
- `execute_fase1_node.js` - Script Node.js para ejecutar el SQL usando MCP
- `execute_fase1.py` - Script Python alternativo (requiere psycopg2)

## Método Recomendado: Consola SQL de Supabase

La forma más confiable es ejecutar el SQL directamente en la consola SQL de Supabase:

### Pasos:

1. Abre el Dashboard de Supabase: https://supabase.com/dashboard
2. Selecciona tu proyecto
3. Ve a **SQL Editor** (menú lateral)
4. Crea una nueva query
5. Copia y pega el contenido completo de `fase1_create_prd_schema.sql`
6. Ejecuta el script (botón "Run" o Ctrl+Enter)

### Verificación:

Después de ejecutar, verifica que las tablas se crearon:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('modelos', 'plataformas', 'cuentas_plataforma', 'contenidos', 'publicaciones', 'eventos_sistema')
ORDER BY table_name;
```

Deberías ver 6 tablas.

## Método Alternativo: Script Node.js

Si tienes configurado MCP con Supabase:

```bash
cd Migracion/scripts
node execute_fase1_node.js
```

**Requisitos:**
- Variables de entorno: `SUPABASE_URL` o `SUPABASE_PROJECT_REF`
- Opcional: `SUPABASE_ACCESS_TOKEN` (si está configurado)

## Método Alternativo: Script Python

Si tienes `psycopg2` instalado:

```bash
cd Migracion/scripts
python3 execute_fase1.py
```

**Requisitos:**
- `psycopg2-binary` instalado: `pip install psycopg2-binary`
- Variable de entorno: `SUPABASE_DB_PASSWORD` en `.env`

## Qué Hace Este Script

1. Crea 3 tipos ENUM:
   - `estado_modelo` (activa, pausada, en_prueba)
   - `estado_contenido` (nuevo, aprobado, rechazado, reutilizable)
   - `estado_publicacion` (programada, procesando, publicado, fallido)

2. Crea función `update_updated_at_column()` para triggers automáticos

3. Crea 6 tablas:
   - `modelos` - Modelos webcam
   - `plataformas` - Plataformas de publicación
   - `cuentas_plataforma` - Cuentas de modelos en plataformas
   - `contenidos` - Videos y contenido recibido
   - `publicaciones` - Publicaciones programadas y ejecutadas
   - `eventos_sistema` - Auditoría y eventos

4. Crea índices críticos para optimizar queries del poster/scheduler

5. Crea triggers para actualizar `updated_at` automáticamente

## Importante

- ✅ **NO elimina** las tablas antiguas
- ✅ **NO migra** datos (eso es FASE 2)
- ✅ Las tablas nuevas **conviven** con las antiguas
- ✅ El sistema actual **sigue funcionando** sin cambios

## Próximos Pasos

Una vez completada FASE 1, puedes proceder con:
- **FASE 2**: Migración de datos desde tablas dinámicas al nuevo esquema
- **FASE 3**: Migración del código (poster, bot, etc.) para usar el nuevo esquema



