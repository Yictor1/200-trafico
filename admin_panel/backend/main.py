"""
FastAPI Backend - Trafico Admin Panel
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import sys
from dotenv import load_dotenv
import os

# Agregar path del proyecto Trafico para importar supabase_client
TRAFICO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(TRAFICO_ROOT / "src"))

# Cargar .env desde src/
env_path = TRAFICO_ROOT / "src" / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ .env cargado desde: {env_path}")
else:
    print(f"⚠️  .env no encontrado en: {env_path}")

from api import models_router, platforms_router, workers_router, capture_router, auth_router, navegador_router, kpi_router

# Crear app
app = FastAPI(
    title="Trafico Admin Panel API",
    description="API para gestión de modelos, plataformas y workers",
    version="1.0.0"
)

# CORS - Soporta puertos dinámicos
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    *[f"http://localhost:{port}" for port in range(3000, 3007)],
    *[f"http://127.0.0.1:{port}" for port in range(3000, 3007)],
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(models_router.router, prefix="/api", tags=["models"])
app.include_router(platforms_router.router, prefix="/api", tags=["platforms"])
app.include_router(workers_router.router, prefix="/api", tags=["workers"])
app.include_router(capture_router.router, prefix="/api", tags=["capture"])
app.include_router(auth_router.router, prefix="/api", tags=["auth"])
app.include_router(navegador_router.router, prefix="/api", tags=["navegador"])
app.include_router(kpi_router.router, prefix="/api", tags=["kpi"])

@app.get("/")
async def root():
    return {
        "message": "Trafico Admin Panel API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "ok"}
