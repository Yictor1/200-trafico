# ✅ Verificación del Bot - Videos Grandes

## Estado Actual

### Servidor Local de Bot API
- ✅ Docker instalado y funcionando
- ✅ Contenedor `telegram-bot-api` corriendo en puerto 8081
- ✅ Configurado con credenciales de API

### Bot de Telegram
- ✅ Bot iniciado y corriendo
- ✅ Usando servidor local: `http://localhost:8081`
- ✅ Configuración cargada desde `.env`

### Configuración
- ✅ `USE_LOCAL_BOT_API=true` en `.env`
- ✅ `TELEGRAM_BOT_API_LOCAL_URL=http://localhost:8081`
- ✅ Soporte para descarga alternativa con `aiohttp`

## Límites de Archivos

- **Sin servidor local**: 20 MB máximo
- **Con servidor local**: Hasta 2 GB

## Cómo Probar

1. Envía `/start` al bot en Telegram
2. Envía un video grande (más de 20 MB)
3. El bot debería:
   - Intentar descargar con método estándar
   - Si falla por tamaño, usar descarga directa desde servidor local
   - Guardar el archivo en `modelos/{modelo}/`

## Comandos Útiles

```bash
# Ver logs del bot
tail -f logs/bot_central.log

# Ver estado del servidor local
docker ps | grep telegram-bot-api
docker logs -f telegram-bot-api

# Reiniciar el bot
pkill -f bot_central.py
cd 100-trafico
source .venv/bin/activate
python3 main.py

# Reiniciar servidor local
cd 100-trafico
./scripts/start_local_bot_api.sh
```

## Solución de Problemas

Si recibes "File is too big":
1. Verifica que el servidor local esté corriendo: `docker ps | grep telegram-bot-api`
2. Verifica la configuración en `src/.env`: `USE_LOCAL_BOT_API=true`
3. Revisa los logs: `tail -f logs/bot_central.log`
