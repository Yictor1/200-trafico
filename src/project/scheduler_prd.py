#!/usr/bin/env python3
"""
Scheduler PRD - Esquema PRD
Lee contenidos y crea publicaciones programadas.
Usa exclusivamente el esquema PRD (contenidos, publicaciones, cuentas_plataforma, etc.)
"""

import os
import random
import datetime as dt
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from datetime import datetime, timezone, timedelta
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cargar variables de entorno
BASE_DIR = Path(__file__).resolve().parents[2]
env_path = BASE_DIR / 'src' / '.env'
load_dotenv(dotenv_path=env_path)

# Configuración Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_ANON_KEY")

if not url or not key:
    raise ValueError(f"Faltan credenciales de Supabase en .env ({env_path})")

supabase: Client = create_client(url, key)

# Variables de entorno
MIN_GAP_MINUTES = int(os.getenv("MIN_GAP_MINUTES", "10"))
MAX_DAYS_AHEAD = int(os.getenv("MAX_DAYS_AHEAD", "30"))
MAX_SAME_VIDEO = int(os.getenv("MAX_SAME_VIDEO", "6"))


def now_tz() -> dt.datetime:
    """Retorna datetime actual en timezone de Colombia (UTC-5)"""
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=-5)))


def parse_dt_local(s: str) -> dt.datetime:
    """Parsea datetime desde string formato 'YYYY-MM-DD HH:MM:SS' en zona Bogotá"""
    y, mo, d = int(s[0:4]), int(s[5:7]), int(s[8:10])
    H, M, S = int(s[11:13]), int(s[14:16]), int(s[17:19])
    return dt.datetime(y, mo, d, H, M, S, tzinfo=dt.timezone(dt.timedelta(hours=-5)))


def fmt_dt_local(x: dt.datetime) -> str:
    """Formatea datetime a string 'YYYY-MM-DD HH:MM:SS'"""
    return x.strftime("%Y-%m-%d %H:%M:%S")


def get_pending_contenidos() -> List[Dict]:
    """
    Obtiene contenidos pendientes de procesar.
    Solo contenidos con estado = 'nuevo'
    """
    try:
        response = supabase.table('contenidos')\
            .select("*, modelos(*)")\
            .eq('estado', 'nuevo')\
            .order('recibido_at', desc=False)\
            .execute()
        
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"❌ Error obteniendo contenidos: {e}")
        return []


def check_idempotencia(contenido_id: str) -> bool:
    """
    Verifica si el contenido ya tiene publicaciones creadas.
    Retorna True si ya tiene publicaciones (idempotencia)
    """
    try:
        existing = supabase.table('publicaciones')\
            .select("id")\
            .eq('contenido_id', contenido_id)\
            .in_('estado', ['programada', 'procesando', 'publicado'])\
            .execute()
        
        return len(existing.data) > 0 if existing.data else False
    except Exception as e:
        logger.error(f"❌ Error verificando idempotencia: {e}")
        return False


def check_limits(contenido_id: str) -> bool:
    """
    Verifica si el contenido alcanzó el límite MAX_SAME_VIDEO.
    Retorna True si alcanzó el límite
    """
    try:
        count_response = supabase.table('publicaciones')\
            .select("id", count="exact")\
            .eq('contenido_id', contenido_id)\
            .execute()
        
        count = count_response.count if hasattr(count_response, 'count') else len(count_response.data) if count_response.data else 0
        return count >= MAX_SAME_VIDEO
    except Exception as e:
        logger.error(f"❌ Error verificando límites: {e}")
        return False


def get_cuentas_plataforma(modelo_id: str, plataformas_nombres: List[str]) -> List[Dict]:
    """
    Obtiene cuentas_plataforma válidas para un modelo y lista de plataformas.
    Solo plataformas activas y que estén en la lista.
    """
    try:
        # Obtener todas las cuentas del modelo
        cuentas = supabase.table('cuentas_plataforma')\
            .select("id, plataforma_id, plataformas!inner(nombre, activa)")\
            .eq('modelo_id', modelo_id)\
            .execute()
        
        if not cuentas.data:
            return []
        
        # Filtrar por plataformas activas y en la lista
        cuentas_validas = []
        for cuenta in cuentas.data:
            plataforma = cuenta.get('plataformas', {})
            if isinstance(plataforma, dict):
                nombre = plataforma.get('nombre', '').lower()
                activa = plataforma.get('activa', False)
                if activa and nombre in [p.lower() for p in plataformas_nombres]:
                    cuentas_validas.append({
                        'id': cuenta['id'],
                        'plataforma_id': cuenta['plataforma_id'],
                        'plataforma_nombre': nombre
                    })
        
        return cuentas_validas
    except Exception as e:
        logger.error(f"❌ Error obteniendo cuentas_plataforma: {e}")
        return []


def _within_window(candidate: dt.datetime, start: dt.datetime, end: dt.datetime) -> bool:
    """Verifica si candidate está dentro de la ventana [start, end]"""
    return start <= candidate <= end


def _valid_gap(candidate: dt.datetime, others: List[dt.datetime], gap_min: int) -> bool:
    """Verifica si candidate tiene gap mínimo con otros slots"""
    for h in others:
        if abs((candidate - h).total_seconds()) < gap_min * 60:
            return False
    return True


def _build_slots_for_day(n: int, start: dt.datetime, hours: int, occupied: List[dt.datetime]) -> List[dt.datetime]:
    """
    Construye N slots distribuidos en una ventana de horas.
    Hereda lógica del scheduler antiguo.
    """
    gap = MIN_GAP_MINUTES
    end = start + dt.timedelta(hours=hours)
    
    proposals: List[dt.datetime] = []
    now_local = now_tz()
    
    # 1) Primer slot cerca de inicio
    if n >= 1:
        jitter = dt.timedelta(minutes=random.randint(0, 5))
        c = (start + jitter).replace(second=0, microsecond=0)
        if _within_window(c, start, end) and _valid_gap(c, occupied + proposals, gap) and c >= now_local:
            proposals.append(c)
    
    # 2) Segundo slot cerca de fin
    if n >= 2:
        jitter = dt.timedelta(minutes=random.randint(0, 5))
        c = (end - jitter).replace(second=0, microsecond=0)
        if _within_window(c, start, end) and _valid_gap(c, occupied + proposals, gap) and c >= now_local:
            proposals.append(c)
    
    # 3) Midpoint entre 1 y 2
    if n >= 3 and len(proposals) >= 2:
        a, b = sorted(proposals)[0], sorted(proposals)[-1]
        c = (a + (b - a) / 2).replace(second=0, microsecond=0)
        if _within_window(c, start, end) and _valid_gap(c, occupied + proposals, gap) and c >= now_local:
            proposals.append(c)
    
    # 4) Midpoints válidos entre ocupados + propuestos (≥ 2×gap)
    def midpoints_fill():
        nonlocal proposals
        timeline = sorted(occupied + proposals)
        made = 0
        for i in range(len(timeline) - 1):
            a, b = timeline[i], timeline[i + 1]
            if (b - a) >= dt.timedelta(minutes=2 * gap):
                c = (a + (b - a) / 2).replace(second=0, microsecond=0)
                if _within_window(c, start, end) and _valid_gap(c, occupied + proposals, gap) and c >= now_local:
                    proposals.append(c)
                    made += 1
                    if len(proposals) >= n:
                        break
        return made
    
    while len(proposals) < n and midpoints_fill() > 0:
        pass
    
    # 5) Relleno hacia adelante en pasos de gap
    t = start
    while len(proposals) < n:
        t = t.replace(second=0, microsecond=0)
        if _within_window(t, start, end) and _valid_gap(t, occupied + proposals, gap) and t >= now_local:
            proposals.append(t)
        t += dt.timedelta(minutes=gap)
        if t > end:
            break
    
    return sorted(proposals)[:n]


def _distinct_contenidos_on_date(modelo_id: str, date_str: str) -> int:
    """
    Cuenta contenidos distintos que tienen publicaciones en una fecha.
    Adaptado para PRD: lee de publicaciones en lugar de tabla dinámica.
    """
    try:
        # Obtener publicaciones del modelo en esa fecha
        fecha_inicio = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone(timedelta(hours=-5)))
        fecha_fin = fecha_inicio + timedelta(days=1)
        
        publicaciones = supabase.table('publicaciones')\
            .select("contenido_id")\
            .gte('scheduled_time', fecha_inicio.isoformat())\
            .lt('scheduled_time', fecha_fin.isoformat())\
            .in_('estado', ['programada', 'procesando', 'publicado'])\
            .execute()
        
        if not publicaciones.data:
            return 0
        
        # Obtener contenidos únicos (verificar que pertenecen al modelo)
        contenido_ids = set()
        for pub in publicaciones.data:
            contenido_id = pub.get('contenido_id')
            if contenido_id:
                # Verificar que el contenido pertenece al modelo
                contenido = supabase.table('contenidos').select("modelo_id").eq('id', contenido_id).execute()
                if contenido.data and contenido.data[0].get('modelo_id') == modelo_id:
                    contenido_ids.add(contenido_id)
        
        return len(contenido_ids)
    except Exception as e:
        logger.error(f"❌ Error contando contenidos distintos: {e}")
        return 0


def _occupied_on_date(modelo_id: str, date_str: str) -> List[dt.datetime]:
    """
    Obtiene slots ocupados en una fecha para un modelo.
    Adaptado para PRD: lee de publicaciones.
    """
    try:
        fecha_inicio = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone(timedelta(hours=-5)))
        fecha_fin = fecha_inicio + timedelta(days=1)
        
        publicaciones = supabase.table('publicaciones')\
            .select("scheduled_time, contenidos!inner(modelo_id)")\
            .gte('scheduled_time', fecha_inicio.isoformat())\
            .lt('scheduled_time', fecha_fin.isoformat())\
            .in_('estado', ['programada', 'procesando', 'publicado'])\
            .execute()
        
        if not publicaciones.data:
            return []
        
        occupied = []
        for pub in publicaciones.data:
            contenido = pub.get('contenidos', {})
            if isinstance(contenido, dict) and contenido.get('modelo_id') == modelo_id:
                st = pub.get('scheduled_time')
                if st:
                    try:
                        # Parsear ISO format a datetime
                        if isinstance(st, str):
                            dt_obj = datetime.fromisoformat(st.replace('Z', '+00:00'))
                            # Convertir a timezone local
                            if dt_obj.tzinfo is None:
                                dt_obj = dt_obj.replace(tzinfo=timezone.utc)
                            dt_obj = dt_obj.astimezone(timezone(timedelta(hours=-5)))
                            occupied.append(dt_obj)
                    except:
                        pass
        
        return sorted(occupied)
    except Exception as e:
        logger.error(f"❌ Error obteniendo slots ocupados: {e}")
        return []


def calculate_scheduled_times(modelo_id: str, n_plataformas: int, hora_inicio: str, ventana_horas: int) -> List[dt.datetime]:
    """
    Calcula scheduled_times distribuidos para N plataformas.
    Busca desde hoy hasta MAX_DAYS_AHEAD días.
    """
    H, M = [int(x) for x in hora_inicio.split(":")]
    tz = dt.timezone(dt.timedelta(hours=-5))
    today = now_tz().date()
    
    # Búsqueda hasta MAX_DAYS_AHEAD
    for day_offset in range(MAX_DAYS_AHEAD + 1):
        date_obj = today + dt.timedelta(days=day_offset)
        date_str = date_obj.strftime("%Y-%m-%d")
        
        # Capacidad por día (3 videos distintos)
        if _distinct_contenidos_on_date(modelo_id, date_str) >= 3:
            continue
        
        start = dt.datetime(date_obj.year, date_obj.month, date_obj.day, H, M, 0, tzinfo=tz)
        end = start + dt.timedelta(hours=ventana_horas)
        
        # Regla: hoy si aún no pasó hora_inicio; si ya pasó, hoy igual pero respetando ahora≥inicio
        if day_offset == 0:
            now_local = now_tz()
            if now_local > end:
                # la ventana de hoy ya pasó
                continue
        
        occupied = _occupied_on_date(modelo_id, date_str)
        times = _build_slots_for_day(n_plataformas, start, ventana_horas, occupied)
        
        if len(times) == n_plataformas:
            # Éxito: retornar times
            return times
    
    # No se encontró espacio
    raise ValueError("sin_espacio")


def create_publicaciones(contenido: Dict, cuentas: List[Dict], scheduled_times: List[dt.datetime]) -> bool:
    """
    Crea publicaciones para un contenido.
    Retorna True si todas se crean exitosamente.
    """
    contenido_id = contenido['id']
    caption = contenido.get('caption_generado', '') or ''
    tags = contenido.get('tags_generados', []) or []
    
    if len(cuentas) != len(scheduled_times):
        logger.error(f"❌ Mismatch: {len(cuentas)} cuentas vs {len(scheduled_times)} scheduled_times")
        return False
    
    try:
        for cuenta, scheduled_time in zip(cuentas, scheduled_times):
            data = {
                "contenido_id": contenido_id,
                "cuenta_plataforma_id": cuenta['id'],
                "scheduled_time": scheduled_time.isoformat(),
                "caption_usado": caption,
                "tags_usados": tags if isinstance(tags, list) else [],
                "estado": "programada",
                "intentos": 0
            }
            
            supabase.table('publicaciones').insert(data).execute()
            logger.info(f"   ✅ Publicación creada: {cuenta['plataforma_nombre']} @ {fmt_dt_local(scheduled_time)}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error creando publicaciones: {e}")
        import traceback
        traceback.print_exc()
        return False


def update_contenido_estado(contenido_id: str, estado: str) -> bool:
    """Actualiza el estado de un contenido"""
    try:
        supabase.table('contenidos')\
            .update({"estado": estado})\
            .eq('id', contenido_id)\
            .execute()
        return True
    except Exception as e:
        logger.error(f"❌ Error actualizando estado del contenido: {e}")
        return False


def process_contenido(contenido: Dict) -> bool:
    """
    Procesa un contenido completo:
    1. Verifica idempotencia
    2. Verifica límites
    3. Obtiene configuración
    4. Obtiene cuentas
    5. Calcula scheduled_times
    6. Crea publicaciones
    7. Marca contenido como 'aprobado'
    
    Retorna True si se procesó exitosamente
    """
    contenido_id = contenido['id']
    archivo_path = contenido.get('archivo_path', 'N/A')
    
    logger.info(f"\n🔄 Procesando contenido: {archivo_path}")
    
    # 1. Verificar idempotencia
    if check_idempotencia(contenido_id):
        logger.info(f"   ℹ️  Contenido ya tiene publicaciones (idempotencia)")
        return False
    
    # 2. Verificar límites
    if check_limits(contenido_id):
        logger.warning(f"   ⚠️  Contenido alcanzó tope (MAX_SAME_VIDEO={MAX_SAME_VIDEO})")
        return False
    
    # 3. Obtener modelo y configuración
    modelo = contenido.get('modelos')
    if not modelo or not isinstance(modelo, dict):
        logger.error(f"   ❌ Modelo no encontrado en relación")
        return False
    
    modelo_id = modelo.get('id')
    modelo_nombre = modelo.get('nombre', 'N/A')
    config = modelo.get('configuracion_distribucion', {})
    
    if not isinstance(config, dict):
        logger.error(f"   ❌ Configuración inválida")
        return False
    
    plataformas = config.get('plataformas', [])
    hora_inicio = config.get('hora_inicio', '12:00')
    ventana_horas = config.get('ventana_horas', 5)
    
    if not plataformas or not isinstance(plataformas, list):
        logger.warning(f"   ⚠️  Modelo '{modelo_nombre}' no tiene plataformas configuradas")
        return False
    
    # 4. Obtener cuentas_plataforma válidas
    cuentas = get_cuentas_plataforma(modelo_id, plataformas)
    
    if not cuentas:
        logger.warning(f"   ⚠️  No hay cuentas_plataforma válidas para plataformas: {', '.join(plataformas)}")
        return False
    
    if len(cuentas) != len(plataformas):
        logger.warning(f"   ⚠️  Solo {len(cuentas)}/{len(plataformas)} cuentas disponibles")
        # Continuar con las cuentas disponibles
    
    # 5. Calcular scheduled_times
    try:
        scheduled_times = calculate_scheduled_times(modelo_id, len(cuentas), hora_inicio, ventana_horas)
        logger.info(f"   ✅ {len(scheduled_times)} slots calculados")
    except ValueError as e:
        if str(e) == "sin_espacio":
            logger.warning(f"   ⚠️  No hay espacio en ventana (hasta {MAX_DAYS_AHEAD} días)")
        else:
            logger.error(f"   ❌ Error calculando slots: {e}")
        return False
    except Exception as e:
        logger.error(f"   ❌ Error calculando slots: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 6. Crear publicaciones
    if not create_publicaciones(contenido, cuentas, scheduled_times):
        logger.error(f"   ❌ Error creando publicaciones")
        return False
    
    # 7. Marcar contenido como 'aprobado' (solo si todo fue exitoso)
    if update_contenido_estado(contenido_id, 'aprobado'):
        logger.info(f"   ✅ Contenido marcado como 'aprobado'")
        return True
    else:
        logger.error(f"   ❌ Error actualizando estado del contenido")
        return False


def main():
    """
    Loop principal del scheduler.
    Lee contenidos y crea publicaciones.
    """
    logger.info("🚀 Iniciando Scheduler PRD")
    logger.info("=" * 60)
    
    while True:
        try:
            # Obtener contenidos pendientes
            contenidos = get_pending_contenidos()
            
            if contenidos:
                logger.info(f"\n📬 {len(contenidos)} contenido(s) pendiente(s) encontrado(s)")
                
                procesados = 0
                saltados = 0
                
                for contenido in contenidos:
                    if process_contenido(contenido):
                        procesados += 1
                    else:
                        saltados += 1
                
                logger.info(f"\n📊 Resumen: {procesados} procesados, {saltados} saltados")
            else:
                logger.info("💤 No hay contenidos pendientes. Esperando...")
            
            # Esperar antes de la siguiente iteración
            logger.info(f"\n💤 Esperando 60 segundos...")
            import time
            time.sleep(60)
            
        except KeyboardInterrupt:
            logger.info("\n🛑 Deteniendo scheduler...")
            break
        except Exception as e:
            logger.error(f"❌ Error en loop principal: {e}")
            import traceback
            traceback.print_exc()
            logger.info("💤 Reintentando en 60 segundos...")
            import time
            time.sleep(60)


if __name__ == "__main__":
    main()



