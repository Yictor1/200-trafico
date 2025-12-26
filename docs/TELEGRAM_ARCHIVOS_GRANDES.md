# Telegram Bot API - Archivos Grandes (>50MB)

## Solución Definitiva (2GB)

Para habilitar la descarga de archivos de hasta **2000 MB (2 GB)**, se utiliza un servidor local de Telegram Bot API.

### 1. Servidor Local

El servidor local ya está configurado y corriendo en Docker en el puerto `8081`.

Para verificar su estado:
```bash
docker ps | grep telegram-bot-api
```

Si no está corriendo, inícialo con:
```bash
cd /home/victor/Escritorio/SkyFlow_Porn-master/100-trafico
./scripts/start_local_bot_api.sh
```

### 2. Configuración del Bot

El bot (`bot_central.py`) ha sido configurado para usar este servidor local mediante las opciones `base_url` y `local_mode`:

```python
app = (
    Application.builder()
    .token(TOKEN)
    .base_url("http://127.0.0.1:8081/bot")
    .local_mode(True)  # ✅ NECESARIO cuando el servidor usa --local
    .build()
)
```

### 3. Funcionamiento

1. El bot recibe el archivo.
2. Solicita `getFile` al servidor local.
3. El servidor local (configurado con `--local`) responde con **rutas del sistema de archivos**.
4. `python-telegram-bot` con `local_mode=True` copia el archivo desde la ruta local.

**Importante:**
- `local_mode=True` **ES NECESARIO** cuando el servidor usa la flag `--local`
- Se requieren permisos de lectura en `~/.telegram-bot-api/` (777 recomendado)
- El bot mapea rutas del contenedor al host automáticamente

### Estado Actual

✅ **Sistema listo para archivos de hasta 2 GB.**
