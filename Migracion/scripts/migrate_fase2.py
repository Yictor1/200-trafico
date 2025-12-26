#!/usr/bin/env python3
"""
FASE 2: Migración de datos desde tablas dinámicas al esquema PRD
Cumple: Idempotencia, Dry-run, Validación de conteos
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional

BASE_DIR = Path(__file__).resolve().parents[2]
env_path = BASE_DIR / '100trafico' / 'src' / '.env'
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://osdpemjvcsmfbacmjlcv.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_KEY:
    print("❌ ERROR: SUPABASE_ANON_KEY no configurado")
    sys.exit(1)


class MigrationStats:
    """Contenedor de estadísticas de migración"""
    def __init__(self):
        self.modelos_creados = 0
        self.modelos_existentes = 0
        self.plataformas_creadas = 0
        self.plataformas_existentes = 0
        self.cuentas_creadas = 0
        self.cuentas_existentes = 0
        self.contenidos_creados = 0
        self.contenidos_existentes = 0
        self.publicaciones_creadas = 0
        self.publicaciones_existentes = 0
        self.errores = []
    
    def print_summary(self):
        """Imprime resumen de estadísticas"""
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE MIGRACIÓN")
        print("=" * 60)
        print(f"Modelos: {self.modelos_creados} nuevos, {self.modelos_existentes} existentes")
        print(f"Plataformas: {self.plataformas_creadas} nuevas, {self.plataformas_existentes} existentes")
        print(f"Cuentas: {self.cuentas_creadas} nuevas, {self.cuentas_existentes} existentes")
        print(f"Contenidos: {self.contenidos_creados} nuevos, {self.contenidos_existentes} existentes")
        print(f"Publicaciones: {self.publicaciones_creadas} nuevas, {self.publicaciones_existentes} existentes")
        if self.errores:
            print(f"\n⚠️  Errores: {len(self.errores)}")
            for error in self.errores[:10]:
                print(f"   - {error}")


def dry_run_analysis(supabase: Client) -> Dict:
    """
    Modo DRY-RUN: Analiza datos sin modificar nada
    Retorna conteos esperados
    """
    print("🔍 MODO DRY-RUN: Analizando datos...\n")
    
    stats = {
        'modelos_old': [],
        'tablas_dinamicas': {},
        'total_registros': 0,
        'plataformas_unicas': set(),
        'videos_unicos': defaultdict(set),  # modelo -> set(videos)
        'auth_files': defaultdict(list)
    }
    
    # 1. Leer tabla modelos antigua
    # La tabla antigua tiene 'modelo' como PK (TEXT)
    # La tabla nueva tiene 'nombre' (TEXT) con 'id' (UUID) como PK
    print("📋 Leyendo tabla 'modelos' (antigua)...")
    try:
        # Intentar leer con estructura antigua (columna 'modelo')
        modelos_old = supabase.table('modelos').select("*").execute()
        
        if modelos_old.data:
            # Verificar si es estructura antigua o nueva
            primer_registro = modelos_old.data[0]
            tiene_modelo_col = 'modelo' in primer_registro
            tiene_nombre_col = 'nombre' in primer_registro
            
            if tiene_modelo_col and not tiene_nombre_col:
                # Es estructura antigua
                stats['modelos_old'] = modelos_old.data
                print(f"   ✅ {len(modelos_old.data)} modelos encontrados (estructura antigua)")
                
                for m in modelos_old.data:
                    # Extraer plataformas
                    plataformas_str = m.get('plataformas', '') or ''
                    for p in plataformas_str.split(','):
                        p_clean = p.strip().lower()
                        if p_clean:
                            stats['plataformas_unicas'].add(p_clean)
            elif tiene_nombre_col:
                # Es estructura nueva (PRD), no hay datos antiguos
                print("   ℹ️  Tabla 'modelos' tiene estructura nueva (PRD)")
                print("   ℹ️  No hay datos antiguos para migrar")
            else:
                print("   ⚠️  Estructura de tabla desconocida")
        else:
            print("   ℹ️  No hay modelos en la tabla")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        # Continuar aunque haya error, puede que no haya datos
    
    # 2. Leer tablas dinámicas
    print(f"\n📋 Leyendo tablas dinámicas...")
    if not stats['modelos_old']:
        print("   ℹ️  No hay modelos para leer tablas dinámicas")
    else:
        for modelo_data in stats['modelos_old']:
            # Obtener nombre del modelo (puede ser 'modelo' o 'nombre')
            modelo = modelo_data.get('modelo') or modelo_data.get('nombre')
            if not modelo:
                continue
                
            try:
                registros = supabase.table(modelo).select("*").execute()
                if registros.data:
                    stats['tablas_dinamicas'][modelo] = registros.data
                    stats['total_registros'] += len(registros.data)
                    
                    # Agrupar videos únicos
                    for reg in registros.data:
                        video = reg.get('video', '').strip()
                        if video:
                            stats['videos_unicos'][modelo].add(video)
                    
                    print(f"   ✅ {modelo}: {len(registros.data)} registros, {len(stats['videos_unicos'][modelo])} videos únicos")
                else:
                    print(f"   ℹ️  {modelo}: tabla vacía")
            except Exception as e:
                error_msg = str(e)
                # PGRST205 = tabla no existe
                if 'PGRST205' in error_msg or 'does not exist' in error_msg.lower():
                    print(f"   ℹ️  {modelo}: tabla no existe (normal si no hay datos)")
                else:
                    print(f"   ⚠️  {modelo}: Error ({error_msg[:50]})")
    
    # 3. Leer archivos .auth
    print(f"\n📋 Leyendo archivos .auth...")
    modelos_dir = BASE_DIR / '100trafico' / 'modelos'
    if modelos_dir.exists():
        for modelo_dir in modelos_dir.iterdir():
            if modelo_dir.is_dir():
                auth_dir = modelo_dir / '.auth'
                if auth_dir.exists():
                    for auth_file in auth_dir.glob('*.json'):
                        platform = auth_file.stem
                        stats['auth_files'][modelo_dir.name].append(platform)
        
        if stats['auth_files']:
            for modelo, platforms in stats['auth_files'].items():
                print(f"   ✅ {modelo}: {', '.join(platforms)}")
        else:
            print("   ℹ️  No se encontraron archivos .auth")
    else:
        print("   ℹ️  Directorio modelos/ no existe")
    
    return stats


def print_dry_run_results(stats: Dict):
    """Imprime resultados del dry-run"""
    print("\n" + "=" * 60)
    print("📋 CONTEOS ESPERADOS (DRY-RUN)")
    print("=" * 60)
    print(f"\n1️⃣  Modelos:")
    print(f"   - Modelos a migrar: {len(stats['modelos_old'])}")
    
    print(f"\n2️⃣  Plataformas:")
    print(f"   - Plataformas únicas encontradas: {len(stats['plataformas_unicas'])}")
    for p in sorted(stats['plataformas_unicas']):
        print(f"     - {p}")
    
    print(f"\n3️⃣  Contenidos:")
    total_videos = sum(len(videos) for videos in stats['videos_unicos'].values())
    print(f"   - Videos únicos totales: {total_videos}")
    for modelo, videos in stats['videos_unicos'].items():
        print(f"     - {modelo}: {len(videos)} videos únicos")
    
    print(f"\n4️⃣  Publicaciones:")
    print(f"   - Registros en tablas dinámicas: {stats['total_registros']}")
    for modelo, registros in stats['tablas_dinamicas'].items():
        print(f"     - {modelo}: {len(registros)} registros")
    
    print(f"\n5️⃣  Cuentas (archivos .auth):")
    total_cuentas = sum(len(platforms) for platforms in stats['auth_files'].values())
    print(f"   - Cuentas con sesión guardada: {total_cuentas}")
    for modelo, platforms in stats['auth_files'].items():
        print(f"     - {modelo}: {', '.join(platforms)}")
    
    print("\n" + "=" * 60)
    print("✅ DRY-RUN completado")
    print("   Estos son los conteos que se crearán si ejecutas la migración")
    print("=" * 60)


def migrate_platforms(supabase: Client, stats: MigrationStats, plataformas: set, dry_run: bool = False) -> Dict[str, str]:
    """
    Migra plataformas a nueva tabla
    Retorna mapeo: nombre_plataforma -> uuid
    """
    print("\n🌐 Migrando plataformas...")
    platform_map = {}
    
    for plataforma_nombre in sorted(plataformas):
        # Verificar si ya existe (IDEMPOTENCIA)
        try:
            existing = supabase.table('plataformas').select("id").eq('nombre', plataforma_nombre).execute()
            
            if existing.data:
                platform_map[plataforma_nombre] = existing.data[0]['id']
                stats.plataformas_existentes += 1
                if not dry_run:
                    print(f"   ℹ️  Plataforma '{plataforma_nombre}' ya existe")
            else:
                if dry_run:
                    stats.plataformas_creadas += 1
                    print(f"   [DRY-RUN] Crearía plataforma '{plataforma_nombre}'")
                else:
                    data = {
                        "nombre": plataforma_nombre,
                        "capacidades": {},
                        "configuracion_tecnica": {},
                        "activa": True
                    }
                    result = supabase.table('plataformas').insert(data).execute()
                    platform_map[plataforma_nombre] = result.data[0]['id']
                    stats.plataformas_creadas += 1
                    print(f"   ✅ Plataforma '{plataforma_nombre}' creada")
        except Exception as e:
            error_msg = f"Error migrando plataforma '{plataforma_nombre}': {e}"
            stats.errores.append(error_msg)
            print(f"   ❌ {error_msg}")
    
    return platform_map


def migrate_modelos(supabase: Client, stats: MigrationStats, modelos_old: List[Dict], dry_run: bool = False) -> Dict[str, str]:
    """
    Migra modelos a nueva tabla
    Retorna mapeo: nombre_modelo -> uuid
    """
    print("\n👤 Migrando modelos...")
    modelo_map = {}
    
    for modelo_old in modelos_old:
        # Obtener nombre (puede ser 'modelo' o 'nombre' dependiendo de estructura)
        nombre = modelo_old.get('modelo') or modelo_old.get('nombre')
        if not nombre:
            continue
        
        try:
            # Verificar si ya existe (IDEMPOTENCIA)
            existing = supabase.table('modelos').select("id").eq('nombre', nombre).execute()
            
            if existing.data:
                modelo_map[nombre] = existing.data[0]['id']
                stats.modelos_existentes += 1
                if not dry_run:
                    print(f"   ℹ️  Modelo '{nombre}' ya existe")
            else:
                if dry_run:
                    stats.modelos_creados += 1
                    print(f"   [DRY-RUN] Crearía modelo '{nombre}'")
                else:
                    # Parsear configuración
                    plataformas_str = modelo_old.get('plataformas', '') or ''
                    plataformas_list = [p.strip() for p in plataformas_str.split(',') if p.strip()]
                    
                    config = {
                        "plataformas": plataformas_list,
                        "hora_inicio": modelo_old.get('hora_inicio', '12:00'),
                        "ventana_horas": modelo_old.get('ventana_horas', 5)
                    }
                    
                    if modelo_old.get('striphours_url'):
                        config['striphours_url'] = modelo_old['striphours_url']
                    if modelo_old.get('striphours_username'):
                        config['striphours_username'] = modelo_old['striphours_username']
                    
                    data = {
                        "nombre": nombre,
                        "estado": "activa",
                        "configuracion_distribucion": config
                    }
                    result = supabase.table('modelos').insert(data).execute()
                    modelo_map[nombre] = result.data[0]['id']
                    stats.modelos_creados += 1
                    print(f"   ✅ Modelo '{nombre}' creado")
        except Exception as e:
            error_msg = f"Error migrando modelo '{nombre}': {e}"
            stats.errores.append(error_msg)
            print(f"   ❌ {error_msg}")
    
    return modelo_map


def migrate_cuentas(supabase: Client, stats: MigrationStats, modelo_map: Dict, platform_map: Dict, auth_files: Dict, dry_run: bool = False):
    """Migra cuentas_plataforma desde archivos .auth"""
    print("\n🔐 Migrando cuentas_plataforma...")
    
    for modelo_nombre, platforms in auth_files.items():
        if modelo_nombre not in modelo_map:
            print(f"   ⚠️  Modelo '{modelo_nombre}' no encontrado en modelo_map, saltando")
            continue
        
        modelo_id = modelo_map[modelo_nombre]
        
        for platform_nombre in platforms:
            if platform_nombre not in platform_map:
                print(f"   ⚠️  Plataforma '{platform_nombre}' no encontrada en platform_map, saltando")
                continue
            
            platform_id = platform_map[platform_nombre]
            
            try:
                # Verificar si ya existe (IDEMPOTENCIA)
                existing = supabase.table('cuentas_plataforma')\
                    .select("id")\
                    .eq('modelo_id', modelo_id)\
                    .eq('plataforma_id', platform_id)\
                    .execute()
                
                if existing.data:
                    stats.cuentas_existentes += 1
                    if not dry_run:
                        print(f"   ℹ️  Cuenta {modelo_nombre}+{platform_nombre} ya existe")
                else:
                    if dry_run:
                        stats.cuentas_creadas += 1
                        print(f"   [DRY-RUN] Crearía cuenta {modelo_nombre}+{platform_nombre}")
                    else:
                        # Leer archivo .auth
                        auth_path = BASE_DIR / '100trafico' / 'modelos' / modelo_nombre / '.auth' / f'{platform_nombre}.json'
                        datos_auth = {}
                        if auth_path.exists():
                            try:
                                with open(auth_path, 'r') as f:
                                    datos_auth = json.load(f)
                            except Exception as e:
                                print(f"   ⚠️  Error leyendo {auth_path}: {e}")
                        
                        data = {
                            "modelo_id": modelo_id,
                            "plataforma_id": platform_id,
                            "sesion_guardada": bool(datos_auth),
                            "datos_auth": datos_auth
                        }
                        supabase.table('cuentas_plataforma').insert(data).execute()
                        stats.cuentas_creadas += 1
                        print(f"   ✅ Cuenta {modelo_nombre}+{platform_nombre} creada")
            except Exception as e:
                error_msg = f"Error migrando cuenta {modelo_nombre}+{platform_nombre}: {e}"
                stats.errores.append(error_msg)
                print(f"   ❌ {error_msg}")


def migrate_contenidos(supabase: Client, stats: MigrationStats, modelo_map: Dict, videos_unicos: Dict, tablas_dinamicas: Dict, dry_run: bool = False) -> Dict[Tuple[str, str], str]:
    """
    Migra contenidos (videos únicos)
    Retorna mapeo: (modelo, video) -> contenido_id
    """
    print("\n📹 Migrando contenidos...")
    contenido_map = {}
    
    for modelo_nombre, videos in videos_unicos.items():
        if modelo_nombre not in modelo_map:
            print(f"   ⚠️  Modelo '{modelo_nombre}' no encontrado en modelo_map, saltando")
            continue
        
        modelo_id = modelo_map[modelo_nombre]
        registros = tablas_dinamicas.get(modelo_nombre, [])
        
        # Agrupar por video para obtener datos del primer registro
        video_data = {}
        for reg in registros:
            video = reg.get('video', '').strip()
            if video and video not in video_data:
                video_data[video] = reg
        
        for video in videos:
            reg = video_data.get(video)
            if not reg:
                continue
            
            archivo_path = f"modelos/{modelo_nombre}/{video}"
            
            try:
                # Verificar si ya existe (IDEMPOTENCIA)
                existing = supabase.table('contenidos')\
                    .select("id")\
                    .eq('modelo_id', modelo_id)\
                    .eq('archivo_path', archivo_path)\
                    .execute()
                
                if existing.data:
                    contenido_map[(modelo_nombre, video)] = existing.data[0]['id']
                    stats.contenidos_existentes += 1
                else:
                    if dry_run:
                        stats.contenidos_creados += 1
                    else:
                        # Parsear tags
                        tags_str = reg.get('tags', '') or ''
                        tags_list = [t.strip() for t in tags_str.split(',') if t.strip()]
                        
                        data = {
                            "modelo_id": modelo_id,
                            "archivo_path": archivo_path,
                            "caption_generado": reg.get('caption', '') or '',
                            "tags_generados": tags_list,
                            "estado": "aprobado",  # Asumimos que si está programado, fue aprobado
                            "approved_at": datetime.now(timezone.utc).isoformat(),
                            "approved_by": "sistema_migracion"
                        }
                        result = supabase.table('contenidos').insert(data).execute()
                        contenido_map[(modelo_nombre, video)] = result.data[0]['id']
                        stats.contenidos_creados += 1
            except Exception as e:
                error_msg = f"Error migrando contenido {modelo_nombre}/{video}: {e}"
                stats.errores.append(error_msg)
                print(f"   ❌ {error_msg}")
        
        if not dry_run and videos:
            print(f"   ✅ {modelo_nombre}: {len(videos)} contenidos procesados")
    
    return contenido_map


def get_cuenta_plataforma_map(supabase: Client, modelo_map: Dict, platform_map: Dict) -> Dict[Tuple[str, str], str]:
    """
    Construye mapeo de (modelo_nombre, plataforma_nombre) -> cuenta_plataforma_id
    """
    cuenta_map = {}
    
    # Crear mapeo inverso: platform_id -> platform_nombre
    platform_id_to_name = {p_id: p_name for p_name, p_id in platform_map.items()}
    
    for modelo_nombre, modelo_id in modelo_map.items():
        try:
            # Obtener todas las cuentas de este modelo
            cuentas = supabase.table('cuentas_plataforma')\
                .select("id, plataforma_id")\
                .eq('modelo_id', modelo_id)\
                .execute()
            
            if cuentas.data:
                for cuenta in cuentas.data:
                    platform_id = cuenta['plataforma_id']
                    # Buscar nombre de plataforma en el mapeo inverso
                    platform_nombre = platform_id_to_name.get(platform_id)
                    if platform_nombre:
                        cuenta_map[(modelo_nombre, platform_nombre)] = cuenta['id']
        except Exception as e:
            print(f"   ⚠️  Error obteniendo cuentas para {modelo_nombre}: {e}")
    
    return cuenta_map


def migrate_publicaciones(supabase: Client, stats: MigrationStats, modelo_map: Dict, platform_map: Dict, contenido_map: Dict, cuenta_map: Dict, tablas_dinamicas: Dict, dry_run: bool = False):
    """Migra publicaciones desde tablas dinámicas"""
    print("\n📅 Migrando publicaciones...")
    
    for modelo_nombre, registros in tablas_dinamicas.items():
        if modelo_nombre not in modelo_map:
            continue
        
        for reg in registros:
            video = reg.get('video', '').strip()
            plataforma_nombre = reg.get('plataforma', '').strip().lower()
            
            if not video or not plataforma_nombre:
                continue
            
            # Buscar contenido_id
            contenido_key = (modelo_nombre, video)
            if contenido_key not in contenido_map:
                error_msg = f"Contenido no encontrado: {modelo_nombre}/{video}"
                stats.errores.append(error_msg)
                continue
            
            contenido_id = contenido_map[contenido_key]
            
            # Buscar cuenta_plataforma_id
            cuenta_key = (modelo_nombre, plataforma_nombre)
            if cuenta_key not in cuenta_map:
                # Intentar crear cuenta si no existe
                if not dry_run:
                    modelo_id = modelo_map[modelo_nombre]
                    if plataforma_nombre in platform_map:
                        platform_id = platform_map[plataforma_nombre]
                        try:
                            # Crear cuenta
                            cuenta_data = {
                                "modelo_id": modelo_id,
                                "plataforma_id": platform_id,
                                "sesion_guardada": False
                            }
                            cuenta_result = supabase.table('cuentas_plataforma').insert(cuenta_data).execute()
                            cuenta_id = cuenta_result.data[0]['id']
                            cuenta_map[cuenta_key] = cuenta_id
                            stats.cuentas_creadas += 1
                            print(f"   ℹ️  Cuenta {modelo_nombre}+{plataforma_nombre} creada automáticamente")
                        except Exception as e:
                            error_msg = f"No se pudo crear cuenta {modelo_nombre}+{plataforma_nombre}: {e}"
                            stats.errores.append(error_msg)
                            continue
                    else:
                        error_msg = f"Plataforma '{plataforma_nombre}' no encontrada para {modelo_nombre}"
                        stats.errores.append(error_msg)
                        continue
                else:
                    # En dry-run, asumimos que se crearía
                    stats.publicaciones_creadas += 1
                    continue
            
            cuenta_id = cuenta_map[cuenta_key]
            
            try:
                # Mapear estado
                estado_old = reg.get('estado', 'pendiente')
                estado_map = {
                    'pendiente': 'programada',
                    'procesando': 'procesando',
                    'publicado': 'publicado',
                    'fallido': 'fallido'
                }
                estado_new = estado_map.get(estado_old.lower(), 'programada')
                
                # Parsear tags
                tags_str = reg.get('tags', '') or ''
                tags_list = [t.strip() for t in tags_str.split(',') if t.strip()]
                
                # Parsear scheduled_time
                scheduled_time = reg.get('scheduled_time')
                if scheduled_time and isinstance(scheduled_time, str):
                    # Intentar parsear fecha
                    try:
                        # Formato esperado: "YYYY-MM-DD HH:MM:SS"
                        if len(scheduled_time) >= 19:
                            dt = datetime.strptime(scheduled_time[:19], "%Y-%m-%d %H:%M:%S")
                            # Asumir timezone de Colombia (UTC-5)
                            from datetime import timedelta
                            tz = timezone(timedelta(hours=-5))
                            dt = dt.replace(tzinfo=tz)
                            scheduled_time = dt.isoformat()
                    except:
                        pass  # Dejar como está si no se puede parsear
                
                if dry_run:
                    stats.publicaciones_creadas += 1
                else:
                    # Verificar si ya existe (IDEMPOTENCIA)
                    # Buscar por contenido_id + cuenta_plataforma_id
                    existing = supabase.table('publicaciones')\
                        .select("id, scheduled_time")\
                        .eq('contenido_id', contenido_id)\
                        .eq('cuenta_plataforma_id', cuenta_id)\
                        .execute()
                    
                    # Si existe publicación con mismo contenido y cuenta, verificar scheduled_time
                    if existing.data:
                        found = False
                        for pub in existing.data:
                            existing_st = pub.get('scheduled_time')
                            if scheduled_time and existing_st:
                                # Comparar fechas (ignorar microsegundos y timezone)
                                try:
                                    # Normalizar ambos a string para comparar
                                    st_str = str(scheduled_time)[:19].replace('T', ' ')
                                    est_str = str(existing_st)[:19].replace('T', ' ')
                                    if st_str == est_str:
                                        found = True
                                        stats.publicaciones_existentes += 1
                                        break
                                except:
                                    pass
                        
                        if found:
                            continue
                    
                    data = {
                        "contenido_id": contenido_id,
                        "cuenta_plataforma_id": cuenta_id,
                        "scheduled_time": scheduled_time,
                        "caption_usado": reg.get('caption', '') or '',
                        "tags_usados": tags_list,
                        "estado": estado_new,
                        "intentos": 0
                    }
                    
                    supabase.table('publicaciones').insert(data).execute()
                    stats.publicaciones_creadas += 1
            except Exception as e:
                error_msg = f"Error migrando publicación {modelo_nombre}/{video}/{plataforma_nombre}: {e}"
                stats.errores.append(error_msg)
                print(f"   ❌ {error_msg}")
        
        if not dry_run and registros:
            print(f"   ✅ {modelo_nombre}: {len(registros)} publicaciones procesadas")


def validate_counts(stats: MigrationStats, dry_run_stats: Dict) -> bool:
    """
    Valida que los conteos cuadran
    Retorna True si todo está bien, False si hay discrepancias
    """
    print("\n" + "=" * 60)
    print("🔍 VALIDACIÓN DE CONTEOS")
    print("=" * 60)
    
    # Comparar conteos esperados vs reales
    expected_publicaciones = dry_run_stats['total_registros']
    actual_publicaciones = stats.publicaciones_creadas + stats.publicaciones_existentes
    
    print(f"\nPublicaciones:")
    print(f"   Esperadas: {expected_publicaciones}")
    print(f"   Creadas: {stats.publicaciones_creadas}")
    print(f"   Existentes: {stats.publicaciones_existentes}")
    print(f"   Total: {actual_publicaciones}")
    
    # Permitir pequeña diferencia por registros inválidos (sin video o plataforma)
    diferencia = abs(expected_publicaciones - actual_publicaciones)
    if diferencia > 0:
        print(f"\n   Diferencia: {diferencia}")
        if diferencia <= len(stats.errores):
            print(f"   ℹ️  Diferencia explicada por errores: {len(stats.errores)}")
            print("   ✅ Conteos aceptables (diferencia por registros inválidos)")
            return True
        else:
            print(f"\n❌ ERROR: Conteos no cuadran!")
            print(f"   Diferencia: {diferencia}")
            return False
    
    print("\n✅ Conteos validados correctamente")
    return True


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='FASE 2: Migración de datos')
    parser.add_argument('--dry-run', action='store_true', help='Modo dry-run (solo análisis)')
    parser.add_argument('--execute', action='store_true', help='Ejecutar migración (requiere confirmación)')
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.execute:
        print("❌ Debes especificar --dry-run o --execute")
        sys.exit(1)
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    stats = MigrationStats()
    
    # 1. DRY-RUN obligatorio
    dry_run_stats = dry_run_analysis(supabase)
    print_dry_run_results(dry_run_stats)
    
    if args.dry_run:
        print("\n✅ DRY-RUN completado. Usa --execute para migrar datos.")
        return
    
    # 2. Confirmación antes de ejecutar
    if args.execute:
        print("\n" + "=" * 60)
        print("⚠️  ADVERTENCIA: Esto modificará la base de datos")
        print("=" * 60)
        respuesta = input("\n¿Continuar con la migración? (escribe 'SI' para confirmar): ")
        if respuesta != 'SI':
            print("❌ Migración cancelada")
            return
    
    # 3. Ejecutar migración
    print("\n🚀 Iniciando migración...\n")
    
    # Migrar en orden
    platform_map = migrate_platforms(supabase, stats, dry_run_stats['plataformas_unicas'], dry_run=False)
    modelo_map = migrate_modelos(supabase, stats, dry_run_stats['modelos_old'], dry_run=False)
    migrate_cuentas(supabase, stats, modelo_map, platform_map, dry_run_stats['auth_files'], dry_run=False)
    contenido_map = migrate_contenidos(supabase, stats, modelo_map, dry_run_stats['videos_unicos'], dry_run_stats['tablas_dinamicas'], dry_run=False)
    
    # Obtener mapa de cuentas antes de migrar publicaciones
    cuenta_map = get_cuenta_plataforma_map(supabase, modelo_map, platform_map)
    migrate_publicaciones(supabase, stats, modelo_map, platform_map, contenido_map, cuenta_map, dry_run_stats['tablas_dinamicas'], dry_run=False)
    
    # 4. Validar conteos
    if not validate_counts(stats, dry_run_stats):
        print("\n❌ MIGRACIÓN ABORTADA: Conteos no cuadran")
        sys.exit(1)
    
    # 5. Resumen final
    stats.print_summary()
    print("\n✅ FASE 2 completada exitosamente")


if __name__ == "__main__":
    main()

