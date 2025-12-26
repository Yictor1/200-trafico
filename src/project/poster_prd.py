#!/usr/bin/env python3
"""
Poster Worker - Esquema PRD
Lee publicaciones programadas y ejecuta workers para publicar contenido.
Usa exclusivamente el esquema PRD (publicaciones, contenidos, cuentas_plataforma, etc.)
"""

import os
import time
import subprocess
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

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


def get_pending_publicaciones() -> List[Dict]:
    """
    Obtiene publicaciones programadas listas para procesar.
    Usa el índice crítico: idx_publicaciones_estado_scheduled
    
    Query optimizada:
    SELECT * FROM publicaciones 
    WHERE estado = 'programada' 
    AND scheduled_time <= now()
    ORDER BY scheduled_time ASC
    """
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        
        # Query usando el índice crítico
        response = supabase.table('publicaciones')\
            .select("*, contenidos(*, modelos(*)), cuentas_plataforma(*, plataformas(*))")\
            .eq('estado', 'programada')\
            .lte('scheduled_time', now_iso)\
            .order('scheduled_time', desc=False)\
            .execute()
        
        return response.data if response.data else []
    except Exception as e:
        print(f"❌ Error obteniendo publicaciones programadas: {e}")
        return []


def create_evento_sistema(
    tipo: str,
    publicacion_id: Optional[str] = None,
    modelo_id: Optional[str] = None,
    descripcion: str = "",
    realizado_por: str = "sistema"
):
    """Registra un evento en eventos_sistema"""
    try:
        data = {
            "tipo": tipo,
            "descripcion": descripcion,
            "realizado_por": realizado_por
        }
        if publicacion_id:
            data["publicacion_id"] = publicacion_id
        if modelo_id:
            data["modelo_id"] = modelo_id
        
        supabase.table('eventos_sistema').insert(data).execute()
    except Exception as e:
        print(f"⚠️  Error registrando evento: {e}")


def update_publicacion_estado(
    publicacion_id: str,
    nuevo_estado: str,
    ultimo_error: Optional[str] = None,
    url_publicacion: Optional[str] = None,
    incrementar_intentos: bool = False
):
    """
    Actualiza el estado de una publicación.
    Maneja: estado, intentos, ultimo_error, published_at
    """
    try:
        update_data = {"estado": nuevo_estado}
        
        if ultimo_error:
            update_data["ultimo_error"] = ultimo_error
        
        if url_publicacion:
            update_data["url_publicacion"] = url_publicacion
        
        if nuevo_estado == 'publicado':
            update_data["published_at"] = datetime.now(timezone.utc).isoformat()
        
        if incrementar_intentos:
            # Obtener intentos actuales
            current = supabase.table('publicaciones').select("intentos").eq('id', publicacion_id).execute()
            if current.data:
                update_data["intentos"] = (current.data[0].get('intentos', 0) or 0) + 1
        
        supabase.table('publicaciones')\
            .update(update_data)\
            .eq('id', publicacion_id)\
            .execute()
        
        return True
    except Exception as e:
        print(f"❌ Error actualizando publicación {publicacion_id}: {e}")
        return False


def get_worker_script_path(plataforma_nombre: str) -> Optional[Path]:
    """
    Obtiene la ruta del script worker para una plataforma.
    Retorna None si no existe.
    """
    # Mapeo de plataformas a scripts
    script_map = {
        'kams': 'workers/kams.js',
        'kams.com': 'workers/kams.js',
        'xxxfollow': 'workers/xxxfollow.js',
    }
    
    script_rel = script_map.get(plataforma_nombre.lower())
    if not script_rel:
        return None
    
    script_path = BASE_DIR / script_rel
    if script_path.exists():
        return script_path
    
    return None


def process_publicacion(publicacion: Dict):
    """
    Procesa una publicación individual:
    1. Cambia estado a 'procesando'
    2. Ejecuta worker
    3. Actualiza estado según resultado
    4. Registra eventos
    """
    publicacion_id = publicacion['id']
    
    # Extraer datos de relaciones anidadas
    # Supabase devuelve: { "contenidos": {...}, "cuentas_plataforma": {...} }
    contenido = publicacion.get('contenidos')
    if isinstance(contenido, dict):
        modelo = contenido.get('modelos', {})
        if isinstance(modelo, dict):
            modelo_nombre = modelo.get('nombre', '')
            modelo_id = modelo.get('id')
        else:
            modelo_nombre = ''
            modelo_id = None
        archivo_path = contenido.get('archivo_path', '')
        caption_generado = contenido.get('caption_generado', '')
        tags_generados = contenido.get('tags_generados', [])
    else:
        modelo_nombre = ''
        modelo_id = None
        archivo_path = ''
        caption_generado = ''
        tags_generados = []
    
    cuenta = publicacion.get('cuentas_plataforma')
    if isinstance(cuenta, dict):
        plataforma = cuenta.get('plataformas', {})
        if isinstance(plataforma, dict):
            plataforma_nombre = plataforma.get('nombre', '')
        else:
            plataforma_nombre = ''
    else:
        plataforma_nombre = ''
    
    # Usar caption_usado si existe, sino caption_generado
    caption = publicacion.get('caption_usado', '') or caption_generado
    # Usar tags_usados si existe, sino tags_generados
    tags = publicacion.get('tags_usados', []) or tags_generados
    
    print(f"\n🔄 Procesando publicación {publicacion_id}")
    print(f"   Modelo: {modelo_nombre}")
    print(f"   Plataforma: {plataforma_nombre}")
    print(f"   Archivo: {archivo_path}")
    
    # Validaciones
    if not modelo_nombre:
        error_msg = "Modelo no encontrado en relación"
        print(f"❌ {error_msg}")
        update_publicacion_estado(publicacion_id, 'fallido', error_msg, incrementar_intentos=True)
        create_evento_sistema('publicacion_fallida', publicacion_id, modelo_id, error_msg)
        return
    
    if not plataforma_nombre:
        error_msg = "Plataforma no encontrada en relación"
        print(f"❌ {error_msg}")
        update_publicacion_estado(publicacion_id, 'fallido', error_msg, incrementar_intentos=True)
        create_evento_sistema('publicacion_fallida', publicacion_id, modelo_id, error_msg)
        return
    
    # 1. Cambiar estado a 'procesando'
    print(f"   📝 Cambiando estado a 'procesando'...")
    update_publicacion_estado(publicacion_id, 'procesando')
    create_evento_sistema('publicacion_iniciada', publicacion_id, modelo_id, 
                         f"Iniciando publicación en {plataforma_nombre}")
    
    # 2. Construir ruta del archivo
    # archivo_path viene como "modelos/{modelo}/{video}"
    video_path = BASE_DIR / archivo_path
    
    if not video_path.exists():
        error_msg = f"Archivo no encontrado: {video_path}"
        print(f"❌ {error_msg}")
        update_publicacion_estado(publicacion_id, 'fallido', error_msg, incrementar_intentos=True)
        create_evento_sistema('publicacion_fallida', publicacion_id, modelo_id, error_msg)
        return
    
    # 3. Obtener worker script
    worker_script = get_worker_script_path(plataforma_nombre)
    if not worker_script:
        error_msg = f"Worker no encontrado para plataforma: {plataforma_nombre}"
        print(f"❌ {error_msg}")
        update_publicacion_estado(publicacion_id, 'fallido', error_msg, incrementar_intentos=True)
        create_evento_sistema('publicacion_fallida', publicacion_id, modelo_id, error_msg)
        return
    
    # 4. Preparar entorno para worker
    env = os.environ.copy()
    env['VIDEO_PATH'] = str(video_path)
    env['VIDEO_TITLE'] = caption
    env['VIDEO_TAGS'] = ','.join(tags) if isinstance(tags, list) else str(tags)
    env['MODEL_NAME'] = modelo_nombre
    
    # 5. Ejecutar worker
    print(f"   🚀 Ejecutando worker: {worker_script.name}")
    print(f"      Video: {video_path.name}")
    print(f"      Título: {caption[:50]}...")
    print(f"      Tags: {env['VIDEO_TAGS']}")
    
    try:
        cmd = ["npx", "playwright", "test", str(worker_script)]
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, cwd=str(BASE_DIR), timeout=300)
        
        if result.returncode == 0:
            # Éxito
            print(f"   ✅ Publicación exitosa")
            if result.stdout:
                # Intentar extraer URL de la salida si está disponible
                url_publicacion = None
                stdout_lines = result.stdout.split('\n')
                for line in stdout_lines:
                    if 'http' in line.lower() and ('kams.com' in line or 'xxxfollow.com' in line):
                        # Extraer URL aproximada
                        url_publicacion = line.strip()
                        break
                
                update_publicacion_estado(publicacion_id, 'publicado', url_publicacion=url_publicacion)
            else:
                update_publicacion_estado(publicacion_id, 'publicado')
            
            create_evento_sistema('publicacion_exitosa', publicacion_id, modelo_id,
                                 f"Publicación exitosa en {plataforma_nombre}")
        else:
            # Fallo
            error_output = result.stderr[-500:] if result.stderr else result.stdout[-500:] if result.stdout else "Error desconocido"
            error_msg = f"Worker falló (code {result.returncode}): {error_output}"
            print(f"   ❌ {error_msg}")
            
            update_publicacion_estado(publicacion_id, 'fallido', error_msg, incrementar_intentos=True)
            create_evento_sistema('publicacion_fallida', publicacion_id, modelo_id, error_msg)
            
    except subprocess.TimeoutExpired:
        error_msg = "Worker timeout (más de 5 minutos)"
        print(f"   ❌ {error_msg}")
        update_publicacion_estado(publicacion_id, 'fallido', error_msg, incrementar_intentos=True)
        create_evento_sistema('publicacion_fallida', publicacion_id, modelo_id, error_msg)
        
    except Exception as e:
        error_msg = f"Error ejecutando worker: {e}"
        print(f"   ❌ {error_msg}")
        update_publicacion_estado(publicacion_id, 'fallido', error_msg, incrementar_intentos=True)
        create_evento_sistema('publicacion_fallida', publicacion_id, modelo_id, error_msg)


def main():
    """
    Loop principal del poster.
    Lee publicaciones programadas y las procesa.
    """
    print("🚀 Iniciando Poster Worker (Esquema PRD)")
    print("=" * 60)
    
    while True:
        try:
            # Obtener publicaciones programadas
            publicaciones = get_pending_publicaciones()
            
            if publicaciones:
                print(f"\n📬 {len(publicaciones)} publicación(es) programada(s) encontrada(s)")
                for pub in publicaciones:
                    process_publicacion(pub)
            else:
                print("💤 No hay publicaciones programadas. Esperando...")
            
            # Esperar antes de la siguiente iteración
            print(f"\n💤 Esperando 60 segundos...")
            time.sleep(60)
            
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo poster...")
            break
        except Exception as e:
            print(f"❌ Error en loop principal: {e}")
            import traceback
            traceback.print_exc()
            print("💤 Reintentando en 60 segundos...")
            time.sleep(60)


if __name__ == "__main__":
    main()

