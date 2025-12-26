#!/usr/bin/env python3
"""
Agente de Monitoreo de Descargas - 100-Tráfico
PRD: Supervisa en tiempo real la recepción y procesamiento de videos.

Funcionalidades:
- Monitoreo de logs de bot_central.py en tiempo real
- Detección automática de errores (timeout, permisos, corrupto, etc.)
- Acciones correctivas automáticas (reintentos, limpieza, notificaciones)
- Logging estructurado en JSON + terminal
- Notificaciones vía Telegram al admin

Uso:
    python workers/monitor_descarga.py
    
    O usar el script de inicio:
    python scripts/start_prueba_con_monitor.py
"""

import sys
import os
import json
import time
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import re

# Configurar paths
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR / "src"))

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv(dotenv_path=BASE_DIR / "src" / ".env")

# Configuración
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
ERROR_LOG_FILE = LOGS_DIR / "descarga_errors.json"
MONITOR_LOG_FILE = LOGS_DIR / "monitor.log"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# Configuración de reintentos
MAX_RETRIES = 3
BACKOFF_DELAYS = [1, 2, 4]  # segundos (exponencial)


@dataclass
class ErrorEvent:
    """Estructura de un evento de error"""
    timestamp: str
    modelo: str
    video: str
    error_type: str
    error_message: str
    accion: str
    estado: str
    intento: int = 1
    max_intentos: int = MAX_RETRIES
    
    def to_dict(self):
        return asdict(self)


class MonitorDescarga:
    """Monitor de descargas en tiempo real"""
    
    def __init__(self):
        self.running = True
        self.error_history: List[ErrorEvent] = []
        self.retry_queue: Dict[str, ErrorEvent] = {}
        self.telegram_bot = None
        
    async def init_telegram(self):
        """Inicializa el bot de Telegram para notificaciones"""
        if not TELEGRAM_TOKEN or not ADMIN_ID:
            self.log_terminal("⚠️  Credenciales de Telegram no configuradas. Notificaciones desactivadas.")
            return
        
        try:
            from telegram import Bot
            self.telegram_bot = Bot(token=TELEGRAM_TOKEN)
            await self.telegram_bot.get_me()  # Verificar conexión
            self.log_terminal("✅ Bot de Telegram conectado para notificaciones")
        except Exception as e:
            self.log_terminal(f"⚠️  Error conectando bot de Telegram: {e}")
            self.telegram_bot = None
    
    def log_terminal(self, message: str):
        """Log en terminal con timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
        # También guardar en archivo de log del monitor
        with open(MONITOR_LOG_FILE, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def log_error_json(self, error_event: ErrorEvent):
        """Guarda error en archivo JSON estructurado"""
        try:
            # Leer errores existentes
            errors = []
            if ERROR_LOG_FILE.exists():
                with open(ERROR_LOG_FILE, "r") as f:
                    errors = json.load(f)
            
            # Agregar nuevo error
            errors.append(error_event.to_dict())
            
            # Guardar
            with open(ERROR_LOG_FILE, "w") as f:
                json.dump(errors, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.log_terminal(f"❌ Error guardando log JSON: {e}")
    
    async def notificar_admin(self, mensaje: str, critico: bool = False):
        """Envía notificación al admin vía Telegram"""
        if not self.telegram_bot or not ADMIN_ID:
            return
        
        try:
            emoji = "🚨" if critico else "⚠️"
            mensaje_completo = f"{emoji} **Monitor de Descargas**\n\n{mensaje}"
            
            await self.telegram_bot.send_message(
                chat_id=ADMIN_ID,
                text=mensaje_completo,
                parse_mode="Markdown"
            )
            self.log_terminal(f"📬 Notificación enviada al admin")
        except Exception as e:
            self.log_terminal(f"❌ Error enviando notificación: {e}")
    
    def detectar_error_en_linea(self, linea: str) -> Optional[Dict]:
        """
        Analiza una línea de log y detecta errores conocidos.
        
        Returns:
            Dict con {tipo, mensaje, modelo, video} si se detecta error, None si no
        """
        # Patrones de error conocidos
        patrones = {
            "timeout": r"timeout|timed out|connection.*timeout",
            "permisos": r"permission denied|chmod|chown|sudo.*error",
            "corrupto": r"corrupt|invalid.*file|broken.*video|ffmpeg.*error",
            "ruta_inexistente": r"no such file|directory.*not found|path.*not.*exist",
            "disco_lleno": r"no space left|disk.*full|quota.*exceeded",
            "servidor_caido": r"connection refused|bot api.*down|127\.0\.0\.1:8081.*failed"
        }
        
        # Buscar patrón de error
        error_detectado = None
        for tipo, patron in patrones.items():
            if re.search(patron, linea, re.IGNORECASE):
                error_detectado = tipo
                break
        
        if not error_detectado:
            return None
        
        # Intentar extraer modelo y video del contexto
        modelo_match = re.search(r"modelo[:\s]+(\w+)", linea, re.IGNORECASE)
        video_match = re.search(r"(\d{8}_\d{6}_[a-f0-9]+\.mp4)", linea)
        
        return {
            "tipo": error_detectado,
            "mensaje": linea.strip(),
            "modelo": modelo_match.group(1) if modelo_match else "unknown",
            "video": video_match.group(1) if video_match else "unknown"
        }
    
    async def ejecutar_accion_correctiva(self, error_event: ErrorEvent) -> bool:
        """
        Ejecuta acción correctiva según el tipo de error.
        
        Returns:
            True si se solucionó, False si persiste
        """
        tipo = error_event.error_type
        modelo = error_event.modelo
        video = error_event.video
        intento = error_event.intento
        
        self.log_terminal(f"🔧 Ejecutando corrección para {tipo} (intento {intento}/{MAX_RETRIES})")
        
        # Timeout de descarga
        if tipo == "timeout":
            await self.retry_descarga(error_event)
            return False  # Esperar siguiente intento
        
        # Ruta inexistente
        elif tipo == "ruta_inexistente":
            modelo_dir = BASE_DIR / "modelos" / modelo
            modelo_dir.mkdir(parents=True, exist_ok=True)
            self.log_terminal(f"✅ Carpeta creada: {modelo_dir}")
            return True
        
        # Archivo corrupto
        elif tipo == "corrupto":
            await self.limpiar_archivo_corrupto(modelo, video)
            await self.retry_descarga(error_event)
            return False
        
        # Problemas de permisos
        elif tipo == "permisos":
            await self.fix_permisos(modelo, video)
            return True
        
        # Disco lleno (crítico)
        elif tipo == "disco_lleno":
            await self.notificar_admin(
                f"🚨 **ERROR CRÍTICO: Disco lleno**\n\n"
                f"No se puede continuar descargando videos.\n"
                f"Modelo: {modelo}\n"
                f"Video: {video}",
                critico=True
            )
            return False
        
        # Servidor local caído
        elif tipo == "servidor_caido":
            await self.verificar_servidor_local()
            return False
        
        return False
    
    async def retry_descarga(self, error_event: ErrorEvent):
        """Reintenta descarga con backoff exponencial"""
        if error_event.intento > MAX_RETRIES:
            self.log_terminal(f"❌ Máximo de reintentos alcanzado para {error_event.video}")
            await self.notificar_admin(
                f"❌ **Fallo en descarga después de {MAX_RETRIES} intentos**\n\n"
                f"Modelo: {error_event.modelo}\n"
                f"Video: {error_event.video}\n"
                f"Error: {error_event.error_message[:100]}"
            )
            return
        
        # Backoff exponencial
        delay = BACKOFF_DELAYS[min(error_event.intento - 1, len(BACKOFF_DELAYS) - 1)]
        self.log_terminal(f"⏳ Esperando {delay}s antes de reintentar...")
        await asyncio.sleep(delay)
        
        # Marcar para reintento
        error_event.intento += 1
        error_event.accion = f"reintento {error_event.intento}/{MAX_RETRIES}"
        error_event.estado = "reintentando"
        
        self.log_error_json(error_event)
        self.log_terminal(f"🔄 Reintentando descarga (intento {error_event.intento})...")
        
        # Nota: El reintento real lo debe manejar el bot central
        # Este monitor solo detecta y registra
    
    async def limpiar_archivo_corrupto(self, modelo: str, video: str):
        """Elimina archivo corrupto/incompleto"""
        video_path = BASE_DIR / "modelos" / modelo / video
        if video_path.exists():
            try:
                video_path.unlink()
                self.log_terminal(f"🗑️  Archivo corrupto eliminado: {video}")
            except Exception as e:
                self.log_terminal(f"❌ Error eliminando archivo: {e}")
    
    async def fix_permisos(self, modelo: str, video: str):
        """Intenta corregir permisos del archivo"""
        video_path = BASE_DIR / "modelos" / modelo / video
        if not video_path.exists():
            return
        
        try:
            # Cambiar propietario
            subprocess.run(
                ['sudo', 'chown', f'{os.getuid()}:{os.getgid()}', str(video_path)],
                check=True,
                capture_output=True
            )
            self.log_terminal(f"✅ Permisos corregidos para: {video}")
        except subprocess.CalledProcessError as e:
            self.log_terminal(f"❌ Error corrigiendo permisos: {e}")
            await self.notificar_admin(
                f"⚠️ **Error de permisos persistente**\n\n"
                f"Modelo: {modelo}\n"
                f"Video: {video}\n"
                f"Requiere intervención manual."
            )
    
    async def verificar_servidor_local(self):
        """Verifica si el servidor local de Telegram está corriendo"""
        try:
            result = subprocess.run(
                ['docker', 'ps', '--filter', 'name=telegram-bot-api', '--format', '{{.Status}}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if "Up" in result.stdout:
                self.log_terminal("✅ Servidor local de Telegram está corriendo")
                return True
            else:
                self.log_terminal("❌ Servidor local de Telegram NO está corriendo")
                await self.notificar_admin(
                    "🚨 **Servidor local de Telegram caído**\n\n"
                    "Inicia el servidor con:\n"
                    "`./scripts/start_local_bot_api.sh`",
                    critico=True
                )
                return False
        except Exception as e:
            self.log_terminal(f"⚠️  No se pudo verificar servidor local: {e}")
            return False
    
    async def monitorear_logs(self):
        """Monitorea logs en tiempo real usando tail -f"""
        self.log_terminal("👀 Iniciando monitoreo de logs...")
        self.log_terminal(f"📂 Monitoreando: logs de bot_central.py")
        
        # Usar subprocess para tail -f (más eficiente que leer archivo manualmente)
        # Nota: En producción real, usaríamos watchdog o inotify
        
        # Por ahora, monitoreamos stdout/stderr capturando logs del proceso main.py
        # En una implementación real, leeríamos el archivo de log
        
        # Crear archivo de log si no existe
        bot_log = LOGS_DIR / "bot_central.log"
        if not bot_log.exists():
            bot_log.touch()
        
        # Leer logs en tiempo real
        proceso_tail = subprocess.Popen(
            ['tail', '-f', '-n', '0', str(bot_log)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        try:
            while self.running:
                linea = proceso_tail.stdout.readline()
                if not linea:
                    await asyncio.sleep(0.1)
                    continue
                
                # Detectar errores en la línea
                error_detectado = self.detectar_error_en_linea(linea)
                if error_detectado:
                    # Crear evento de error
                    error_event = ErrorEvent(
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        modelo=error_detectado["modelo"],
                        video=error_detectado["video"],
                        error_type=error_detectado["tipo"],
                        error_message=error_detectado["mensaje"],
                        accion="detectado",
                        estado="pendiente"
                    )
                    
                    # Registrar error
                    self.log_terminal(f"⚠️  Error detectado: {error_event.error_type}")
                    self.log_error_json(error_event)
                    self.error_history.append(error_event)
                    
                    # Ejecutar acción correctiva
                    solucionado = await self.ejecutar_accion_correctiva(error_event)
                    
                    if solucionado:
                        error_event.estado = "solucionado"
                        self.log_terminal(f"✅ Error solucionado automáticamente")
                    else:
                        error_event.estado = "pendiente"
                    
                    self.log_error_json(error_event)
                
                # También mostrar líneas importantes en terminal
                if any(keyword in linea.lower() for keyword in ["error", "✅", "❌", "descargando"]):
                    print(linea.strip())
                    
        except KeyboardInterrupt:
            self.log_terminal("\n👋 Deteniendo monitor...")
        finally:
            proceso_tail.terminate()
    
    async def ejecutar_verificacion_periodica(self):
        """Ejecuta verificaciones periódicas del sistema"""
        while self.running:
            await asyncio.sleep(30)  # Cada 30 segundos
            
            # Verificar espacio en disco
            try:
                statvfs = os.statvfs(BASE_DIR)
                espacio_libre_gb = (statvfs.f_bavail * statvfs.f_frsize) / (1024**3)
                
                if espacio_libre_gb < 5:  # Menos de 5GB
                    self.log_terminal(f"⚠️  Espacio en disco bajo: {espacio_libre_gb:.2f} GB libres")
                    if espacio_libre_gb < 2:  # Crítico
                        await self.notificar_admin(
                            f"🚨 **Espacio en disco crítico**\n\n"
                            f"Solo {espacio_libre_gb:.2f} GB libres.\n"
                            f"Limpia archivos antiguos urgentemente.",
                            critico=True
                        )
            except Exception as e:
                self.log_terminal(f"⚠️  Error verificando espacio en disco: {e}")
    
    async def run(self):
        """Inicia el monitor"""
        self.log_terminal("=" * 60)
        self.log_terminal("🚀 AGENTE DE MONITOREO DE DESCARGAS")
        self.log_terminal("=" * 60)
        self.log_terminal(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log_terminal(f"📂 Base: {BASE_DIR}")
        self.log_terminal(f"📝 Logs: {ERROR_LOG_FILE}")
        self.log_terminal("=" * 60)
        
        # Inicializar Telegram
        await self.init_telegram()
        
        # Notificar inicio
        await self.notificar_admin(
            "✅ **Monitor de descargas iniciado**\n\n"
            "Supervisando el pipeline de videos en tiempo real."
        )
        
        # Ejecutar tareas en paralelo
        try:
            await asyncio.gather(
                self.monitorear_logs(),
                self.ejecutar_verificacion_periodica()
            )
        except KeyboardInterrupt:
            self.log_terminal("\n🛑 Monitor detenido por usuario")
        finally:
            self.running = False
            
            # Resumen final
            self.log_terminal("\n" + "=" * 60)
            self.log_terminal("📊 RESUMEN DE LA SESIÓN")
            self.log_terminal("=" * 60)
            self.log_terminal(f"Total de errores detectados: {len(self.error_history)}")
            
            if self.error_history:
                errores_por_tipo = {}
                for err in self.error_history:
                    errores_por_tipo[err.error_type] = errores_por_tipo.get(err.error_type, 0) + 1
                
                for tipo, count in errores_por_tipo.items():
                    self.log_terminal(f"  - {tipo}: {count}")
            
            self.log_terminal("=" * 60)
            
            await self.notificar_admin(
                f"🛑 **Monitor de descargas detenido**\n\n"
                f"Errores detectados: {len(self.error_history)}\n"
                f"Logs disponibles en: `logs/descarga_errors.json`"
            )


async def main():
    """Punto de entrada principal"""
    monitor = MonitorDescarga()
    await monitor.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Adiós")


