# 🧯 Troubleshooting — 100-Tráfico

## 1. Problemas con Workers
- Revisar `console.log` del Playwright.
- Revisar storageState (puede haberse invalidado).
- Revisar perfiles persistentes en modelos/*/browser_profile.

## 2. Problemas con Scheduler
- Ver logs en terminal.
- Confirmar que la función está registrada en scheduler.py.
- Revisar si otra tarea está bloqueando el loop.

## 3. Problemas con el Bot
- Token expirado o cambiado.
- Límite de rate de Telegram.
- Archivos muy grandes no permitidos por API oficial.

## 4. KPIs caídos
- API de Striphours/CbHours caída.
- Tabla de BD mal creada.
- Scheduler no está corriendo el sync.

## 5. Panel Admin roto
- Error en servicio (service.ts) → revisar URL
- Hook mal gestionado
- Faltan tipos en shared/types/api.ts

## 6. Workers no publican
- Selector cambiado por plataforma
- Timeout insuficiente
- Antibots detectan patrón → hay que randomizar

## 7. Regla general
Siempre hacer:
1. Revisar logs
2. Revisar BD
3. Revisar router PRD
4. Revisar agentes
5. Revisar estructura de carpetas
