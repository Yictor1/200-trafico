"""
Router de Plataformas - Gestión de plataformas disponibles
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from pathlib import Path

router = APIRouter()

TRAFICO_ROOT = Path(__file__).resolve().parents[3]
WORKERS_DIR = TRAFICO_ROOT / "workers"

# Schemas
class PlatformCreate(BaseModel):
    nombre: str
    url: str

class PlatformResponse(BaseModel):
    nombre: str
    url: str
    has_worker: bool

@router.get("/platforms", response_model=List[PlatformResponse])
async def get_platforms():
    """Lista todas las plataformas disponibles (basado en workers existentes)"""
    try:
        platforms = []
        
        # Detectar plataformas desde workers existentes
        if WORKERS_DIR.exists():
            for worker_file in WORKERS_DIR.glob("*.js"):
                if worker_file.stem not in ["login_kams"]:  # Excluir helpers
                    platforms.append({
                        "nombre": worker_file.stem,
                        "url": "",  # No tenemos URL guardada
                        "has_worker": True
                    })
        
        # Agregar plataformas conocidas sin worker
        known_platforms = [
            {"nombre": "kams", "url": "https://kams.com", "has_worker": True},
            {"nombre": "xxxfollow", "url": "https://xxxfollow.com", "has_worker": True},
            {"nombre": "onlyfans", "url": "https://onlyfans.com", "has_worker": False},
            {"nombre": "fansly", "url": "https://fansly.com", "has_worker": False},
        ]
        
        # Merge con workers existentes
        platform_names = {p["nombre"] for p in platforms}
        for known in known_platforms:
            if known["nombre"] not in platform_names:
                platforms.append(known)
        
        return platforms
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo plataformas: {str(e)}")

@router.post("/platforms", response_model=PlatformResponse)
async def create_platform(platform: PlatformCreate):
    """Registra una nueva plataforma (sin worker aún)"""
    try:
        # Por ahora solo retornamos la plataforma
        # El worker se creará con /capture/start
        return {
            "nombre": platform.nombre,
            "url": platform.url,
            "has_worker": False
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando plataforma: {str(e)}")
