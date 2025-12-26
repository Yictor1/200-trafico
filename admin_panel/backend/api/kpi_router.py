"""
Router para KPIs de Stripchat/CBHours
Lee desde archivos JSON locales en modelos/{modelo}/metrics.json
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import json
import re

TRAFICO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(TRAFICO_ROOT / "kpi_stripchat"))

router = APIRouter()

# Schemas
class DailyMetric(BaseModel):
    fecha: str
    best_rank: int
    avg_rank: int
    best_gender_rank: int
    avg_gender_rank: int
    most_viewers: int
    avg_viewers: float
    starting_followers: int
    ending_followers: int
    growth: int
    total_segments: int

class MetricsResponse(BaseModel):
    modelo: str
    total_days: int
    date_range: dict
    daily_metrics: List[DailyMetric]
    last_sync: Optional[str] = None

def get_metrics_file_path(modelo: str) -> Path:
    """Obtiene la ruta del archivo de métricas para una modelo"""
    MODELOS_DIR = TRAFICO_ROOT / "modelos"
    modelo_dir = MODELOS_DIR / modelo
    return modelo_dir / "metrics.json"

def load_metrics_from_file(modelo: str) -> dict:
    """Carga las métricas desde el archivo JSON"""
    metrics_file = get_metrics_file_path(modelo)
    
    if not metrics_file.exists():
        return {
            "last_sync": None,
            "metrics": {}
        }
    
    try:
        with open(metrics_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if "metrics" not in data:
                data["metrics"] = {}
            if "last_sync" not in data:
                data["last_sync"] = None
            return data
    except Exception as e:
        print(f"⚠️ Error cargando métricas de {modelo}: {e}")
        return {
            "last_sync": None,
            "metrics": {}
        }

# Importar cliente Supabase solo para verificar modelo
sys.path.insert(0, str(TRAFICO_ROOT / "src"))
from database.supabase_client import supabase

@router.get("/kpi/{modelo}", response_model=MetricsResponse)
async def get_model_metrics(
    modelo: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    days: int = 30
):
    """Obtiene métricas de una modelo desde el archivo JSON local"""
    try:
        # Verificar que el modelo existe
        model_config = supabase.table("modelos").select("*").eq("modelo", modelo).execute()
        if not model_config.data:
            raise HTTPException(status_code=404, detail=f"Modelo '{modelo}' no encontrado")
        
        striphours_url = model_config.data[0].get("striphours_url")
        if not striphours_url:
            raise HTTPException(
                status_code=400, 
                detail="La modelo no tiene URL de Striphours configurada"
            )
        
        # Cargar métricas desde archivo JSON
        metrics_storage = load_metrics_from_file(modelo)
        
        if not metrics_storage.get("metrics"):
            raise HTTPException(
                status_code=404,
                detail="No hay métricas disponibles. El scheduler aún no ha sincronizado datos."
            )
        
        # Calcular fechas (usar UTC para coincidir con la API de Striphours)
        if end_date is None:
            end_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if start_date is None:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            start = end_dt - timedelta(days=days-1)
            start_date = start.strftime("%Y-%m-%d")
        
        # Filtrar métricas por rango de fechas
        all_metrics = metrics_storage["metrics"]
        filtered_metrics = {}
        
        for date_str, metric_data in all_metrics.items():
            if start_date <= date_str <= end_date:
                filtered_metrics[date_str] = metric_data
        
        # Convertir a lista ordenada
        daily_metrics = []
        for date_str in sorted(filtered_metrics.keys(), reverse=True):
            metric_data = filtered_metrics[date_str]
            daily_metrics.append(DailyMetric(
                fecha=date_str,
                best_rank=metric_data.get("best_rank", 0),
                avg_rank=metric_data.get("avg_rank", 0),
                best_gender_rank=metric_data.get("best_gender_rank", 0),
                avg_gender_rank=metric_data.get("avg_gender_rank", 0),
                most_viewers=metric_data.get("most_viewers", 0),
                avg_viewers=float(metric_data.get("avg_viewers", 0)),
                starting_followers=metric_data.get("starting_followers", 0),
                ending_followers=metric_data.get("ending_followers", 0),
                growth=metric_data.get("growth", 0),
                total_segments=metric_data.get("total_segments", 0)
            ))
        
        # Determinar rango real de fechas disponibles
        if daily_metrics:
            actual_start = daily_metrics[-1].fecha
            actual_end = daily_metrics[0].fecha
        else:
            actual_start = start_date
            actual_end = end_date
        
        return MetricsResponse(
            modelo=modelo,
            total_days=len(daily_metrics),
            date_range={"start": actual_start, "end": actual_end},
            daily_metrics=daily_metrics,
            last_sync=metrics_storage.get("last_sync")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo métricas: {str(e)}")

@router.post("/kpi/{modelo}/sync")
async def sync_model_metrics(modelo: str, days: int = 30):
    """
    Sincroniza métricas de una modelo desde la API de Striphours.
    Si es la primera vez, descarga los últimos 30 días.
    Si ya hay datos, actualiza solo el día actual.
    """
    try:
        # Obtener configuración del modelo
        model_config = supabase.table("modelos").select("*").eq("modelo", modelo).execute()
        if not model_config.data:
            raise HTTPException(status_code=404, detail=f"Modelo '{modelo}' no encontrado")
        
        striphours_url = model_config.data[0].get("striphours_url")
        if not striphours_url:
            raise HTTPException(
                status_code=400,
                detail="La modelo no tiene URL de Striphours configurada"
            )
        
        # Importar funciones del scheduler
        sys.path.insert(0, str(TRAFICO_ROOT / "src" / "project"))
        from kpi_scheduler import sync_first_time_model, sync_missing_days, load_metrics
        
        # Importar excepciones de la API
        sys.path.insert(0, str(TRAFICO_ROOT / "kpi_stripchat"))
        from api_wrapper import APIError, ModelNotInDatabaseError
        
        # Verificar si ya hay métricas
        metrics_storage = load_metrics(modelo)
        is_first_time = not metrics_storage.get("metrics")
        
        if is_first_time:
            # Primera vez: descargar últimos 30 días
            try:
                success = sync_first_time_model(modelo, striphours_url)
                if success:
                    return {
                        "success": True,
                        "message": f"Primera sincronización completada (30 días)",
                        "is_first_time": True
                    }
                else:
                    raise HTTPException(
                        status_code=500, 
                        detail="Error en primera sincronización: La función retornó False. Verifica los logs del servidor."
                    )
            except ModelNotInDatabaseError as e:
                raise HTTPException(
                    status_code=404,
                    detail=f"La modelo no está en la base de datos de Striphours: {str(e)}"
                )
            except APIError as e:
                raise HTTPException(
                    status_code=502,
                    detail=f"Error de la API de Striphours: {str(e)}"
                )
        else:
            # Ya hay datos: sincronizar todos los días faltantes desde last_sync hasta hoy (UTC)
            try:
                success = sync_missing_days(modelo, striphours_url)
                if success:
                    # Obtener el nuevo last_sync para mostrar en la respuesta
                    metrics_storage = load_metrics(modelo)
                    last_sync = metrics_storage.get("last_sync", "N/A")
                    return {
                        "success": True,
                        "message": f"Días faltantes sincronizados desde Striphours (UTC)",
                        "synced_date": last_sync,
                        "is_first_time": False
                    }
                else:
                    # No se pudieron sincronizar días (puede ser que no haya datos nuevos)
                    metrics_storage = load_metrics(modelo)
                    last_sync = metrics_storage.get("last_sync", "N/A")
                    return {
                        "success": False,
                        "message": f"No se pudieron sincronizar días nuevos. Última sincronización: {last_sync} (UTC)",
                        "synced_date": last_sync,
                        "is_first_time": False,
                        "no_data": True
                    }
            except ModelNotInDatabaseError as e:
                raise HTTPException(
                    status_code=404,
                    detail=f"La modelo no está en la base de datos de Striphours: {str(e)}"
                )
            except APIError as e:
                raise HTTPException(
                    status_code=502,
                    detail=f"Error de la API de Striphours: {str(e)}"
                )
            except (ValueError, IOError) as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error crítico sincronizando métricas: {str(e)}"
                )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Error inesperado sincronizando métricas para {modelo}:")
        print(error_trace)
        raise HTTPException(
            status_code=500, 
            detail=f"Error sincronizando métricas: {str(e)}. Revisa los logs del servidor para más detalles."
        )



