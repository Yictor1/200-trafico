# 🔍 Monitor de Descargas - Referencia Rápida

## ¿Qué es?

Agente de monitoreo en tiempo real que supervisa la descarga de videos desde Telegram, detecta errores y ejecuta acciones correctivas automáticas.

## Inicio Rápido

```bash
# Desde la raíz del proyecto
cd /home/victor/100-trafico/100trafico

# Opción 1: Script automático (recomendado)
python scripts/start_prueba_con_monitor.py

# Opción 2: Solo el monitor
python workers/monitor_descarga.py
```

## ¿Qué Detecta?

| Error | Acción |
|-------|--------|
| Timeout | Reintenta 3 veces con delays: 1s → 2s → 4s |
| Ruta inexistente | Crea carpeta automáticamente |
| Archivo corrupto | Elimina y reintenta |
| Permisos | Ejecuta `sudo chown` |
| Disco lleno | Alerta crítica al admin |
| Servidor caído | Verifica y notifica |

## Logs

- **Terminal**: Output en tiempo real con timestamps
- **JSON**: `logs/descarga_errors.json` (estructurado)
- **Monitor**: `logs/monitor.log` (completo)

## Notificaciones

Envía alertas vía Telegram al admin configurado en `src/.env`:

```bash
TELEGRAM_TOKEN=tu_token
ADMIN_ID=tu_user_id
```

## Documentación Completa

Ver: `docs/MONITOR_DESCARGAS.md`

## PRD

Este agente implementa el PRD: **Agente de Monitoreo de Descargas (Primera Prueba)**

Objetivo: Garantizar que el pipeline funcione correctamente durante la primera prueba del sistema.

---

**Estado**: ✅ Implementado y listo para prueba  
**Versión**: 1.0.0-prueba  
**Fecha**: 25 de diciembre de 2025


