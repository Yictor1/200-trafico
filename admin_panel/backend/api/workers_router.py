"""
Router de Workers - Gestión de workers de Playwright
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from pathlib import Path

router = APIRouter()

TRAFICO_ROOT = Path(__file__).resolve().parents[3]
WORKERS_DIR = TRAFICO_ROOT / "workers"

# Schemas
class WorkerResponse(BaseModel):
    nombre: str
    path: str
    size: int
    lines: int

class WorkerCodeResponse(BaseModel):
    nombre: str
    code: str

class WorkerUpdateRequest(BaseModel):
    code: str

@router.get("/workers", response_model=List[WorkerResponse])
async def get_workers():
    """Lista todos los workers disponibles"""
    try:
        workers = []
        
        if not WORKERS_DIR.exists():
            return workers
        
        for worker_file in WORKERS_DIR.glob("*.js"):
            code = worker_file.read_text()
            workers.append({
                "nombre": worker_file.stem,
                "path": str(worker_file.relative_to(TRAFICO_ROOT)),
                "size": worker_file.stat().st_size,
                "lines": len(code.splitlines())
            })
        
        return sorted(workers, key=lambda x: x["nombre"])
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo workers: {str(e)}")

@router.get("/workers/{nombre}", response_model=WorkerCodeResponse)
async def get_worker_code(nombre: str):
    """Obtiene el código de un worker específico"""
    try:
        worker_file = WORKERS_DIR / f"{nombre}.js"
        
        if not worker_file.exists():
            raise HTTPException(status_code=404, detail=f"Worker '{nombre}' no encontrado")
        
        code = worker_file.read_text()
        
        return {
            "nombre": nombre,
            "code": code
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo worker: {str(e)}")

@router.put("/workers/{nombre}")
async def update_worker(nombre: str, request: WorkerUpdateRequest):
    """Actualiza el código de un worker"""
    try:
        worker_file = WORKERS_DIR / f"{nombre}.js"
        
        if not worker_file.exists():
            raise HTTPException(status_code=404, detail=f"Worker '{nombre}' no encontrado")
        
        # Guardar código actualizado
        worker_file.write_text(request.code)
        
        return {
            "status": "updated",
            "nombre": nombre,
            "size": len(request.code)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando worker: {str(e)}")

@router.delete("/workers/{nombre}")
async def delete_worker(nombre: str):
    """Elimina un worker"""
    try:
        worker_file = WORKERS_DIR / f"{nombre}.js"
        
        if not worker_file.exists():
            raise HTTPException(status_code=404, detail=f"Worker '{nombre}' no encontrado")
        
        worker_file.unlink()
        
        return {
            "status": "deleted",
            "nombre": nombre
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando worker: {str(e)}")
