#!/usr/bin/env python3
"""
Módulo para crear y gestionar contenidos en el esquema PRD
FASE 4A: Migración del Bot Telegram
"""

import os
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime, timezone
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
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


def get_modelo_id_by_nombre(modelo_nombre: str) -> Optional[str]:
    """
    Obtiene el ID del modelo por su nombre.
    
    Args:
        modelo_nombre: Nombre del modelo (slug)
    
    Returns:
        UUID del modelo o None si no existe
    """
    try:
        response = supabase.table('modelos')\
            .select("id")\
            .eq('nombre', modelo_nombre)\
            .execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]['id']
        return None
    except Exception as e:
        logger.error(f"Error obteniendo modelo_id para '{modelo_nombre}': {e}")
        return None


def create_contenido(
    modelo_nombre: str,
    archivo_path: str,
    contexto_original: str = "",
    enviado_por: str = "",
    caption_generado: str = "",
    tags_generados: list = None
) -> Optional[str]:
    """
    Crea un contenido en la tabla contenidos (esquema PRD).
    Implementa idempotencia: no duplica si ya existe.
    
    Args:
        modelo_nombre: Nombre del modelo (slug)
        archivo_path: Ruta relativa del archivo (ej: "modelos/{modelo}/{video}")
        contexto_original: Contexto original del mensaje (qué vendes, outfit, etc.)
        enviado_por: Usuario que envió el contenido (telegram_user_id o nombre)
        caption_generado: Caption generado (opcional, puede venir después)
        tags_generados: Lista de tags generados (opcional, puede venir después)
    
    Returns:
        UUID del contenido creado o existente, None si hay error
    """
    if tags_generados is None:
        tags_generados = []
    
    try:
        # 1. Obtener modelo_id
        modelo_id = get_modelo_id_by_nombre(modelo_nombre)
        if not modelo_id:
            logger.error(f"❌ Modelo '{modelo_nombre}' no existe en tabla modelos")
            return None
        
        # 2. Verificar si ya existe (IDEMPOTENCIA)
        # Buscar por modelo_id + archivo_path
        existing = supabase.table('contenidos')\
            .select("id")\
            .eq('modelo_id', modelo_id)\
            .eq('archivo_path', archivo_path)\
            .execute()
        
        if existing.data and len(existing.data) > 0:
            contenido_id = existing.data[0]['id']
            logger.info(f"ℹ️  Contenido ya existe: {archivo_path} (ID: {contenido_id})")
            return contenido_id
        
        # 3. Crear nuevo contenido
        data = {
            "modelo_id": modelo_id,
            "archivo_path": archivo_path,
            "contexto_original": contexto_original,
            "enviado_por": enviado_por,
            "estado": "nuevo",
            "recibido_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Agregar caption y tags si están disponibles
        if caption_generado:
            data["caption_generado"] = caption_generado
        
        if tags_generados:
            data["tags_generados"] = tags_generados
        
        result = supabase.table('contenidos').insert(data).execute()
        
        if result.data and len(result.data) > 0:
            contenido_id = result.data[0]['id']
            logger.info(f"✅ Contenido creado: {archivo_path} (ID: {contenido_id})")
            return contenido_id
        else:
            logger.error(f"❌ No se recibió ID al crear contenido: {archivo_path}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error creando contenido '{archivo_path}': {e}")
        import traceback
        traceback.print_exc()
        return None


def update_contenido_caption_tags(
    contenido_id: str,
    caption_generado: str = "",
    tags_generados: list = None
) -> bool:
    """
    Actualiza el caption y tags de un contenido existente.
    Útil cuando el caption se genera después de crear el contenido.
    
    Args:
        contenido_id: UUID del contenido
        caption_generado: Caption generado
        tags_generados: Lista de tags generados
    
    Returns:
        True si se actualizó exitosamente
    """
    if tags_generados is None:
        tags_generados = []
    
    try:
        update_data = {}
        
        if caption_generado:
            update_data["caption_generado"] = caption_generado
        
        if tags_generados:
            update_data["tags_generados"] = tags_generados
        
        if not update_data:
            logger.warning(f"⚠️  No hay datos para actualizar en contenido {contenido_id}")
            return False
        
        supabase.table('contenidos')\
            .update(update_data)\
            .eq('id', contenido_id)\
            .execute()
        
        logger.info(f"✅ Contenido {contenido_id} actualizado con caption/tags")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error actualizando contenido {contenido_id}: {e}")
        return False



