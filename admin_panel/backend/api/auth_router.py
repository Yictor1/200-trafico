"""
Router de Autenticación - Captura de credenciales de plataformas
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict
from pathlib import Path
import uuid
from datetime import datetime

router = APIRouter()

TRAFICO_ROOT = Path(__file__).resolve().parents[3]
MODELOS_DIR = TRAFICO_ROOT / "modelos"

# Estado de sesiones de autenticación (en memoria)
auth_sessions: Dict[str, dict] = {}

# Schemas
class AuthStartRequest(BaseModel):
    modelo: str
    plataforma: str
    url: str

class AuthStartResponse(BaseModel):
    session_id: str
    status: str
    message: str

class AuthStatusResponse(BaseModel):
    session_id: str
    status: str  # authenticating, completed, failed
    message: str

@router.post("/auth/start", response_model=AuthStartResponse)
async def start_auth(request: AuthStartRequest, background_tasks: BackgroundTasks):
    """
    Inicia captura de credenciales con Playwright
    
    Abre un navegador para que el usuario haga login manualmente
    y guarda las credenciales en .auth/{plataforma}.json
    """
    try:
        session_id = str(uuid.uuid4())
        
        # Verificar que el modelo existe
        modelo_dir = MODELOS_DIR / request.modelo
        if not modelo_dir.exists():
            raise HTTPException(status_code=404, detail=f"Modelo '{request.modelo}' no encontrado")
        
        # Crear sesión
        auth_sessions[session_id] = {
            "status": "authenticating",
            "modelo": request.modelo,
            "plataforma": request.plataforma,
            "url": request.url,
            "started_at": datetime.now().isoformat(),
            "message": f"Navegador abierto para {request.plataforma}. Haz login manualmente."
        }
        
        # Ejecutar captura en background
        background_tasks.add_task(
            run_playwright_auth,
            session_id,
            request.modelo,
            request.plataforma,
            request.url
        )
        
        return {
            "session_id": session_id,
            "status": "authenticating",
            "message": f"Navegador abierto para {request.plataforma}. Completa el login."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error iniciando autenticación: {str(e)}")

@router.get("/auth/status/{session_id}", response_model=AuthStatusResponse)
async def get_auth_status(session_id: str):
    """Obtiene el estado de una sesión de autenticación"""
    try:
        if session_id not in auth_sessions:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        session = auth_sessions[session_id]
        
        return {
            "session_id": session_id,
            "status": session["status"],
            "message": session.get("message", "")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado: {str(e)}")

async def run_playwright_auth(session_id: str, modelo: str, plataforma: str, url: str):
    """
    Ejecuta Playwright para capturar credenciales
    
    Esta función corre en background
    """
    try:
        from playwright.async_api import async_playwright
        import json
        
        session = auth_sessions[session_id]
        auth_file = MODELOS_DIR / modelo / ".auth" / f"{plataforma}.json"
        
        # Asegurar que existe el directorio .auth
        auth_file.parent.mkdir(parents=True, exist_ok=True)
        
        async with async_playwright() as p:
            # Lanzar navegador en modo NO headless para que el usuario vea
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',  # Evitar detección de bot
                ]
            )
            
            # Si ya existe una sesión guardada, cargarla
            context_options = {}
            if auth_file.exists():
                print(f"🔄 Cargando sesión existente de {plataforma}...")
                context_options['storage_state'] = str(auth_file)
            
            # Crear contexto (con o sin sesión previa)
            context = await browser.new_context(**context_options)
            page = await context.new_page()
            
            print(f"🌐 Abriendo {url} para {modelo} ({plataforma})...")
            await page.goto(url)
            
            print(f"⏸️  Esperando a que {modelo} complete el login en {plataforma}...")
            print(f"   El navegador se cerrará automáticamente en 5 minutos o cuando cierres la ventana.")
            print(f"   💡 Tip: Después de hacer login, espera unos segundos antes de cerrar el navegador.")
            
            # Esperar a que el usuario cierre el navegador o timeout de 5 minutos
            try:
                await page.wait_for_timeout(300000)  # 5 minutos
            except:
                pass
            
            # Guardar credenciales (cookies, localStorage, sessionStorage)
            print(f"💾 Guardando credenciales de {plataforma}...")
            
            # Guardar el estado completo del contexto
            await context.storage_state(path=str(auth_file))
            
            print(f"✅ Archivo guardado: {auth_file}")
            print(f"📊 Tamaño del archivo: {auth_file.stat().st_size} bytes")
            
            await browser.close()
        
        session["status"] = "completed"
        session["message"] = f"Credenciales guardadas en {auth_file.name}"
        session["auth_file"] = str(auth_file)
        
        print(f"✅ Credenciales de {plataforma} guardadas para {modelo}")
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        session["status"] = "failed"
        session["message"] = f"Error en autenticación: {str(e)}"
        print(f"❌ Error guardando credenciales: {e}")
        print(f"📋 Detalle del error:\n{error_detail}")

