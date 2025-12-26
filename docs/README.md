# 📚 Documentación del Proyecto

Esta carpeta contiene toda la documentación del bot de Telegram y el sistema de gestión de contenido.

## 📄 Archivos Disponibles

### Guías de Instalación
- **`INSTALACION.md`** - Guía completa de instalación del proyecto
- **`INICIO_RAPIDO.md`** - Guía rápida para empezar a usar el sistema
- **`INSTALACION_AGENTE_CURSOR.md`** - 🤖 **Guía automatizada para instalación en nuevo PC** (para agentes de Cursor)
- **`INSTRUCCIONES_DOCKER.txt`** - Instrucciones específicas para Docker

### Configuración y Verificación
- **`TELEGRAM_ARCHIVOS_GRANDES.md`** - 📁 **Documentación oficial** sobre el servidor local de Telegram Bot API (hasta 2GB) - **¡LEE ESTO PRIMERO!**
- **`VERIFICACION_BOT.md`** - Pasos para verificar que el bot está funcionando correctamente
- **`MONITOR_DESCARGAS.md`** - 🔍 **Agente de monitoreo en tiempo real** para supervisar descargas y detectar errores automáticamente
- **`../FIX_DEFINITIVO_LOCAL_MODE.md`** - ✅ **Fix definitivo** - Por qué NO usar `local_mode=True`

### Documentación Técnica
- **`DOCUMENTO_TECNICO.md`** - 📋 **Documento técnico completo del proyecto** (estructura, arquitectura, flujos, integraciones, problemas potenciales)

## 🚀 Inicio Rápido

### Opción A: Con Monitor de Descargas (Recomendado para Primera Prueba)
```bash
cd /ruta/al/proyecto/100-trafico/100trafico
source ../.venv/bin/activate
python scripts/start_prueba_con_monitor.py
```
Ver **`MONITOR_DESCARGAS.md`** para más detalles.

### Opción B: Inicio Manual

#### 1. Iniciar el servidor local de Telegram (para archivos grandes)
```bash
cd /ruta/al/proyecto/100-trafico
./scripts/start_local_bot_api.sh
```

#### 2. Iniciar el bot de Telegram
```bash
cd /ruta/al/proyecto/100-trafico
python3 main.py
```

#### 3. Iniciar el panel de administración (opcional)

**Backend:**
```bash
./scripts/start_backend.sh
```

**Frontend:**
```bash
./scripts/start_frontend.sh
```

## 📦 Estructura del Proyecto

```
100-trafico/
├── docs/              # Documentación (esta carpeta)
├── scripts/           # Scripts de inicio e instalación
├── tests/             # Archivos de prueba
├── src/               # Código fuente
│   ├── database/      # Cliente de Supabase
│   └── project/       # Bot y lógica principal
├── workers/           # Workers de Playwright para plataformas
├── modelos/           # Videos y configuración por modelo
├── admin_panel/       # Panel web de administración
└── main.py            # Punto de entrada del bot

```

## 🎯 Funcionalidades Principales

- **Descarga de videos grandes** (hasta 2GB) mediante servidor local de Telegram
- **Generación automática de captions** con IA (Gemini)
- **Publicación programada** en múltiples plataformas (Kams, XXXFollow, FikFap)
- **Panel de administración** web para gestionar modelos y contenido
- **Métricas y KPIs** de rendimiento de cada modelo

## 🔧 Solución de Problemas

Si tienes problemas:
1. Revisa `VERIFICACION_BOT.md` para diagnóstico
2. Verifica que Docker esté corriendo: `docker ps`
3. Revisa los logs del bot en la terminal donde ejecutaste `main.py`
4. Consulta `TELEGRAM_ARCHIVOS_GRANDES.md` si tienes problemas con archivos grandes

## 📞 Soporte

Para más información, consulta los archivos de documentación específicos en esta carpeta.

