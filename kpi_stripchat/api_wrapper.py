#!/usr/bin/env python3
"""
Wrapper mejorado para la API de CBHours con rate limiting inteligente
y manejo robusto de errores
"""

import requests
import json
import time
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Any, Optional
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CBHoursAPI:
    """Wrapper para la API de CBHours con rate limiting automático"""
    
    API_BASE_URL = "https://www.cbhours.com/api.php"
    RATE_LIMIT_DELAY = 1.1  # Segundos entre requests
    MAX_DATE_RANGE = 60  # Días máximos permitidos por la API
    
    def __init__(self, timezone_offset: int = -300):
        """
        Inicializa el wrapper de la API
        
        Args:
            timezone_offset: Offset en minutos desde GMT (ej: -300 para Colombia)
        """
        self.timezone_offset = timezone_offset
        self.last_request_time = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CBHours-Dashboard/1.0'
        })
    
    def _wait_for_rate_limit(self):
        """Espera el tiempo necesario para respetar el rate limit"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.RATE_LIMIT_DELAY:
            wait_time = self.RATE_LIMIT_DELAY - time_since_last_request
            logger.debug(f"Rate limit: esperando {wait_time:.2f}s")
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, params: Dict[str, Any]) -> Dict:
        """
        Hace una petición a la API respetando el rate limit
        
        Args:
            params: Parámetros de la petición
            
        Returns:
            Respuesta de la API como diccionario
            
        Raises:
            APIError: Si hay un error en la API
            requests.RequestException: Si hay un error de red
        """
        self._wait_for_rate_limit()
        
        try:
            logger.info(f"Haciendo petición: {params.get('action')} para {params.get('username', 'N/A')}")
            response = self.session.get(
                self.API_BASE_URL,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Verificar si hay error de la API
            if isinstance(data, dict) and data.get('status') == 'error':
                error_msg = data.get('message', 'Error desconocido')
                
                if 'Error Code:300' in error_msg:
                    raise ModelNotInDatabaseError(
                        "La modelo no está en la base de datos. "
                        "Debe tener el ícono de trofeo/calendario en su bio "
                        "y ser buscada en STUDIO search."
                    )
                
                raise APIError(error_msg)
            
            return data
            
        except requests.exceptions.Timeout:
            raise APIError("Timeout: La API no respondió a tiempo")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Error de red: {str(e)}")
        except json.JSONDecodeError:
            raise APIError("La API retornó una respuesta inválida")
    
    def get_activity(
        self,
        domain: str,
        username: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days_back: int = 30,
        include_details: bool = True
    ) -> Dict:
        """
        Obtiene datos de actividad de una modelo
        
        Args:
            domain: cbhours, striphours, o sodahours
            username: Username de la modelo
            start_date: Fecha inicio (YYYY-MM-DD). Si no se especifica, se calcula desde end_date
            end_date: Fecha fin (YYYY-MM-DD). Default: hoy
            days_back: Días hacia atrás si no se especifica start_date
            include_details: Si incluir datos de 3 minutos
            
        Returns:
            Diccionario con los datos de la API
        """
        # Validar dominio
        valid_domains = ['cbhours', 'striphours', 'sodahours']
        if domain.lower() not in valid_domains:
            raise ValueError(f"Dominio inválido. Debe ser uno de: {valid_domains}")
        
        # Calcular fechas si no se especifican
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
        
        if start_date is None:
            end = datetime.strptime(end_date, "%Y-%m-%d")
            start = end - timedelta(days=days_back)
            start_date = start.strftime("%Y-%m-%d")
        
        # Validar rango de fechas
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        date_diff = (end - start).days
        
        if date_diff > self.MAX_DATE_RANGE:
            logger.warning(
                f"Rango de {date_diff} días excede el máximo de {self.MAX_DATE_RANGE}. "
                f"Ajustando start_date."
            )
            start = end - timedelta(days=self.MAX_DATE_RANGE)
            start_date = start.strftime("%Y-%m-%d")
        
        params = {
            'action': 'get_activity',
            'domain': domain.lower(),
            'username': username,
            'start_date': start_date,
            'end_date': end_date,
            'tzo': str(self.timezone_offset),
            'include_details': 'true' if include_details else 'false'
        }
        
        return self._make_request(params)
    
    def get_live_stats(self, usernames: List[str]) -> Dict:
        """
        Obtiene estadísticas en vivo de hasta 50 modelos (solo cbhours)
        
        Args:
            usernames: Lista de usernames (máximo 50)
            
        Returns:
            Diccionario con los datos en vivo
        """
        if len(usernames) > 50:
            raise ValueError("Máximo 50 usernames permitidos")
        
        params = {
            'action': 'get_live',
            'usernames': ','.join(usernames)
        }
        
        return self._make_request(params)
    
    def get_available_months(self, domain: str, username: str) -> List[str]:
        """
        Obtiene los meses disponibles para una modelo
        
        Args:
            domain: cbhours, striphours, o sodahours
            username: Username de la modelo
            
        Returns:
            Lista de meses en formato YYYY-MM
        """
        params = {
            'action': 'get_months',
            'domain': domain.lower(),
            'username': username
        }
        
        result = self._make_request(params)
        return result if isinstance(result, list) else []
    
    def calculate_daily_metrics(self, details: Dict[str, List[Dict]]) -> Dict[str, Dict]:
        """
        Calcula métricas diarias a partir de los detalles
        
        Args:
            details: Diccionario de detalles por fecha
            
        Returns:
            Métricas calculadas por fecha
        """
        daily_metrics = {}
        
        for date_str, segments in details.items():
            if not segments:
                continue
            
            ranks = []
            granks = []
            viewers = []
            
            starting_followers = None
            ending_followers = None
            
            for segment in segments:
                try:
                    rank = int(segment.get("rank", 0))
                    grank = int(segment.get("grank", 0))
                    viewer = int(segment.get("viewers", 0))
                    follower = int(segment.get("followers", 0))
                    
                    if rank > 0:
                        ranks.append(rank)
                    if grank > 0:
                        granks.append(grank)
                    if viewer >= 0:
                        viewers.append(viewer)
                    
                    if follower > 0:
                        if starting_followers is None:
                            starting_followers = follower
                        ending_followers = follower
                        
                except (ValueError, TypeError):
                    continue
            
            # Calcular métricas con exclusión de outliers (10%)
            def calculate_avg_excluding_outliers(values, special_case_length=38):
                if not values:
                    return 0
                
                sorted_values = sorted(values)
                
                if len(sorted_values) == special_case_length:
                    n_exclude = 4
                else:
                    n_exclude = max(0, int(len(sorted_values) * 0.05))
                
                if len(sorted_values) > 2 * n_exclude and n_exclude > 0:
                    filtered = sorted_values[n_exclude:-n_exclude]
                    return sum(filtered) / len(filtered)
                
                return sum(values) / len(values)
            
            daily_metrics[date_str] = {
                "best_rank": min(ranks) if ranks else 0,
                "avg_rank": round(calculate_avg_excluding_outliers(ranks)),
                "best_gender_rank": min(granks) if granks else 0,
                "avg_gender_rank": round(calculate_avg_excluding_outliers(granks)),
                "most_viewers": max(viewers) if viewers else 0,
                "avg_viewers": round(sum(viewers) / len(viewers), 1) if viewers else 0,
                "starting_followers": starting_followers or 0,
                "ending_followers": ending_followers or 0,
                "growth": (ending_followers or 0) - (starting_followers or 0),
                "total_segments": len(segments)
            }
        
        return daily_metrics


class APIError(Exception):
    """Excepción base para errores de la API"""
    pass


class ModelNotInDatabaseError(APIError):
    """Excepción cuando la modelo no está en la base de datos"""
    pass


# Ejemplo de uso
if __name__ == "__main__":
    import sys
    
    # Crear instancia de la API
    api = CBHoursAPI(timezone_offset=-300)
    
    # Obtener username del argumento o input
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = input("Username de la modelo: ").strip()
    
    if not username:
        print("❌ Username requerido")
        sys.exit(1)
    
    try:
        # Obtener datos de actividad
        print(f"\n🔍 Obteniendo datos para {username}...")
        data = api.get_activity(
            domain='striphours',
            username=username,
            days_back=30,
            include_details=True
        )
        
        if not data.get('details'):
            print("⚠️ No hay datos disponibles")
            sys.exit(0)
        
        # Calcular métricas
        print("\n📊 Calculando métricas...")
        metrics = api.calculate_daily_metrics(data['details'])
        
        # Guardar resultados
        output = {
            'username': username,
            'domain': 'striphours',
            'generated_at': datetime.now().isoformat(),
            'date_range': {
                'start': min(metrics.keys()),
                'end': max(metrics.keys())
            },
            'daily_metrics': metrics,
            'raw_details': data['details']
        }
        
        filename = f"metrics_{username}_{min(metrics.keys())}_{max(metrics.keys())}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Datos guardados en: {filename}")
        
        # Mostrar resumen
        print(f"\n📈 Resumen:")
        print(f"   Total de días: {len(metrics)}")
        print(f"   Mejor rank global: {min(m['best_rank'] for m in metrics.values())}")
        print(f"   Crecimiento total: {sum(m['growth'] for m in metrics.values())}")
        
    except ModelNotInDatabaseError as e:
        logger.error(f"❌ {str(e)}")
        sys.exit(1)
    except APIError as e:
        logger.error(f"❌ Error de API: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error inesperado: {str(e)}")
        sys.exit(1)
