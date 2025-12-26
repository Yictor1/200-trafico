"""
Cliente centralizado de Supabase para el proyecto Trafico (PRD).

Este archivo contiene únicamente:
- Inicialización del cliente Supabase
- Exports del cliente para uso en otros módulos

NOTA: Funciones legacy ELIMINADAS (FASE 5 ETAPA 3.2)
Las siguientes funciones fueron eliminadas porque usaban esquema legacy:
- get_model_config() → usa modelos.modelo (columna legacy)
- create_model_config() → crea con estructura legacy
- table_exists() → verifica tablas dinámicas (no existen en PRD)
- create_model_table() → crea tablas dinámicas (no existen en PRD)
- ensure_model_exists() → crea modelos y tablas dinámicas
- insert_schedule() → inserta en tablas dinámicas
- get_all_schedules() → lee de tablas dinámicas
- get_pending_schedules() → lee de tablas dinámicas
- update_schedule_time() → actualiza tablas dinámicas

Esquema PRD actual:
- modelos.id (UUID PK) + modelos.nombre (TEXT UNIQUE)
- contenidos (contenido recibido desde bot)
- publicaciones (publicaciones programadas, unificada)
- cuentas_plataforma (relacional)
- NO hay tablas dinámicas por modelo

Para operaciones con modelos, usar directamente:
- supabase.table("modelos").select("*").eq("nombre", nombre_modelo)
- supabase.table("contenidos").insert(...)
- supabase.table("publicaciones").select(...)

Ver: Migracion/FASE5_ETAPA3_COMPLETADA.md
Última actualización: 2025-12-25
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Configuración
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://osdpemjvcsmfbacmjlcv.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_KEY:
    raise ValueError("SUPABASE_ANON_KEY no está configurado en .env")

# Cliente global - Disponible para importación directa
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
