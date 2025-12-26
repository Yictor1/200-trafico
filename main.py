#!/usr/bin/env python3
import subprocess
import time
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
VENV_PYTHON = BASE_DIR.parent / ".venv" / "bin" / "python3"  # .venv está en el directorio raíz del proyecto
BOT_MAIN = BASE_DIR / "src" / "project" / "bot_central.py"
POSTER_MAIN = BASE_DIR / "src" / "project" / "poster_prd.py"
# KPI_SCHEDULER = BASE_DIR / "src" / "project" / "kpi_scheduler.py"  # DESACTIVADO: migrado a PRD, listo para activación (FASE6-B completada)

# Validar que los archivos principales existan
if not BOT_MAIN.exists():
    print(f"❌ Error: No se encuentra {BOT_MAIN}")
    sys.exit(1)
if not POSTER_MAIN.exists():
    print(f"❌ Error: No se encuentra {POSTER_MAIN}")
    sys.exit(1)
# KPI Scheduler desactivado por diseño (migrado a PRD en FASE6-B, listo para activación)
# if not KPI_SCHEDULER.exists():
#     print(f"⚠️  Advertencia: No se encuentra {KPI_SCHEDULER}")
#     print("   El scheduler de KPIs no se iniciará")

# Determinar qué python usar
if VENV_PYTHON.exists() and not sys.executable.startswith(str(BASE_DIR / ".venv")):
    print(f"⚠️  Recomiendo activar el entorno virtual:\n    source {BASE_DIR}/.venv/bin/activate\n")
    python_exe = str(VENV_PYTHON)
else:
    python_exe = sys.executable

print(f"🚀 Iniciando servicios con: {python_exe}")

processes = []

try:
    # Iniciar Bot Central
    print("🤖 Iniciando Bot Central...")
    p_bot = subprocess.Popen([python_exe, str(BOT_MAIN)])
    processes.append(p_bot)

    # Iniciar Poster Scheduler
    print("📅 Iniciando Poster Scheduler...")
    p_poster = subprocess.Popen([python_exe, str(POSTER_MAIN)])
    processes.append(p_poster)

    # KPI Scheduler desactivado por diseño (migrado a PRD en FASE6-B, listo para activación)
    # Para activar: descomentar KPI_SCHEDULER arriba y este bloque
    # if KPI_SCHEDULER.exists():
    #     print("📊 Iniciando KPI Scheduler (PRD)...")
    #     p_kpi = subprocess.Popen([python_exe, str(KPI_SCHEDULER)])
    #     processes.append(p_kpi)
    # else:
    #     print("⚠️  KPI Scheduler no disponible (archivo no encontrado)")

    print("✅ Servicios iniciados (Bot Central + Poster PRD). Presiona Ctrl+C para detener.")
    
    # Mantener vivo el proceso principal
    while True:
        time.sleep(1)
        # Verificar si algún proceso murió
        if p_bot.poll() is not None:
            print("❌ Bot Central se detuvo inesperadamente.")
            break
        if p_poster.poll() is not None:
            print("❌ Poster Scheduler se detuvo inesperadamente.")
            break
        # KPI Scheduler desactivado por diseño (listo para activación futura)
        # if KPI_SCHEDULER.exists() and len(processes) > 2:
        #     p_kpi = processes[2]
        #     if p_kpi.poll() is not None:
        #         print("❌ KPI Scheduler se detuvo inesperadamente.")
        #         break

except KeyboardInterrupt:
    print("\n🛑 Deteniendo servicios...")
finally:
    for p in processes:
        if p.poll() is None:
            p.terminate()
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()
    print("👋 Adiós.")

