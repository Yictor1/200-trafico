#!/usr/bin/env python3
"""
Script de Inicio para Prueba con Monitor de Descargas

Ejecuta en paralelo:
1. main.py - Sistema principal (bot + poster)
2. monitor_descarga.py - Agente de monitoreo

Uso:
    python scripts/start_prueba_con_monitor.py
    
    O directamente:
    ./scripts/start_prueba_con_monitor.py
"""

import subprocess
import time
import sys
import signal
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
VENV_PYTHON = BASE_DIR.parent / ".venv" / "bin" / "python3"

# Determinar qué python usar
if VENV_PYTHON.exists():
    python_exe = str(VENV_PYTHON)
    print(f"✅ Usando entorno virtual: {python_exe}")
else:
    python_exe = sys.executable
    print(f"⚠️  Usando Python del sistema: {python_exe}")
    print(f"   Recomendado: activar entorno virtual")

# Archivos a ejecutar
MAIN_PY = BASE_DIR / "main.py"
MONITOR_PY = BASE_DIR / "workers" / "monitor_descarga.py"

# Verificar que existan
if not MAIN_PY.exists():
    print(f"❌ Error: No se encuentra {MAIN_PY}")
    sys.exit(1)

if not MONITOR_PY.exists():
    print(f"❌ Error: No se encuentra {MONITOR_PY}")
    sys.exit(1)

# Lista de procesos
processes = []

def signal_handler(sig, frame):
    """Maneja Ctrl+C para detener todos los procesos"""
    print("\n\n🛑 Deteniendo todos los servicios...")
    for p in processes:
        if p.poll() is None:
            p.terminate()
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()
    print("👋 Todos los servicios detenidos. Adiós.")
    sys.exit(0)

# Registrar handler para Ctrl+C
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

print("=" * 70)
print("🚀 INICIO DE PRUEBA CON MONITOR DE DESCARGAS")
print("=" * 70)
print("📅 Sistema: Bot Central + Poster + Monitor")
print("🔍 Monitoreando: Descargas, errores y acciones correctivas")
print("⚠️  Presiona Ctrl+C para detener todos los servicios")
print("=" * 70)
print()

try:
    # 1. Iniciar main.py (Bot Central + Poster)
    print("🤖 Iniciando main.py (Bot Central + Poster)...")
    # Redirigir stdout/stderr a archivo de log para que el monitor pueda leerlo
    log_file = BASE_DIR / "logs" / "bot_central.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(log_file, "w") as f:
        f.write(f"=== Inicio de sesión: {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
    
    # Iniciar main.py con logging
    p_main = subprocess.Popen(
        [python_exe, str(MAIN_PY)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1  # Line buffered
    )
    processes.append(p_main)
    print("   ✅ main.py iniciado")
    
    # Dar tiempo para que main.py inicie completamente
    time.sleep(3)
    
    # 2. Iniciar monitor_descarga.py
    print("👀 Iniciando monitor de descargas...")
    p_monitor = subprocess.Popen(
        [python_exe, str(MONITOR_PY)],
        stdout=sys.stdout,  # Output directo a consola
        stderr=sys.stderr
    )
    processes.append(p_monitor)
    print("   ✅ Monitor iniciado")
    
    print()
    print("=" * 70)
    print("✅ SISTEMA COMPLETAMENTE INICIADO")
    print("=" * 70)
    print()
    print("📋 Servicios corriendo:")
    print("   1. Bot Central - Recibe videos de Telegram")
    print("   2. Poster Worker - Publica contenido programado")
    print("   3. Monitor - Supervisa errores y ejecuta correcciones")
    print()
    print("💡 Tips:")
    print("   - Envía un video al bot para probar el sistema")
    print("   - El monitor mostrará eventos en tiempo real")
    print("   - Logs JSON: logs/descarga_errors.json")
    print("   - Logs del monitor: logs/monitor.log")
    print()
    print("⚠️  Presiona Ctrl+C cuando termines la prueba")
    print("=" * 70)
    print()
    
    # Redirigir output de main.py al archivo de log (en segundo plano)
    def log_main_output():
        with open(log_file, "a") as f:
            for line in p_main.stdout:
                f.write(line)
                f.flush()
                # También mostrar en consola líneas importantes
                if any(kw in line.lower() for kw in ["error", "❌", "✅", "descargando", "video"]):
                    print(f"[MAIN] {line.strip()}")
    
    import threading
    log_thread = threading.Thread(target=log_main_output, daemon=True)
    log_thread.start()
    
    # Mantener vivo y verificar procesos
    while True:
        time.sleep(1)
        
        # Verificar si main.py murió
        if p_main.poll() is not None:
            print("\n❌ ERROR: main.py se detuvo inesperadamente")
            print(f"   Código de salida: {p_main.returncode}")
            break
        
        # Verificar si monitor murió
        if p_monitor.poll() is not None:
            print("\n⚠️  Monitor se detuvo")
            print(f"   Código de salida: {p_monitor.returncode}")
            # Continuar sin monitor
            processes.remove(p_monitor)

except KeyboardInterrupt:
    print("\n🛑 Interrupción detectada...")
except Exception as e:
    print(f"\n❌ Error inesperado: {e}")
    import traceback
    traceback.print_exc()
finally:
    # Limpiar procesos
    signal_handler(None, None)


