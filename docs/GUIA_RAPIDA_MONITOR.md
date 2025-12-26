# 🚀 Guía Rápida - Primera Prueba con Monitor de Descargas

## ⚡ TL;DR (Inicio Ultra Rápido)

```bash
# 1. Ir al proyecto
cd /home/victor/100-trafico/100trafico

# 2. Activar entorno virtual
source ../.venv/bin/activate

# 3. Verificar que todo esté listo
./scripts/verificar_monitor.sh

# 4. Iniciar sistema con monitor
python scripts/start_prueba_con_monitor.py

# 5. Enviar video por Telegram
# (Abre tu bot en Telegram y envía un video)

# 6. Observar logs en tiempo real
# (El monitor mostrará todo en la terminal)

# 7. Para detener: Ctrl+C
```

---

## 📋 Respuestas a Tus Preguntas Originales

### 1️⃣ Ruta de descarga y almacenamiento

**✅ Ruta definida:**
```
/home/victor/100-trafico/100trafico/modelos/{nombre_modelo}/{timestamp}_{random}.mp4
```

**Ejemplo:**
```
modelos/victor/20251225_143020_a3f2b1.mp4
```

### 2️⃣ Formato y límites del video

- **Formato guardado:** `.mp4` (forzado por el sistema)
- **Formatos aceptados:** Cualquier video/documento que Telegram envíe
- **Tamaño máximo:** **4 GB** (con servidor local)
- **Sin servidor local:** 20 MB máximo

### 3️⃣ Agente de monitoreo

**✅ Implementado:** Watchdog en tiempo real

- Detecta errores en logs automáticamente
- Ejecuta acciones correctivas
- Notifica al admin vía Telegram
- Registra todo en JSON

### 4️⃣ Errores típicos esperados

El monitor detecta y maneja:

1. ✅ **Timeout de descarga** (más común)
2. ✅ **Problemas de permisos** (frecuente)
3. ✅ **Ruta inexistente** (auto-corregible)
4. ✅ **Archivo corrupto** (recuperable)
5. ✅ **Disco lleno** (crítico)
6. ✅ **Servidor local caído** (crítico)

### 5️⃣ Acciones correctivas

**El agente:**

- ✅ Reintenta descargas automáticamente (hasta 3 veces)
- ✅ Crea carpetas si faltan
- ✅ Limpia archivos corruptos
- ✅ Corrige permisos con sudo
- ✅ Notifica errores críticos
- ✅ Loggea todo (JSON + terminal)

### 6️⃣ Integración con el pipeline

**Flujo completo:**

```
Video Telegram → Bot descarga → [Monitor supervisa] 
                      ↓
                 ¿Error? → [Monitor corrige]
                      ↓
              Caption IA → BD → Poster (cada 60s)
```

**El monitor garantiza que el video llegue correctamente al disco.**
Después de eso, el pipeline continúa normalmente.

---

## 🎯 Casos de Uso

### Caso 1: Primera Prueba Completa ⭐

```bash
# Terminal 1
cd /home/victor/100-trafico/100trafico
source ../.venv/bin/activate
python scripts/start_prueba_con_monitor.py

# Telegram
# Enviar 3-5 videos de diferentes tamaños

# Observar
# - Terminal muestra eventos en tiempo real
# - Verificar que no haya errores
# - Si hay errores, ver cómo el monitor los corrige

# Al terminar: Ctrl+C

# Revisar logs
cat logs/descarga_errors.json
cat logs/monitor.log
```

### Caso 2: Debug de Problema Específico

```bash
# Si tienes un problema recurrente con descargas

# Limpiar logs anteriores
rm logs/*.json logs/*.log

# Iniciar con monitor
python scripts/start_prueba_con_monitor.py

# Reproducir el problema
# (Enviar el video que falla)

# Revisar qué detectó el monitor
cat logs/descarga_errors.json | python -m json.tool
```

### Caso 3: Prueba de Carga (Muchos Videos)

```bash
# Iniciar monitor
python scripts/start_prueba_con_monitor.py

# Enviar múltiples videos seguidos
# (5-10 videos de diferentes tamaños)

# Verificar que:
# - Todos se descarguen correctamente
# - No haya cuellos de botella
# - El monitor registre todos los eventos

# Analizar resultados
cat logs/monitor.log | grep "✅\|❌"
```

---

## 📁 Archivos Importantes

### Ejecutables
- `scripts/start_prueba_con_monitor.py` - Inicia todo automáticamente
- `workers/monitor_descarga.py` - Monitor standalone
- `scripts/verificar_monitor.sh` - Verificación pre-vuelo

### Documentación
- `docs/MONITOR_DESCARGAS.md` - Documentación completa (⭐ léelo)
- `workers/README_MONITOR.md` - Referencia rápida
- `CHANGELOG_MONITOR.md` - Historial de cambios

### Logs (se crean al ejecutar)
- `logs/descarga_errors.json` - Errores estructurados
- `logs/monitor.log` - Log completo del monitor
- `logs/bot_central.log` - Log del bot (monitoreado)

---

## 🔧 Comandos Útiles

### Verificar Estado

```bash
# Verificar que todo esté listo
./scripts/verificar_monitor.sh

# Ver procesos corriendo
ps aux | grep -E "main.py|monitor_descarga"

# Ver servidor Telegram local
docker ps | grep telegram-bot-api
```

### Ver Logs

```bash
# Log del monitor en tiempo real
tail -f logs/monitor.log

# Errores en formato bonito
cat logs/descarga_errors.json | python -m json.tool

# Solo errores críticos
cat logs/monitor.log | grep "❌\|🚨"

# Contar errores por tipo
cat logs/descarga_errors.json | jq -r '.[].error_type' | sort | uniq -c
```

### Limpiar y Reiniciar

```bash
# Detener todo
pkill -f "main.py|monitor_descarga"

# Limpiar logs
rm logs/*.log logs/*.json

# Reiniciar limpio
python scripts/start_prueba_con_monitor.py
```

---

## ⚠️ Troubleshooting Rápido

### No inicia el monitor

```bash
# Verificar dependencias
pip install python-telegram-bot>=20.8 python-dotenv

# Verificar Python
python3 --version  # Debe ser 3.10+
```

### No recibo notificaciones Telegram

```bash
# Verificar .env
cat src/.env | grep -E "TELEGRAM_TOKEN|ADMIN_ID"

# Debe contener:
# TELEGRAM_TOKEN=123456...
# ADMIN_ID=123456789
```

### Errores de permisos

```bash
# Corregir propietario de archivos
sudo chown -R $USER:$USER modelos/
sudo chown -R $USER:$USER logs/

# Configurar sudo sin contraseña (opcional)
echo "$USER ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/$USER
```

### Servidor Telegram local no corre

```bash
# Ver logs del contenedor
docker logs telegram-bot-api

# Reiniciar
docker restart telegram-bot-api

# O iniciarlo si no existe
./scripts/start_local_bot_api.sh
```

---

## 📊 ¿Qué Esperar Durante la Prueba?

### ✅ Escenario Ideal (Sin Errores)

```
[14:30:15] 👀 Iniciando monitoreo de logs...
[14:30:20] [MAIN] 🤖 Iniciando Bot Central...
[14:30:25] [MAIN] ✅ Bot corriendo
[14:31:00] [MAIN] 📥 Video recibido de victor
[14:31:05] [MAIN] ⏬ Descargando: 250 MB
[14:31:45] [MAIN] ✅ Descarga completa: 20251225_143120_f3a1b2.mp4
[14:32:00] [MAIN] 🎨 Generando caption con Gemini...
[14:32:05] [MAIN] ✅ Caption generado
[14:32:10] [MAIN] 💾 Contenido guardado en BD
```

### ⚠️ Escenario con Error Recuperable

```
[14:30:15] 👀 Iniciando monitoreo de logs...
[14:31:00] [MAIN] 📥 Video recibido
[14:31:30] ⚠️  Error detectado: timeout
[14:31:30] 🔧 Ejecutando corrección para timeout (intento 1/3)
[14:31:31] ⏳ Esperando 1s antes de reintentar...
[14:31:32] 🔄 Reintentando descarga (intento 2)...
[14:32:00] [MAIN] ✅ Descarga completa
[14:32:05] ✅ Error solucionado automáticamente
```

### 🚨 Escenario Crítico

```
[14:30:15] 👀 Iniciando monitoreo de logs...
[14:31:00] [MAIN] 📥 Video recibido
[14:31:30] ⚠️  Error detectado: disco_lleno
[14:31:30] 🚨 ERROR CRÍTICO: Disco lleno
[14:31:30] 💾 Espacio disponible: 1.2 GB
[14:31:35] 📬 Notificación enviada al admin
```

---

## 🎓 Tips Pro

### 1. Monitoreo Dual

```bash
# Terminal 1: Sistema con monitor
python scripts/start_prueba_con_monitor.py

# Terminal 2: Ver logs JSON en tiempo real
watch -n 1 'cat logs/descarga_errors.json | python -m json.tool | tail -20'
```

### 2. Simular Errores (Testing)

```bash
# Llenar disco (cuidado!)
# dd if=/dev/zero of=/tmp/testfile bs=1G count=10

# Romper permisos
# chmod 000 modelos/victor/

# Detener servidor Telegram
# docker stop telegram-bot-api
```

### 3. Análisis Post-Prueba

```bash
# Resumen de errores
jq -r '.[].error_type' logs/descarga_errors.json | sort | uniq -c

# Videos procesados
ls -lh modelos/victor/*.mp4

# Timeline completo
cat logs/monitor.log | grep -E "\[.*\]" | sort
```

---

## 📱 Notificaciones en Telegram

Durante la prueba, recibirás notificaciones como:

**Inicio:**
```
✅ Monitor de descargas iniciado

Supervisando el pipeline de videos en tiempo real.
```

**Error recuperable:**
```
⚠️ Monitor de Descargas

Error de timeout detectado
Modelo: victor
Video: 20251225_143020_a3f2b1.mp4
Reintentando automáticamente...
```

**Error crítico:**
```
🚨 Monitor de Descargas

ERROR CRÍTICO: Disco lleno

Solo 1.2 GB libres.
Limpia archivos antiguos urgentemente.
```

**Finalización:**
```
🛑 Monitor de descargas detenido

Errores detectados: 3
Logs disponibles en: `logs/descarga_errors.json`
```

---

## 🎯 Checklist Pre-Vuelo

Antes de iniciar la prueba, verifica:

- [ ] Entorno virtual activado
- [ ] `./scripts/verificar_monitor.sh` sin errores críticos
- [ ] Servidor Telegram local corriendo (Docker)
- [ ] Variables `TELEGRAM_TOKEN` y `ADMIN_ID` configuradas
- [ ] Al menos 5 GB de espacio libre en disco
- [ ] Permisos correctos en carpeta `modelos/`
- [ ] Bot de Telegram responde a `/start`

**Si todo está ✅, estás listo para la prueba.**

---

## 🚀 ¡Comienza La Prueba!

```bash
cd /home/victor/100-trafico/100trafico
source ../.venv/bin/activate
python scripts/start_prueba_con_monitor.py
```

**¡Mucha suerte! 🍀**

---

## 📞 Ayuda

- **Documentación completa:** `docs/MONITOR_DESCARGAS.md`
- **Preguntas:** Revisa el CHANGELOG y los comentarios en código
- **Issues:** Revisa los logs en `logs/`

---

_Guía generada el 25 de diciembre de 2025_  
_Sistema: 100-Tráfico - Monitor de Descargas v1.0.0-prueba_


