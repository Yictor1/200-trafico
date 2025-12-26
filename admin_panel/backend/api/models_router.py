"""
Router de Modelos - CRUD de modelos (PRD)

✅ MIGRADO A ESQUEMA PRD (FASE 5 ETAPA 3.3)
================================================================================

Este router usa exclusivamente el esquema PRD:
- modelos.id (UUID PK) + modelos.nombre (TEXT UNIQUE)
- modelos.configuracion_distribucion (JSONB)
- NO usa funciones legacy de supabase_client.py
- NO crea tablas dinámicas

Esquema PRD:
- modelos (tabla maestra con id UUID)
- cuentas_plataforma (relacional para plataformas)
- publicaciones (unificada con FK a modelos)

Última actualización: 2025-12-25
Ver: Migracion/FASE5_ETAPA3_COMPLETADA.md
================================================================================
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import sys
import json
import shutil
from datetime import datetime
from PIL import Image
import io

# Importar cliente de Supabase del proyecto Trafico
TRAFICO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(TRAFICO_ROOT / "src"))

try:
    from database.supabase_client import supabase
    SUPABASE_AVAILABLE = True
except Exception as e:
    print(f"⚠️  Error importando Supabase: {e}")
    SUPABASE_AVAILABLE = False
    supabase = None

router = APIRouter()

# Schemas PRD
class ModelResponse(BaseModel):
    nombre: str  # PRD usa "nombre" (no "modelo")
    telegram_user_id: str = ""
    telegram_username: str = ""  # Mantener para compatibilidad/display
    configuracion_distribucion: Optional[dict] = None  # PRD: JSONB config
    profile_photo: Optional[str] = None
    caracteristicas: Optional[dict] = None
    striphours_url: Optional[str] = None
    striphours_username: Optional[str] = None

def save_profile_photo(file: UploadFile, modelo_dir: Path) -> str:
    """Guarda la foto de perfil y la recorta a 1:1"""
    try:
        print(f"📸 Procesando foto de perfil...")
        
        # Leer imagen
        image_data = file.file.read()
        if not image_data:
            raise Exception("El archivo de imagen está vacío")
        
        print(f"📸 Imagen leída: {len(image_data)} bytes")
        image = Image.open(io.BytesIO(image_data))
        print(f"📸 Dimensiones originales: {image.size}")
        
        # Convertir a RGB si es necesario
        if image.mode != 'RGB':
            print(f"📸 Convirtiendo de {image.mode} a RGB")
            image = image.convert('RGB')
        
        # Recortar a cuadrado 1:1 (centrado)
        width, height = image.size
        size = min(width, height)
        left = (width - size) // 2
        top = (height - size) // 2
        right = left + size
        bottom = top + size
        
        image = image.crop((left, top, right, bottom))
        print(f"📸 Imagen recortada a: {image.size}")
        
        # Redimensionar a 512x512
        image = image.resize((512, 512), Image.Resampling.LANCZOS)
        print(f"📸 Imagen redimensionada a: {image.size}")
        
        # Guardar
        photo_path = modelo_dir / "profile_photo.jpg"
        image.save(photo_path, "JPEG", quality=95)
        
        # Verificar que se guardó
        if not photo_path.exists():
            raise Exception(f"No se pudo crear el archivo: {photo_path}")
        
        file_size = photo_path.stat().st_size
        print(f"✅ Foto guardada: {photo_path} ({file_size} bytes)")
        
        return "profile_photo.jpg"
    except Exception as e:
        import traceback
        print(f"❌ Error en save_profile_photo: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=f"Error procesando imagen: {str(e)}")

def load_config_json(modelo_dir: Path) -> dict:
    """Carga config.json del modelo"""
    config_path = modelo_dir / "config.json"
    if config_path.exists():
        return json.loads(config_path.read_text(encoding="utf-8"))
    return {}

def save_config_json(modelo_dir: Path, config: dict):
    """Guarda config.json del modelo"""
    try:
        config_path = modelo_dir / "config.json"
        config_json = json.dumps(config, indent=2, ensure_ascii=False)
        config_path.write_text(config_json, encoding="utf-8")
        
        # Verificar que se guardó correctamente
        if not config_path.exists():
            raise Exception(f"No se pudo crear el archivo: {config_path}")
        
        # Verificar que se puede leer
        loaded = json.loads(config_path.read_text(encoding="utf-8"))
        if not loaded:
            raise Exception(f"El archivo se creó pero está vacío: {config_path}")
        
        print(f"✅ config.json guardado y verificado: {config_path}")
    except Exception as e:
        print(f"❌ Error en save_config_json: {e}")
        import traceback
        print(traceback.format_exc())
        raise

@router.get("/models", response_model=List[ModelResponse])
async def get_models():
    """Obtiene lista de todos los modelos desde Supabase (esquema PRD)"""
    try:
        if not SUPABASE_AVAILABLE or supabase is None:
            print("⚠️  Supabase no está disponible - retornando lista vacía")
            return []
        
        print(f"🔍 Consultando tabla 'modelos' en Supabase (esquema PRD)...")
        
        # Intentar consultar Supabase con timeout
        try:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    lambda: supabase.table("modelos").select("*").execute()
                )
                response = future.result(timeout=5)
        except concurrent.futures.TimeoutError:
            print("❌ Timeout consultando Supabase (más de 5 segundos)")
            return []
        except Exception as supabase_error:
            print(f"❌ Error consultando Supabase: {supabase_error}")
            return []
        
        if not hasattr(response, 'data'):
            print("⚠️  Respuesta de Supabase sin atributo 'data'")
            return []
        
        print(f"✅ Respuesta de Supabase: {len(response.data) if response.data else 0} modelos")
        
        if not response.data:
            print("ℹ️  No hay modelos en la tabla 'modelos'")
            return []
        
        MODELOS_DIR = TRAFICO_ROOT / "modelos"
        models = []
        for model in response.data:
            try:
                model_data = dict(model)
                # PRD usa "nombre" (no "modelo")
                modelo_nombre = model_data.get("nombre", "")
                if not modelo_nombre:
                    print(f"⚠️ Modelo sin nombre: {model_data}")
                    continue
                
                modelo_dir = MODELOS_DIR / modelo_nombre
                
                # Cargar config.json si existe
                config = load_config_json(modelo_dir) if modelo_dir.exists() else {}
                
                # Agregar datos del config.json y PRD
                model_data["telegram_user_id"] = config.get("telegram_user_id", "")
                model_data["telegram_username"] = config.get("telegram_username", "")
                model_data["profile_photo"] = "profile_photo.jpg" if (modelo_dir / "profile_photo.jpg").exists() else None
                model_data["caracteristicas"] = config.get("caracteristicas", {})
                model_data["configuracion_distribucion"] = model_data.get("configuracion_distribucion", {})
                model_data["striphours_url"] = model_data.get("striphours_url")
                model_data["striphours_username"] = model_data.get("striphours_username")
                
                models.append(model_data)
            except Exception as e:
                print(f"⚠️ Error procesando modelo {model.get('nombre', 'unknown')}: {e}")
                continue
        
        print(f"✅ Retornando {len(models)} modelos procesados")
        return models
    except Exception as e:
        import traceback
        error_msg = f"❌ Error obteniendo modelos: {e}\n{traceback.format_exc()}"
        print(error_msg)
        return []

@router.post("/models", response_model=ModelResponse)
async def create_model(
    nombre: str = Form(...),
    telegram_user_id: str = Form(...),
    plataformas: str = Form(...),
    hora_inicio: str = Form(...),
    ventana_horas: int = Form(...),
    caracteristicas: str = Form(...),
    profile_photo: UploadFile = File(...),
    striphours_url: Optional[str] = Form(None)
):
    """Crea un nuevo modelo (esquema PRD)"""
    try:
        # Validar nombre
        import re
        nombre_normalizado = re.sub(r'\s+', '_', nombre.lower())
        
        # Validar que no exista (PRD usa "nombre")
        existing = supabase.table("modelos").select("*").eq("nombre", nombre_normalizado).execute()
        if existing.data:
            raise HTTPException(status_code=400, detail=f"Modelo '{nombre_normalizado}' ya existe")
        
        # Validar Telegram User ID
        if not telegram_user_id.strip().isdigit():
            raise HTTPException(status_code=400, detail="Telegram User ID debe ser un número")
        
        # Validar hora_inicio
        try:
            datetime.strptime(hora_inicio, "%H:%M")
        except ValueError:
            raise HTTPException(status_code=400, detail="hora_inicio debe estar en formato HH:MM")
        
        # Validar ventana_horas
        if ventana_horas < 1 or ventana_horas > 24:
            raise HTTPException(status_code=400, detail="ventana_horas debe estar entre 1 y 24")
        
        # Validar plataformas
        if not plataformas.strip():
            raise HTTPException(status_code=400, detail="plataformas no puede estar vacío")
        
        # Normalizar plataformas
        plataformas_list = [p.strip().lower() for p in plataformas.split(',') if p.strip()]
        if not plataformas_list:
            raise HTTPException(status_code=400, detail="Debe especificar al menos una plataforma válida")
        
        # Parsear características
        try:
            caracteristicas_dict = json.loads(caracteristicas)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="caracteristicas debe ser JSON válido")
        
        # Extraer username de striphours_url
        striphours_username = None
        if striphours_url:
            pattern = r'striphours\.com/user/([^/?#]+)'
            match = re.search(pattern, striphours_url)
            if match:
                striphours_username = match.group(1)
            else:
                raise HTTPException(
                    status_code=400,
                    detail="URL de Striphours inválida. Debe ser: https://www.striphours.com/user/username"
                )
        
        # Crear modelo en Supabase (esquema PRD - NO crea tablas dinámicas)
        print(f"✅ Creando modelo en Supabase (esquema PRD): {nombre_normalizado}")
        modelo_data = {
            "nombre": nombre_normalizado,
            "configuracion_distribucion": {
                "plataformas": plataformas_list,
                "hora_inicio": hora_inicio,
                "ventana_horas": ventana_horas
            },
            "estado": "activa"
        }
        
        if striphours_url:
            modelo_data["striphours_url"] = striphours_url
            modelo_data["striphours_username"] = striphours_username
        
        create_response = supabase.table("modelos").insert(modelo_data).execute()
        if not create_response.data:
            raise HTTPException(status_code=500, detail="Error creando modelo en Supabase")
        
        print(f"✅ Modelo creado en Supabase: {nombre_normalizado}")
        
        # Crear carpeta local
        MODELOS_DIR = TRAFICO_ROOT / "modelos"
        modelo_dir = MODELOS_DIR / nombre_normalizado
        
        if not MODELOS_DIR.exists():
            MODELOS_DIR.mkdir(parents=True, exist_ok=True)
        
        modelo_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Carpeta creada: {modelo_dir}")
        
        # Crear browser_profile/
        browser_profile_dir = modelo_dir / "browser_profile"
        browser_profile_dir.mkdir(exist_ok=True)
        print(f"✅ browser_profile creado")
        
        # Guardar foto de perfil
        photo_filename = save_profile_photo(profile_photo, modelo_dir)
        print(f"✅ Foto guardada: {photo_filename}")
        
        # Crear config.json
        config = {
            "nombre": nombre_normalizado,
            "telegram_user_id": telegram_user_id.strip(),
            "profile_photo": photo_filename,
            "hora_inicio": hora_inicio,
            "ventana_horas": ventana_horas,
            "caracteristicas": caracteristicas_dict,
            "plataformas": plataformas_list,
            "created_at": datetime.now().isoformat()
        }
        save_config_json(modelo_dir, config)
        print(f"✅ config.json guardado")
        
        # Retornar modelo creado
        created = supabase.table("modelos").select("*").eq("nombre", nombre_normalizado).execute()
        if not created.data:
            raise HTTPException(status_code=500, detail="Modelo creado pero no se pudo recuperar")
        
        model_data = dict(created.data[0])
        model_data["telegram_user_id"] = telegram_user_id.strip()
        model_data["profile_photo"] = photo_filename
        model_data["caracteristicas"] = caracteristicas_dict
        
        print(f"✅ Modelo creado exitosamente: {nombre_normalizado}")
        return model_data
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"❌ Error creando modelo: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)
        raise HTTPException(status_code=500, detail=f"Error creando modelo: {str(e)}")

@router.put("/models/{nombre}/editar", response_model=ModelResponse)
async def update_model(
    nombre: str,
    telegram_user_id: Optional[str] = Form(None),
    plataformas: Optional[str] = Form(None),
    hora_inicio: Optional[str] = Form(None),
    ventana_horas: Optional[int] = Form(None),
    caracteristicas: Optional[str] = Form(None),
    profile_photo: Optional[UploadFile] = File(None),
    striphours_url: Optional[str] = Form(None)
):
    """Actualiza un modelo existente (esquema PRD)"""
    try:
        # Verificar que existe (PRD usa "nombre")
        existing = supabase.table("modelos").select("*").eq("nombre", nombre).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail=f"Modelo '{nombre}' no encontrado")
        
        MODELOS_DIR = TRAFICO_ROOT / "modelos"
        modelo_dir = MODELOS_DIR / nombre
        
        if not modelo_dir.exists():
            raise HTTPException(status_code=404, detail=f"Carpeta del modelo '{nombre}' no encontrada")
        
        # Cargar config actual
        config = load_config_json(modelo_dir)
        
        # Preparar actualización para Supabase (configuracion_distribucion)
        config_dist = existing.data[0].get("configuracion_distribucion", {})
        updates = {}
        
        # Actualizar campos si se proporcionan
        if telegram_user_id is not None:
            if not telegram_user_id.strip().isdigit():
                raise HTTPException(status_code=400, detail="Telegram User ID debe ser un número")
            config["telegram_user_id"] = telegram_user_id.strip()
        
        if plataformas is not None:
            if not plataformas.strip():
                raise HTTPException(status_code=400, detail="plataformas no puede estar vacío")
            plataformas_list = [p.strip().lower() for p in plataformas.split(',') if p.strip()]
            if not plataformas_list:
                raise HTTPException(status_code=400, detail="Debe especificar al menos una plataforma válida")
            config_dist["plataformas"] = plataformas_list
            updates["configuracion_distribucion"] = config_dist
        
        if hora_inicio is not None:
            try:
                datetime.strptime(hora_inicio, "%H:%M")
            except ValueError:
                raise HTTPException(status_code=400, detail="hora_inicio debe estar en formato HH:MM")
            config["hora_inicio"] = hora_inicio
            config_dist["hora_inicio"] = hora_inicio
            updates["configuracion_distribucion"] = config_dist
        
        if ventana_horas is not None:
            if ventana_horas < 1 or ventana_horas > 24:
                raise HTTPException(status_code=400, detail="ventana_horas debe estar entre 1 y 24")
            config["ventana_horas"] = ventana_horas
            config_dist["ventana_horas"] = ventana_horas
            updates["configuracion_distribucion"] = config_dist
        
        if caracteristicas is not None:
            try:
                caracteristicas_dict = json.loads(caracteristicas)
                config["caracteristicas"] = caracteristicas_dict
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="caracteristicas debe ser JSON válido")
        
        if profile_photo is not None:
            # Eliminar foto anterior
            old_photo = modelo_dir / "profile_photo.jpg"
            if old_photo.exists():
                old_photo.unlink()
            # Guardar nueva foto
            photo_filename = save_profile_photo(profile_photo, modelo_dir)
            config["profile_photo"] = photo_filename
        
        if striphours_url is not None:
            striphours_username = None
            if striphours_url.strip():
                import re
                pattern = r'striphours\.com/user/([^/?#]+)'
                match = re.search(pattern, striphours_url)
                if match:
                    striphours_username = match.group(1)
                else:
                    raise HTTPException(
                        status_code=400,
                        detail="URL de Striphours inválida"
                    )
            updates["striphours_url"] = striphours_url if striphours_url.strip() else None
            updates["striphours_username"] = striphours_username
        
        # Actualizar en Supabase
        if updates:
            supabase.table("modelos").update(updates).eq("nombre", nombre).execute()
        
        # Guardar config.json actualizado
        save_config_json(modelo_dir, config)
        
        # Retornar modelo actualizado
        updated = supabase.table("modelos").select("*").eq("nombre", nombre).execute()
        if not updated.data:
            raise HTTPException(status_code=500, detail="Error actualizando modelo")
        
        model_data = dict(updated.data[0])
        model_data["telegram_user_id"] = config.get("telegram_user_id", "")
        model_data["telegram_username"] = config.get("telegram_username", "")
        model_data["profile_photo"] = config.get("profile_photo")
        model_data["caracteristicas"] = config.get("caracteristicas", {})
        
        return model_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando modelo: {str(e)}")

@router.delete("/models/{nombre}")
async def delete_model(nombre: str):
    """Elimina un modelo (esquema PRD)"""
    try:
        # Verificar que existe
        existing = supabase.table("modelos").select("*").eq("nombre", nombre).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail=f"Modelo '{nombre}' no encontrado")
        
        # Eliminar de Supabase
        supabase.table("modelos").delete().eq("nombre", nombre).execute()
        
        # Eliminar carpeta local
        MODELOS_DIR = TRAFICO_ROOT / "modelos"
        modelo_dir = MODELOS_DIR / nombre
        if modelo_dir.exists():
            shutil.rmtree(modelo_dir)
            print(f"✅ Carpeta eliminada: {modelo_dir}")
        
        return {"status": "deleted", "modelo": nombre}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando modelo: {str(e)}")

@router.get("/models/{nombre}", response_model=ModelResponse)
async def get_model(nombre: str):
    """Obtiene un modelo específico (esquema PRD)"""
    try:
        model = supabase.table("modelos").select("*").eq("nombre", nombre).execute()
        if not model.data:
            raise HTTPException(status_code=404, detail=f"Modelo '{nombre}' no encontrado")
        
        MODELOS_DIR = TRAFICO_ROOT / "modelos"
        modelo_dir = MODELOS_DIR / nombre
        
        # Cargar config.json si existe
        config = load_config_json(modelo_dir) if modelo_dir.exists() else {}
        
        model_data = dict(model.data[0])
        model_data["telegram_user_id"] = config.get("telegram_user_id", "")
        model_data["telegram_username"] = config.get("telegram_username", "")
        model_data["profile_photo"] = "profile_photo.jpg" if (modelo_dir / "profile_photo.jpg").exists() else None
        model_data["caracteristicas"] = config.get("caracteristicas", {})
        
        return model_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo modelo: {str(e)}")

@router.get("/models/{nombre}/profile-photo")
async def get_profile_photo(nombre: str):
    """Obtiene la foto de perfil de un modelo"""
    from fastapi.responses import FileResponse
    
    MODELOS_DIR = TRAFICO_ROOT / "modelos"
    photo_path = MODELOS_DIR / nombre / "profile_photo.jpg"
    
    if not photo_path.exists():
        raise HTTPException(status_code=404, detail="Foto de perfil no encontrada")
    
    return FileResponse(photo_path)

@router.get("/models/test-supabase")
async def test_supabase():
    """Endpoint de prueba para verificar conexión a Supabase"""
    try:
        if not SUPABASE_AVAILABLE or supabase is None:
            return {
                "success": False,
                "error": "Supabase no está disponible. Verifica SUPABASE_ANON_KEY en .env"
            }
        
        print("🔍 Probando conexión a Supabase...")
        response = supabase.table("modelos").select("count", count="exact").execute()
        return {
            "success": True,
            "message": "Conexión a Supabase exitosa",
            "count": response.count if hasattr(response, 'count') else "N/A"
        }
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }
