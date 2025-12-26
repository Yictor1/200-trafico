# 🔍 Agente de Monitoreo de Descargas - Documentación Completa

## 📋 Descripción

El **Agente de Monitoreo de Descargas** es un sistema de supervisión en tiempo real que detecta, registra y corrige automáticamente errores durante el proceso de descarga y procesamiento de videos en el sistema 100-Tráfico.

Diseñado específicamente para la **primera prueba del sistema**, garantiza que el pipeline completo funcione correctamente desde la recepción del video hasta su publicación programada.

---

## ✨ Características Principales

### 🎯 Monitoreo en Tiempo Real
- Supervisa logs del bot central en tiempo real
- Detecta errores automáticamente mediante patrones
- Registra todos los eventos en formato estructurado (JSON)

### 🔧 Acciones Correctivas Automáticas
- **Timeout de descarga**: Reintento automático con backoff exponencial (1s → 2s → 4s)
- **Ruta inexistente**: Crea carpeta del modelo automáticamente
- **Archivo corrupto**: Elimina archivo y reintenta descarga
- **Problemas de permisos**: Ejecuta `sudo chown` automáticamente
- **Disco lleno**: Alerta crítica al admin
- **Servidor local caído**: Verifica y notifica estado del servidor Docker

### 📬 Notificaciones Inteligentes
- Envía alertas vía Telegram al administrador
- Distingue entre errores recuperables y críticos
- Notifica cuando se solucionan problemas automáticamente

### 📊 Logging Estructurado
- **Terminal**: Eventos en tiempo real con timestamps
- **JSON**: `logs/descarga_errors.json` con todos los detalles
- **Monitor Log**: `logs/monitor.log` para análisis posterior

---

## 🚀 Inicio Rápido

### Opción 1: Script Automático (Recomendado)

```bash
# Desde la raíz del proyecto
cd /home/victor/100-trafico/100trafico

# Asegúrate de tener el entorno virtual activado
source ../.venv/bin/activate

# Ejecutar prueba completa con monitor
python scripts/start_prueba_con_monitor.py
```

Esto iniciará automáticamente:
1. ✅ Bot Central (recibe videos)
2. ✅ Poster Worker (publica contenido)
3. ✅ Monitor de Descargas (supervisa todo)

### Opción 2: Manual

Terminal 1 - Sistema principal:
```bash
cd /home/victor/100-trafico/100trafico
source ../.venv/bin/activate
python main.py
```

Terminal 2 - Monitor:
```bash
cd /home/victor/100-trafico/100trafico
source ../.venv/bin/activate
python workers/monitor_descarga.py
```

---

## 🔍 Tipos de Errores Detectados

| Error | Acción Automática | Notificación Admin | Registro |
|-------|-------------------|-------------------|----------|
| **Timeout de descarga** | Reintento hasta 3 veces con backoff exponencial | ✅ Si falla tras 3 intentos | JSON + Terminal |
| **Ruta inexistente** | Crea carpeta `mkdir -p` | ❌ No | JSON + Terminal |
| **Archivo corrupto** | Elimina archivo y reintenta | ✅ Sí | JSON + Terminal |
| **Problemas de permisos** | Ejecuta `sudo chown` | ✅ Si persiste | JSON + Terminal |
| **Disco lleno** | Detiene y marca crítico | ✅ Sí (CRÍTICO) | JSON + Terminal |
| **Servidor local caído** | Verifica cada 10s (3 intentos) | ✅ Sí (CRÍTICO) | JSON + Terminal |

---

## 📝 Formato de Log JSON

Cada error se registra en `logs/descarga_errors.json`:

```json
{
  "timestamp": "2025-12-25T14:30:20.123456+00:00",
  "modelo": "victor",
  "video": "20251225_143020_a3f2b1.mp4",
  "error_type": "timeout",
  "error_message": "Error completo del log original",
  "accion": "reintento 2/3",
  "estado": "reintentando",
  "intento": 2,
  "max_intentos": 3
}
```

### Estados Posibles
- `detectado`: Error recién detectado
- `pendiente`: Esperando acción correctiva
- `reintentando`: Reintento en proceso
- `solucionado`: Problema resuelto automáticamente
- `fallido`: No se pudo resolver tras reintentos

---

## 🎬 Flujo de Operación

```
┌──────────────────────────────────────────────────────────┐
│  1. Usuario envía video por Telegram                     │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│  2. Bot Central recibe y comienza descarga              │
│     • Monitor detecta inicio de descarga                 │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
          ┌──────┴──────┐
          │   ¿Error?   │
          └──────┬──────┘
                 │
        ┌────────┴────────┐
        │                 │
       SÍ                NO
        │                 │
        ▼                 ▼
┌───────────────┐  ┌──────────────────┐
│ 3a. Detectar  │  │ 3b. Descarga OK  │
│     tipo      │  │     Continúa     │
└───────┬───────┘  └──────────────────┘
        │
        ▼
┌────────────────────────────────────────┐
│ 4. Ejecutar acción correctiva          │
│    • Timeout → Reintento               │
│    • Corrupto → Limpiar + Reintento    │
│    • Permisos → sudo chown             │
│    • etc.                              │
└────────────────┬───────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────┐
│ 5. Registrar en logs/descarga_errors.json│
└────────────────┬─────────────────────────┘
                 │
                 ▼
          ┌──────┴──────┐
          │ ¿Solucionado?│
          └──────┬───────┘
                 │
        ┌────────┴────────┐
        │                 │
       SÍ                NO
        │                 │
        ▼                 ▼
┌───────────────┐  ┌─────────────────┐
│ 6a. Continúa  │  │ 6b. Notificar   │
│     pipeline  │  │     admin       │
└───────────────┘  └─────────────────┘
```

---

## 🛠️ Configuración

### Variables de Entorno Requeridas

Archivo: `src/.env`

```bash
# Credenciales de Telegram (obligatorias)
TELEGRAM_TOKEN=tu_token_aqui
ADMIN_ID=tu_user_id_aqui

# Servidor local de Telegram (para archivos grandes)
USE_LOCAL_BOT_API=true
TELEGRAM_BOT_API_LOCAL_URL=http://localhost:8081
```

### Configuración del Monitor

Variables configurables en `workers/monitor_descarga.py`:

```python
# Número máximo de reintentos
MAX_RETRIES = 3

# Delays para backoff exponencial (segundos)
BACKOFF_DELAYS = [1, 2, 4]

# Intervalo de verificación periódica (segundos)
VERIFICACION_PERIODICA = 30
```

---

## 📊 Verificaciones Periódicas

Cada 30 segundos, el monitor ejecuta verificaciones automáticas:

### ✅ Espacio en Disco
- **Advertencia**: < 5 GB libres
- **Crítico**: < 2 GB libres (notifica admin)

### ✅ Estado del Servidor Local
- Verifica que Docker esté corriendo
- Confirma que `telegram-bot-api` esté activo

### ✅ Salud del Sistema
- Verifica que `main.py` siga corriendo
- Detecta caídas inesperadas

---

## 🧪 Prueba del Sistema

### Paso 1: Preparar Entorno

```bash
# Verificar que el servidor local esté corriendo
docker ps | grep telegram-bot-api

# Si no está corriendo, iniciarlo
./scripts/start_local_bot_api.sh

# Activar entorno virtual
cd /home/victor/100-trafico/100trafico
source ../.venv/bin/activate
```

### Paso 2: Iniciar Monitor

```bash
# Usar script automático (recomendado)
python scripts/start_prueba_con_monitor.py
```

### Paso 3: Enviar Video de Prueba

1. Abre Telegram y busca tu bot
2. Envía `/start`
3. Envía un video (preferiblemente > 20 MB para probar servidor local)
4. Observa el monitor en terminal

### Paso 4: Observar Resultados

#### En Terminal
```
[14:30:15] 👀 Iniciando monitoreo de logs...
[14:30:20] [MAIN] 🤖 Iniciando Bot Central...
[14:30:25] [MAIN] ✅ Video recibido: 20251225_143020_a3f2b1.mp4
[14:30:30] ✅ Descarga exitosa: 250 MB
```

#### En JSON (`logs/descarga_errors.json`)
Si hay errores, verás:
```json
[
  {
    "timestamp": "2025-12-25T14:30:20+00:00",
    "modelo": "victor",
    "video": "20251225_143020_a3f2b1.mp4",
    "error_type": "timeout",
    "accion": "reintento 1/3",
    "estado": "solucionado"
  }
]
```

#### En Telegram (Admin)
Recibirás notificaciones como:
```
⚠️ Monitor de Descargas

Error de timeout detectado
Modelo: victor
Video: 20251225_143020_a3f2b1.mp4
Reintentando automáticamente...
```

---

## 🔧 Solución de Problemas

### El monitor no inicia

**Problema**: `ModuleNotFoundError: No module named 'telegram'`

**Solución**:
```bash
pip install python-telegram-bot>=20.8 python-dotenv
```

### No recibo notificaciones en Telegram

**Problema**: Credenciales no configuradas

**Solución**:
1. Verifica `src/.env`:
```bash
cat src/.env | grep TELEGRAM
```
2. Debe contener:
```
TELEGRAM_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_ID=123456789
```

### El monitor detecta errores pero no corrige

**Problema**: Permisos insuficientes

**Solución**:
```bash
# Para archivos del servidor local
sudo chown -R $USER:$USER ~/.telegram-bot-api

# Para carpeta de modelos
sudo chown -R $USER:$USER modelos/
```

### Logs JSON vacíos

**Problema**: No se detectan errores (¡puede ser bueno!)

**Verificación**:
```bash
# Ver si hay logs del monitor
cat logs/monitor.log

# Ver contenido actual del JSON
cat logs/descarga_errors.json
```

---

## 📈 Análisis Post-Prueba

### Ver Resumen de Errores

```bash
# Ver todos los errores registrados
cat logs/descarga_errors.json | python -m json.tool

# Contar errores por tipo
cat logs/descarga_errors.json | jq -r '.[].error_type' | sort | uniq -c
```

### Ver Timeline Completo

```bash
# Ver log cronológico del monitor
cat logs/monitor.log

# Filtrar solo errores
cat logs/monitor.log | grep -E "⚠️|❌"
```

### Verificar Estado del Sistema

```bash
# Ver últimos eventos del bot
tail -50 logs/bot_central.log

# Ver si hay procesos huérfanos
ps aux | grep -E "main.py|monitor_descarga"
```

---

## 🔄 Integración con Pipeline

El monitor **NO altera** el flujo normal del sistema. Solo observa y corrige:

```
Video Telegram → Bot Central → [Monitor supervisa] → Caption → BD → Poster
                      ↓
                  ¿Error?
                      ↓
             [Monitor corrige]
                      ↓
              Continúa flujo
```

### Después de la Descarga

El monitor **no interviene** en:
- Generación de captions (Gemini AI)
- Inserción en Supabase
- Programación de publicaciones
- Ejecución de workers Playwright

Solo garantiza que el **video llegue correctamente al disco**.

---

## 🎯 Casos de Uso

### Caso 1: Primera Prueba del Sistema
```bash
# Inicio completo supervisado
python scripts/start_prueba_con_monitor.py

# Enviar 3-5 videos de prueba
# Observar que todo funcione
# Revisar logs/descarga_errors.json

# Detener con Ctrl+C
```

### Caso 2: Debug de Problemas de Descarga
```bash
# Si hay problemas recurrentes
# Iniciar solo el monitor en modo verbose

python workers/monitor_descarga.py

# En otra terminal, iniciar el bot
cd /home/victor/100-trafico/100trafico
python main.py

# Observar logs en tiempo real
```

### Caso 3: Prueba de Carga (Múltiples Videos)
```bash
# Iniciar con monitor
python scripts/start_prueba_con_monitor.py

# Enviar múltiples videos seguidos
# El monitor detectará y registrará todos los eventos
# Verificar que no haya cuellos de botella
```

---

## ⚠️ Limitaciones

### Solo Para Primera Prueba
- Diseñado para sesiones temporales
- No está optimizado para ejecución 24/7
- Para producción, considerar:
  - Servicio systemd permanente
  - Base de datos para logs (no solo JSON)
  - Dashboard web de monitoreo
  - Alertas más sofisticadas (email, Slack, etc.)

### Detección de Errores
- Depende de patrones en logs
- Errores nuevos no previstos pueden no detectarse
- Añadir nuevos patrones en `detectar_error_en_linea()`

### Acciones Correctivas
- **sudo**: Requiere que el usuario tenga permisos sudo sin contraseña
- **Reintentos**: No garantizan éxito si el problema es externo (ej: internet caído)
- **Disco lleno**: El monitor solo alerta, no libera espacio

---

## 🚀 Próximos Pasos (Post-Primera Prueba)

Después de la prueba exitosa, considerar:

### 1. Servicio Permanente
```bash
# Crear servicio systemd
sudo nano /etc/systemd/system/trafico-monitor.service
```

### 2. Dashboard de Monitoreo
- Integrar con panel admin (Next.js)
- Visualizar errores en tiempo real
- Gráficos de tendencias

### 3. Alertas Avanzadas
- Integración con email (SMTP)
- Webhooks para Slack/Discord
- Escalado de alertas (admin → supervisor → dev)

### 4. Machine Learning
- Predecir errores antes de que ocurran
- Detectar patrones anómalos
- Optimizar reintentos según historial

---

## 📚 Referencias

- **PRD Original**: (ver comentarios en código)
- **Bot Central**: `src/project/bot_central.py`
- **Poster Worker**: `src/project/poster_prd.py`
- **Arquitectura**: `docs/DOCUMENTO_TECNICO.md`
- **Telegram API**: `docs/TELEGRAM_ARCHIVOS_GRANDES.md`

---

## 💬 Soporte

Si encuentras problemas:

1. **Revisar logs**:
   - `logs/monitor.log`
   - `logs/descarga_errors.json`
   - `logs/bot_central.log`

2. **Verificar servicios**:
   ```bash
   docker ps | grep telegram-bot-api
   ps aux | grep -E "main.py|monitor"
   ```

3. **Reiniciar limpio**:
   ```bash
   pkill -f "main.py|monitor_descarga"
   rm logs/*.log logs/*.json
   python scripts/start_prueba_con_monitor.py
   ```

---

**🎉 ¡Listo para la primera prueba! Buena suerte con el sistema.**

---

_Documentación generada el 25 de diciembre de 2025_  
_Versión del Monitor: 1.0.0-prueba_  
_Sistema: 100-Tráfico_


