"""
KPI Scheduler — Sistema de Métricas Striphours (PRD Puro)
===========================================================

VERSIÓN: 2.0 (PRD)
FECHA: 2025-12-25
ESTADO: DESACTIVADO (migrado a esquema PRD, listo para activación)

DESCRIPCIÓN:
-----------
Scheduler que sincroniza métricas de Striphours para todas las modelos.

- Primera vez: descarga métricas de los últimos 30 días
- Actualización: sincroniza días faltantes + día actual cada 10 minutos
- Almacenamiento: modelos/{nombre_modelo}/metrics.json

ESQUEMA PRD USADO:
-----------------
- modelos.id (UUID PK)
- modelos.nombre (TEXT UNIQUE) → identificador lógico
- modelos.striphours_url (TEXT) → URL de tracking

ZONA HORARIA:
------------
Todas las operaciones usan UTC (datetime.now(timezone.utc)) para coincidir
con el formato de indexación de la API de Striphours.

Ejemplo: "2025-12-25 00:00 UTC" = "2025-12-24 19:00 COT" → ambos son "2025-12-25" en datos

FUNCIONALIDAD:
-------------
1. sync_first_time_model() → Descarga últimos 30 días (primera vez)
2. sync_missing_days() → Sincroniza días faltantes desde last_sync
3. sync_model_metrics_single_day() → Actualiza un día específico
4. sync_today_all_models() → Actualiza día actual de todas las modelos
5. check_and_sync_new_models() → Detecta y sincroniza modelos nuevas

DEPENDENCIAS EXTERNAS:
---------------------
- kpi_stripchat/api_wrapper.py → CBHoursAPI
- src/database/supabase_client.py → Cliente Supabase (PRD)

CÓMO ACTIVAR:
------------
1. Verificar que modelos tienen striphours_url configurado
2. Descomentar líneas en main.py
3. Reiniciar servicios

NO HACE:
-------
- NO crea tablas dinámicas
- NO usa modelos.modelo (legacy)
- NO infiere estructura
- Solo lectura de modelos, escritura de archivos JSON locales

REFERENCIAS:
-----------
- Migracion/FASE5_CIERRE_OFICIAL.md
- Migracion/FASE6_OPCION_B_KPI_MIGRADO.md
"""

import os
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

# Imports de módulos externos
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR / "kpi_stripchat"))
from api_wrapper import CBHoursAPI, APIError, ModelNotInDatabaseError

sys.path.insert(0, str(BASE_DIR / "src"))
from database.supabase_client import supabase


# =============================================================================
# HELPERS DE ARCHIVO
# =============================================================================

def extract_username_from_url(url: str) -> str | None:
    """
    Extrae el username de una URL de striphours.
    
    Args:
        url: URL completa (ej: https://striphours.com/user/demo)
    
    Returns:
        Username extraído o None si no se encuentra
    """
    import re
    if not url:
        return None
    pattern = r'striphours\.com/user/([^/?#]+)'
    match = re.search(pattern, url)
    return match.group(1) if match else None


def get_metrics_file_path(nombre_modelo: str) -> Path:
    """
    Obtiene la ruta del archivo de métricas para una modelo.
    
    Args:
        nombre_modelo: Nombre de la modelo (modelos.nombre)
    
    Returns:
        Path al archivo metrics.json
    """
    MODELOS_DIR = BASE_DIR / "modelos"
    modelo_dir = MODELOS_DIR / nombre_modelo
    modelo_dir.mkdir(parents=True, exist_ok=True)
    return modelo_dir / "metrics.json"


def load_metrics(nombre_modelo: str) -> dict:
    """
    Carga las métricas desde el archivo JSON.
    
    Args:
        nombre_modelo: Nombre de la modelo
    
    Returns:
        Dict con estructura: {"last_sync": str, "metrics": dict}
    """
    metrics_file = get_metrics_file_path(nombre_modelo)
    
    if not metrics_file.exists():
        return {
            "last_sync": None,
            "metrics": {}
        }
    
    try:
        with open(metrics_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Asegurar estructura correcta
            if "metrics" not in data:
                data["metrics"] = {}
            if "last_sync" not in data:
                data["last_sync"] = None
            return data
    except Exception as e:
        print(f"⚠️ Error cargando métricas de {nombre_modelo}: {e}")
        return {
            "last_sync": None,
            "metrics": {}
        }


def save_metrics(nombre_modelo: str, metrics_data: dict) -> bool:
    """
    Guarda las métricas en el archivo JSON.
    
    Args:
        nombre_modelo: Nombre de la modelo
        metrics_data: Dict con métricas
    
    Returns:
        True si se guardó exitosamente, False en caso de error
    """
    metrics_file = get_metrics_file_path(nombre_modelo)
    
    try:
        with open(metrics_file, 'w', encoding='utf-8') as f:
            json.dump(metrics_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Error guardando métricas de {nombre_modelo}: {e}")
        return False


# =============================================================================
# SINCRONIZACIÓN DE MÉTRICAS
# =============================================================================

def sync_model_metrics_single_day(nombre_modelo: str, date_str: str, striphours_url: str) -> bool:
    """
    Sincroniza métricas de una modelo para un día específico.
    
    Args:
        nombre_modelo: Nombre de la modelo
        date_str: Fecha en formato YYYY-MM-DD (UTC)
        striphours_url: URL de Striphours de la modelo
    
    Returns:
        True si se sincronizó exitosamente
        False si no hay datos disponibles
    
    Raises:
        ModelNotInDatabaseError: Si la modelo no está en Striphours
        APIError: Si hay error de API
        ValueError: Si no se puede extraer username
        IOError: Si hay error guardando métricas
    """
    try:
        username = extract_username_from_url(striphours_url)
        if not username:
            print(f"❌ {nombre_modelo}: No se pudo extraer username de la URL: {striphours_url}")
            raise ValueError(f"No se pudo extraer username de la URL: {striphours_url}")
        
        print(f"📥 Sincronizando {nombre_modelo} para {date_str}...")
        
        # Llamar a la API para ese día específico
        api = CBHoursAPI(timezone_offset=-300)
        data = api.get_activity(
            domain='striphours',
            username=username,
            start_date=date_str,
            end_date=date_str,
            include_details=True
        )
        
        if not data.get('details'):
            print(f"⚠️ {nombre_modelo}: No hay detalles disponibles para {date_str}")
            return False
        
        if date_str not in data['details']:
            print(f"⚠️ {nombre_modelo}: La fecha {date_str} no está en los detalles de la respuesta")
            return False
        
        # Calcular métricas diarias
        metrics = api.calculate_daily_metrics(data['details'])
        
        if date_str not in metrics:
            print(f"⚠️ {nombre_modelo}: No se pudieron calcular métricas para {date_str}")
            return False
        
        metric_data = metrics[date_str]
        
        # Cargar métricas existentes
        metrics_storage = load_metrics(nombre_modelo)
        
        # Actualizar métrica del día
        metrics_storage["metrics"][date_str] = {
            "best_rank": metric_data["best_rank"],
            "avg_rank": metric_data["avg_rank"],
            "best_gender_rank": metric_data["best_gender_rank"],
            "avg_gender_rank": metric_data["avg_gender_rank"],
            "most_viewers": metric_data["most_viewers"],
            "avg_viewers": metric_data["avg_viewers"],
            "starting_followers": metric_data["starting_followers"],
            "ending_followers": metric_data["ending_followers"],
            "growth": metric_data["growth"],
            "total_segments": metric_data["total_segments"],
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Actualizar last_sync
        metrics_storage["last_sync"] = date_str
        
        # Guardar
        if save_metrics(nombre_modelo, metrics_storage):
            print(f"✅ {nombre_modelo}: Métricas de {date_str} sincronizadas exitosamente")
            return True
        else:
            print(f"❌ {nombre_modelo}: Error guardando métricas para {date_str}")
            raise IOError(f"Error guardando métricas para {date_str}")
        
    except ModelNotInDatabaseError as e:
        print(f"⚠️ {nombre_modelo} no está en la base de datos de Striphours: {e}")
        raise
    except APIError as e:
        print(f"❌ Error de API para {nombre_modelo}: {e}")
        raise
    except (ValueError, IOError) as e:
        print(f"❌ Error crítico sincronizando {nombre_modelo} para {date_str}: {e}")
        raise
    except Exception as e:
        print(f"❌ Error inesperado sincronizando {nombre_modelo} para {date_str}: {e}")
        import traceback
        traceback.print_exc()
        raise


def sync_missing_days(nombre_modelo: str, striphours_url: str) -> bool:
    """
    Sincroniza todos los días faltantes desde last_sync hasta hoy.
    Solo agrega datos, no borra nada existente.
    
    Args:
        nombre_modelo: Nombre de la modelo
        striphours_url: URL de Striphours
    
    Returns:
        True si se sincronizó exitosamente, False en caso de error
    """
    try:
        # Cargar métricas existentes para obtener last_sync
        metrics_storage = load_metrics(nombre_modelo)
        last_sync = metrics_storage.get("last_sync")
        
        if not last_sync:
            # Si no hay last_sync, hacer primera sincronización
            return sync_first_time_model(nombre_modelo, striphours_url)
        
        # Calcular días faltantes (usando UTC)
        last_date = datetime.strptime(last_sync, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        today_utc = datetime.now(timezone.utc)
        
        # Si last_sync es hoy o futuro, no hay nada que sincronizar
        if last_date.date() >= today_utc.date():
            print(f"ℹ️ {nombre_modelo}: Ya está sincronizado hasta {last_sync}")
            return True
        
        # Calcular días a sincronizar (desde last_sync + 1 hasta hoy en UTC)
        days_to_sync = []
        current_date = last_date + timedelta(days=1)
        while current_date.date() <= today_utc.date():
            days_to_sync.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)
        
        if not days_to_sync:
            print(f"ℹ️ {nombre_modelo}: No hay días nuevos para sincronizar")
            return True
        
        print(f"📥 Sincronizando {len(days_to_sync)} días faltantes para {nombre_modelo} (desde {days_to_sync[0]} hasta {days_to_sync[-1]})...")
        
        username = extract_username_from_url(striphours_url)
        if not username:
            raise ValueError(f"No se pudo extraer username de la URL: {striphours_url}")
        
        # Hacer una petición por rango para obtener todos los días faltantes
        start_date = days_to_sync[0]
        end_date = days_to_sync[-1]
        
        print(f"📥 Obteniendo datos de Striphours para {nombre_modelo} desde {start_date} hasta {end_date}...")
        api = CBHoursAPI(timezone_offset=-300)
        data = api.get_activity(
            domain='striphours',
            username=username,
            start_date=start_date,
            end_date=end_date,
            include_details=True
        )
        
        if not data.get('details'):
            print(f"⚠️ {nombre_modelo}: No hay detalles disponibles para el rango {start_date} a {end_date}")
            return False
        
        # Calcular métricas diarias
        metrics = api.calculate_daily_metrics(data['details'])
        
        # Cargar métricas existentes (para no borrar nada)
        metrics_storage = load_metrics(nombre_modelo)
        
        # Agregar solo los días que faltan
        synced_count = 0
        last_processed_date = last_sync
        last_successful_date = last_sync
        
        for date_str in days_to_sync:
            last_processed_date = date_str
            if date_str in metrics:
                metric_data = metrics[date_str]
                metrics_storage["metrics"][date_str] = {
                    "best_rank": metric_data["best_rank"],
                    "avg_rank": metric_data["avg_rank"],
                    "best_gender_rank": metric_data["best_gender_rank"],
                    "avg_gender_rank": metric_data["avg_gender_rank"],
                    "most_viewers": metric_data["most_viewers"],
                    "avg_viewers": metric_data["avg_viewers"],
                    "starting_followers": metric_data["starting_followers"],
                    "ending_followers": metric_data["ending_followers"],
                    "growth": metric_data["growth"],
                    "total_segments": metric_data["total_segments"],
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                synced_count += 1
                last_successful_date = date_str
                print(f"✅ {date_str} sincronizado")
            else:
                print(f"⚠️ {date_str} no disponible en la respuesta de la API")
        
        # Actualizar last_sync al último día procesado
        if days_to_sync:
            metrics_storage["last_sync"] = last_processed_date
            if save_metrics(nombre_modelo, metrics_storage):
                if synced_count > 0:
                    print(f"✅ {nombre_modelo}: {synced_count} días sincronizados (hasta {last_successful_date})")
                else:
                    print(f"⚠️ {nombre_modelo}: No se encontraron datos nuevos en el rango")
                return True
            else:
                print(f"❌ {nombre_modelo}: Error guardando métricas")
                return False
        else:
            print(f"⚠️ {nombre_modelo}: No hay días para sincronizar")
            return False
        
    except ModelNotInDatabaseError as e:
        print(f"⚠️ {nombre_modelo} no está en la base de datos de Striphours: {e}")
        raise
    except APIError as e:
        print(f"❌ Error de API para {nombre_modelo}: {e}")
        raise
    except Exception as e:
        print(f"❌ Error sincronizando días faltantes para {nombre_modelo}: {e}")
        import traceback
        traceback.print_exc()
        raise


def sync_first_time_model(nombre_modelo: str, striphours_url: str) -> bool:
    """
    Sincroniza los últimos 30 días para una modelo (primera vez).
    
    Args:
        nombre_modelo: Nombre de la modelo
        striphours_url: URL de Striphours
    
    Returns:
        True si se sincronizó exitosamente, False en caso de error
    """
    try:
        username = extract_username_from_url(striphours_url)
        if not username:
            print(f"  ⚠️ {nombre_modelo}: No se pudo extraer username de la URL")
            return False
        
        print(f"📥 Descargando últimos 30 días para {nombre_modelo}...")
        
        # Usar UTC para coincidir con la API de Striphours
        now_utc = datetime.now(timezone.utc)
        end_date = now_utc.strftime("%Y-%m-%d")
        start_date = (now_utc - timedelta(days=29)).strftime("%Y-%m-%d")
        
        api = CBHoursAPI(timezone_offset=-300)
        data = api.get_activity(
            domain='striphours',
            username=username,
            start_date=start_date,
            end_date=end_date,
            include_details=True
        )
        
        if not data.get('details'):
            print(f"  ⚠️ {nombre_modelo}: Sin datos disponibles")
            return False
        
        metrics = api.calculate_daily_metrics(data['details'])
        
        # Cargar métricas existentes (por si acaso ya hay algo)
        metrics_storage = load_metrics(nombre_modelo)
        
        # Agregar todas las métricas
        synced_count = 0
        for date_str, metric_data in metrics.items():
            metrics_storage["metrics"][date_str] = {
                "best_rank": metric_data["best_rank"],
                "avg_rank": metric_data["avg_rank"],
                "best_gender_rank": metric_data["best_gender_rank"],
                "avg_gender_rank": metric_data["avg_gender_rank"],
                "most_viewers": metric_data["most_viewers"],
                "avg_viewers": metric_data["avg_viewers"],
                "starting_followers": metric_data["starting_followers"],
                "ending_followers": metric_data["ending_followers"],
                "growth": metric_data["growth"],
                "total_segments": metric_data["total_segments"],
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            synced_count += 1
        
        # Actualizar last_sync
        metrics_storage["last_sync"] = end_date
        
        # Guardar
        if save_metrics(nombre_modelo, metrics_storage):
            print(f"  ✅ {nombre_modelo}: {synced_count} días sincronizados ({start_date} a {end_date})")
            return True
        else:
            print(f"  ❌ {nombre_modelo}: Error guardando métricas")
            return False
        
    except ModelNotInDatabaseError as e:
        print(f"  ⚠️ {nombre_modelo} no está en la base de datos de Striphours: {e}")
        return False
    except APIError as e:
        print(f"  ❌ Error de API para {nombre_modelo}: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error sincronizando {nombre_modelo}: {e}")
        import traceback
        traceback.print_exc()
        return False


# =============================================================================
# ORCHESTRATORS
# =============================================================================

def sync_today_all_models():
    """
    Actualiza métricas del día actual de todas las modelos.
    
    Query PRD: SELECT id, nombre, striphours_url FROM modelos WHERE striphours_url IS NOT NULL
    """
    try:
        # Usar UTC para coincidir con la API de Striphours
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        # Query PRD: Usar nombre en lugar de modelo
        models = supabase.table("modelos")\
            .select("id, nombre, striphours_url")\
            .not_.is_("striphours_url", "null")\
            .execute()
        
        if not models.data:
            return
        
        synced = 0
        for model in models.data:
            nombre_modelo = model["nombre"]
            striphours_url = model["striphours_url"]
            
            if sync_model_metrics_single_day(nombre_modelo, today, striphours_url):
                synced += 1
        
        if synced > 0:
            print(f"🔄 Día actual actualizado: {synced}/{len(models.data)} modelos ({today})")
        
    except Exception as e:
        print(f"❌ Error actualizando día actual: {e}")
        import traceback
        traceback.print_exc()


def check_and_sync_new_models():
    """
    Verifica si hay modelos nuevas sin métricas y las sincroniza (primera vez).
    
    Query PRD: SELECT id, nombre, striphours_url FROM modelos WHERE striphours_url IS NOT NULL
    """
    try:
        # Query PRD: Usar nombre en lugar de modelo
        models = supabase.table("modelos")\
            .select("id, nombre, striphours_url")\
            .not_.is_("striphours_url", "null")\
            .execute()
        
        if not models.data:
            return
        
        new_models = []
        for model in models.data:
            nombre_modelo = model["nombre"]
            striphours_url = model["striphours_url"]
            
            # Verificar si ya tiene métricas (archivo existe y tiene datos)
            metrics_storage = load_metrics(nombre_modelo)
            if not metrics_storage.get("metrics"):
                # No tiene métricas, es primera vez
                new_models.append((nombre_modelo, striphours_url))
        
        if new_models:
            print(f"🆕 Encontradas {len(new_models)} modelos nuevas sin métricas")
            for nombre_modelo, striphours_url in new_models:
                sync_first_time_model(nombre_modelo, striphours_url)
                # Esperar un poco entre modelos para respetar rate limit
                time.sleep(1.2)
        
    except Exception as e:
        print(f"❌ Error verificando modelos nuevas: {e}")
        import traceback
        traceback.print_exc()


# =============================================================================
# MAIN LOOP
# =============================================================================

def main():
    """
    Función principal del scheduler.
    
    - Verifica modelos nuevas al iniciar
    - Actualiza día actual cada 10 minutos
    - Verifica modelos nuevas cada hora
    """
    print("🚀 Iniciando KPI Scheduler (PRD)...")
    print("   - Primera vez: últimos 30 días")
    print("   - Día actual: cada 10 minutos")
    print("   - Guardado en: modelos/{nombre}/metrics.json")
    print("   - Esquema: modelos.nombre (PRD)\n")
    
    # Verificar modelos nuevas al iniciar
    check_and_sync_new_models()
    
    last_today_sync = None
    
    while True:
        # Usar UTC para coincidir con la API de Striphours
        now = datetime.now(timezone.utc)
        
        # Actualizar día actual cada 10 minutos
        if last_today_sync is None or (now - last_today_sync).total_seconds() >= 600:
            sync_today_all_models()
            last_today_sync = now
        
        # Verificar modelos nuevas cada hora
        if now.minute == 0:
            check_and_sync_new_models()
            time.sleep(60)  # Esperar 1 minuto para no ejecutar múltiples veces
        
        # Esperar 1 minuto antes de verificar de nuevo
        time.sleep(60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 KPI Scheduler detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error fatal en KPI Scheduler: {e}")
        import traceback
        traceback.print_exc()
