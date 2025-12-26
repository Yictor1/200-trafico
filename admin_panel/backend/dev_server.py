#!/usr/bin/env python3
"""
Servidor de desarrollo con auto-detección de puerto (8000-8006)
"""
import socket
import subprocess
import sys
from pathlib import Path

def is_port_available(port: int) -> bool:
    """Verifica si un puerto está disponible"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            return True
    except OSError:
        return False

def find_available_port(start_port: int = 8000, end_port: int = 8006) -> int:
    """Encuentra el primer puerto disponible en el rango"""
    for port in range(start_port, end_port + 1):
        if is_port_available(port):
            return port
    raise RuntimeError(f"No hay puertos disponibles en el rango {start_port}-{end_port}")

if __name__ == "__main__":
    try:
        port = find_available_port()
        print(f"🚀 Iniciando servidor en puerto {port}...")
        print(f"📡 API: http://localhost:{port}")
        print(f"📚 Docs: http://localhost:{port}/docs")
        print(f"🔄 ReDoc: http://localhost:{port}/redoc")
        print(f"\n⏸️  Presiona Ctrl+C para detener\n")
        
        # Ejecutar uvicorn
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--host", "0.0.0.0",
            "--port", str(port),
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
