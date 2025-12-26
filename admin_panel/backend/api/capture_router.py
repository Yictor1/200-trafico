"""
Router de Captura - Captura de network flows con Playwright
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, List
from pathlib import Path
import asyncio
import json
import uuid
import os
from datetime import datetime

router = APIRouter()

TRAFICO_ROOT = Path(__file__).resolve().parents[3]
WORKERS_DIR = TRAFICO_ROOT / "workers"
CAPTURES_DIR = TRAFICO_ROOT / "captures"  # Nueva carpeta para JSONs de captura
LOGS_DIR = TRAFICO_ROOT / "logs"  # Carpeta para logs de network

# Crear directorios si no existen
CAPTURES_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Estado de sesiones de captura (en memoria por ahora)
capture_sessions: Dict[str, dict] = {}

# Configurar Gemini si está disponible
try:
    import google.generativeai as genai
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
    else:
        gemini_model = None
except ImportError:
    gemini_model = None

# Schemas
class CaptureStartRequest(BaseModel):
    platform_name: str
    platform_url: str
    modelo: str

class CaptureStartResponse(BaseModel):
    session_id: str
    status: str
    message: str

class CaptureStatusResponse(BaseModel):
    session_id: str
    status: str  # capturing, completed, failed
    message: str
    flow_data: Optional[dict] = None

class CapturarRequest(BaseModel):
    nombre_plataforma: str

class FinalizarCapturaRequest(BaseModel):
    capture_id: str

@router.post("/plataforma/capturar")
async def capturar_plataforma(request: CapturarRequest):
    """
    PASO 8: Inicia captura de una plataforma.
    Recibe nombre_plataforma, inicia Playwright con DevTools,
    registra TODOS los network events y retorna capture_id.
    """
    try:
        capture_id = str(uuid.uuid4())
        
        # Crear sesión de captura
        capture_sessions[capture_id] = {
            "status": "capturing",
            "platform_name": request.nombre_plataforma,
            "started_at": datetime.now().isoformat(),
            "network_logs": [],
            "message": "Captura iniciada. Abre el navegador y realiza el flujo completo."
        }
        
        # Ejecutar captura en background
        asyncio.create_task(
            run_network_capture(capture_id, request.nombre_plataforma)
        )
        
        return {
            "success": True,
            "capture_id": capture_id,
            "message": f"Captura iniciada para {request.nombre_plataforma}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error iniciando captura: {str(e)}")

@router.post("/plataforma/finalizar-captura")
async def finalizar_captura(request: FinalizarCapturaRequest):
    """
    PASO 9: Finaliza captura y genera worker con Gemini.
    Obtiene network_logs, guarda en logs/, envía a Gemini,
    y guarda worker generado en workers/.
    """
    try:
        if request.capture_id not in capture_sessions:
            raise HTTPException(status_code=404, detail="Captura no encontrada")
        
        session = capture_sessions[request.capture_id]
        
        if session["status"] != "completed":
            raise HTTPException(status_code=400, detail="La captura aún no está completada")
        
        network_logs = session.get("network_logs", [])
        
        if not network_logs:
            raise HTTPException(status_code=400, detail="No hay network logs capturados")
        
        # Guardar logs en logs/[plataforma]_capture.json
        platform_name = session["platform_name"]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = LOGS_DIR / f"{platform_name}_capture_{timestamp}.json"
        
        log_data = {
            "plataforma": platform_name,
            "timestamp": datetime.now().isoformat(),
            "duracion_captura": session.get("duracion_captura", "N/A"),
            "authentication": extract_authentication_data(network_logs),
            "requests": network_logs
        }
        
        log_file.write_text(
            json.dumps(log_data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        
        # Leer workers de referencia
        kams_worker = (WORKERS_DIR / "kams.js").read_text(encoding="utf-8") if (WORKERS_DIR / "kams.js").exists() else ""
        xxxfollow_worker = (WORKERS_DIR / "xxxfollow.js").read_text(encoding="utf-8") if (WORKERS_DIR / "xxxfollow.js").exists() else ""
        
        # Generar worker con Gemini
        worker_code = await generate_worker_with_gemini(
            platform_name,
            network_logs,
            kams_worker,
            xxxfollow_worker
        )
        
        # Guardar worker
        worker_file = WORKERS_DIR / f"{platform_name}.js"
        worker_file.write_text(worker_code, encoding="utf-8")
        
        session["worker_generated"] = True
        session["worker_path"] = str(worker_file)
        session["log_file"] = str(log_file)
        
        return {
            "success": True,
            "message": f"Worker generado para {platform_name}",
            "worker_path": str(worker_file),
            "log_file": str(log_file)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finalizando captura: {str(e)}")

async def run_network_capture(capture_id: str, platform_name: str):
    """Ejecuta captura de network events con Playwright"""
    try:
        from playwright.async_api import async_playwright
        
        session = capture_sessions[capture_id]
        network_logs = []
        start_time = datetime.now()
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                devtools=True  # Abrir DevTools
            )
            context = await browser.new_context()
            page = await context.new_page()
            
            # Capturar TODOS los network events
            async def handle_request(request):
                try:
                    post_data = None
                    try:
                        post_data = request.post_data
                    except:
                        post_data = "<binary_data>"
                    
                    req_data = {
                        "order": len(network_logs) + 1,
                        "url": request.url,
                        "method": request.method,
                        "headers": dict(request.headers),
                        "body": post_data,
                        "query_params": dict(request.url.split("?")[1].split("&")) if "?" in request.url else {},
                        "timestamp": datetime.now().isoformat(),
                        "response": None,
                        "timing": None
                    }
                    
                    network_logs.append(req_data)
                except Exception as e:
                    print(f"⚠️ Error capturando request: {e}")
            
            async def handle_response(response):
                try:
                    # Buscar request correspondiente
                    for req in network_logs:
                        if req["url"] == response.url and req.get("response") is None:
                            # Capturar response
                            response_body = None
                            try:
                                content_type = response.headers.get("content-type", "")
                                if "json" in content_type or "text" in content_type:
                                    body_text = await response.text()
                                    # Limitar a 10KB
                                    if len(body_text) > 10000:
                                        response_body = body_text[:10000] + "... [truncated]"
                                    else:
                                        response_body = body_text
                            except:
                                pass
                            
                            req["response"] = {
                                "status": response.status,
                                "headers": dict(response.headers),
                                "body": response_body
                            }
                            
                            # Timing (aproximado)
                            req["timing"] = 0  # Se puede mejorar con timing real
                            break
                except Exception as e:
                    print(f"⚠️ Error capturando response: {e}")
            
            page.on("request", handle_request)
            page.on("response", handle_response)
            
            # Abrir página en blanco
            await page.goto("about:blank")
            
            print(f"🌐 Navegador abierto para captura de {platform_name}")
            print(f"   Realiza el flujo completo. Cierra cuando termines.")
            
            # Esperar a que el usuario cierre el navegador
            try:
                while browser.is_connected():
                    await asyncio.sleep(1)
            except:
                pass
            
            # Guardar estado antes de cerrar
            try:
                await browser.close()
            except:
                pass
        
        # Calcular duración
        end_time = datetime.now()
        duracion = (end_time - start_time).total_seconds()
        
        session["status"] = "completed"
        session["network_logs"] = network_logs
        session["duracion_captura"] = f"{int(duracion)}s"
        session["message"] = f"Captura completada. {len(network_logs)} requests capturadas."
        
    except Exception as e:
        import traceback
        print(f"❌ Error en captura: {str(e)}\n{traceback.format_exc()}")
        session["status"] = "failed"
        session["message"] = f"Error en captura: {str(e)}"

def extract_authentication_data(network_logs: List[dict]) -> dict:
    """Extrae información de autenticación de los network logs"""
    auth_data = {
        "tokens_encontrados": [],
        "cookies_auth": [],
        "headers_auth": []
    }
    
    for req in network_logs:
        # Buscar tokens en headers
        headers = req.get("headers", {})
        for key, value in headers.items():
            if "auth" in key.lower() or "token" in key.lower():
                auth_data["headers_auth"].append(key)
                if value and len(value) < 200:  # Evitar tokens muy largos
                    auth_data["tokens_encontrados"].append(f"{key}: {value[:50]}...")
        
        # Buscar tokens en response body
        response = req.get("response", {})
        if response and response.get("body"):
            try:
                body = json.loads(response["body"])
                for key in ["token", "access_token", "refresh_token", "auth_token"]:
                    if key in body:
                        auth_data["tokens_encontrados"].append(f"{key}: {str(body[key])[:50]}...")
            except:
                pass
    
    return auth_data

async def generate_worker_with_gemini(
    platform_name: str,
    network_logs: List[dict],
    kams_worker: str,
    xxxfollow_worker: str
) -> str:
    """Genera worker usando Gemini con el prompt especificado"""
    
    if not gemini_model:
        # Fallback: generar worker básico sin Gemini
        return generate_worker_from_flow(
            analyze_captured_flow(network_logs),
            platform_name
        )
    
    # Preparar logs JSON (limitado a primeros 50 requests para no exceder límites)
    logs_json = json.dumps(network_logs[:50], indent=2, ensure_ascii=False)
    
    # Construir prompt según PASO 10
    prompt = f"""Eres un experto en automatización web con Playwright. Tu tarea es generar un worker para publicar contenido en una plataforma específica.

WORKERS DE REFERENCIA:

Usa estos dos workers como base y estructura:

=== KAMS.JS ===

{kams_worker}

=== XXXFOLLOW.JS ===

{xxxfollow_worker}

NETWORK LOGS CAPTURADOS:

{logs_json}

INSTRUCCIONES:

Analiza los network logs y genera un worker de Playwright que:

1. **Estructura similar a los workers de referencia**
   - Sigue el patrón de exportación y funciones
   - Usa la misma estructura de manejo de errores
   - Mantén el estilo de comentarios

2. **Autenticación**
   - Use el storageState del modelo (cookies/localStorage)
   - Identifica y extrae tokens de autenticación de los logs
   - Maneja refresh tokens si existen

3. **Replicación del flujo**
   - Replica el flujo EXACTO capturado en los logs
   - Mantén el orden de las requests
   - Incluye todos los headers necesarios

4. **Manejo de errores robusto**
   - Try/catch en operaciones críticas
   - Timeouts apropiados
   - Mensajes de error descriptivos

5. **Retorno estandarizado**
   - Retorna: {{success: bool, message: string, data?: any}}
   - Incluye información útil en caso de error

6. **Comentarios en pasos críticos**
   - Explica qué hace cada sección importante
   - Documenta valores hardcoded si los hay

GENERA SOLO CÓDIGO JAVASCRIPT VÁLIDO para Playwright.
NO incluyas explicaciones fuera del código.

Plataforma: {platform_name}
"""
    
    try:
        response = gemini_model.generate_content(prompt)
        worker_code = response.text
        
        # Limpiar el código (remover markdown si existe)
        if "```javascript" in worker_code:
            worker_code = worker_code.split("```javascript")[1].split("```")[0]
        elif "```js" in worker_code:
            worker_code = worker_code.split("```js")[1].split("```")[0]
        elif "```" in worker_code:
            worker_code = worker_code.split("```")[1].split("```")[0]
        
        return worker_code.strip()
        
    except Exception as e:
        print(f"⚠️ Error generando worker con Gemini: {e}")
        # Fallback
        return generate_worker_from_flow(
            analyze_captured_flow(network_logs),
            platform_name
        )

@router.post("/capture/start", response_model=CaptureStartResponse)
async def start_capture(request: CaptureStartRequest, background_tasks: BackgroundTasks):
    """
    Inicia captura de network flow con Playwright
    
    Abre un navegador para que el usuario haga login manualmente
    y captura todas las peticiones HTTP
    """
    try:
        session_id = str(uuid.uuid4())
        
        # Crear sesión
        capture_sessions[session_id] = {
            "status": "capturing",
            "platform_name": request.platform_name,
            "platform_url": request.platform_url,
            "modelo": request.modelo,
            "started_at": datetime.now().isoformat(),
            "requests": [],
            "message": "Navegador abierto. Haz login y sube un video de prueba."
        }
        
        # Ejecutar captura en background
        background_tasks.add_task(
            run_playwright_capture,
            session_id,
            request.platform_url,
            request.platform_name,
            request.modelo
        )
        
        return {
            "session_id": session_id,
            "status": "capturing",
            "message": "Captura iniciada. Abre el navegador y realiza el login."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error iniciando captura: {str(e)}")

@router.get("/capture/status/{session_id}", response_model=CaptureStatusResponse)
async def get_capture_status(session_id: str):
    """Obtiene el estado de una sesión de captura"""
    try:
        if session_id not in capture_sessions:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        session = capture_sessions[session_id]
        
        return {
            "session_id": session_id,
            "status": session["status"],
            "message": session.get("message", ""),
            "flow_data": session.get("flow_data")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado: {str(e)}")

@router.post("/capture/stop/{session_id}")
async def stop_capture(session_id: str):
    """
    Detiene captura y genera worker automáticamente
    """
    try:
        if session_id not in capture_sessions:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        session = capture_sessions[session_id]
        
        if session["status"] != "completed":
            session["status"] = "stopped"
            session["message"] = "Captura detenida manualmente"
        
        # Generar worker si hay datos
        if session.get("flow_data"):
            worker_code = generate_worker_from_flow(
                session["flow_data"],
                session["platform_name"]
            )
            
            # Guardar worker
            worker_file = WORKERS_DIR / f"{session['platform_name']}.js"
            worker_file.write_text(worker_code)
            
            session["worker_generated"] = True
            session["worker_path"] = str(worker_file)
        
        return {
            "status": "stopped",
            "session_id": session_id,
            "worker_generated": session.get("worker_generated", False)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deteniendo captura: {str(e)}")

async def run_playwright_capture(session_id: str, url: str, platform_name: str, modelo: str):
    """
    Ejecuta Playwright para capturar network flow
    
    Esta función corre en background
    """
    try:
        from playwright.async_api import async_playwright
        
        session = capture_sessions[session_id]
        requests_captured = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            
            # Capturar requests con TODOS los detalles
            async def handle_request(request):
                try:
                    # Intentar obtener post_data
                    post_data = None
                    try:
                        post_data = request.post_data
                    except (UnicodeDecodeError, Exception):
                        post_data = "<binary_data>"
                    
                    # Capturar TODO
                    req_data = {
                        "timestamp": datetime.now().isoformat(),
                        "url": request.url,
                        "method": request.method,
                        "headers": dict(request.headers),
                        "post_data": post_data,
                        "resource_type": request.resource_type
                    }
                    
                    requests_captured.append(req_data)
                except Exception as e:
                    print(f"⚠️  Error capturando request: {e}")
            
            # Capturar responses con body completo
            async def handle_response(response):
                try:
                    for req in requests_captured:
                        if req["url"] == response.url:
                            req["status"] = response.status
                            req["response_headers"] = dict(response.headers)
                            
                            # Intentar obtener el body de la respuesta
                            try:
                                # Solo capturar body de respuestas pequeñas (< 1MB)
                                content_type = response.headers.get("content-type", "")
                                if "json" in content_type or "text" in content_type:
                                    req["response_body"] = await response.text()
                            except:
                                req["response_body"] = None
                            break
                except Exception as e:
                    print(f"⚠️  Error capturando response: {e}")
            
            page.on("request", handle_request)
            page.on("response", handle_response)
            
            # Navegar a la plataforma
            print(f"🌐 Navegando a {url}...")
            await page.goto(url)
            
            print(f"⏸️  Esperando a que el usuario complete el flujo...")
            print(f"   Máximo 10 minutos o hasta que cierres el navegador")
            
            # Esperar a que el usuario cierre el navegador
            try:
                await page.wait_for_timeout(600000)  # 10 min
            except:
                pass
            
            # Guardar estado de autenticación antes de cerrar
            try:
                auth_dir = TRAFICO_ROOT / "modelos" / modelo / ".auth"
                auth_dir.mkdir(parents=True, exist_ok=True)
                auth_file = auth_dir / f"{platform_name}.json"
                
                await context.storage_state(path=str(auth_file))
                print(f"💾 Sesión guardada en: {auth_file}")
                session["auth_file"] = str(auth_file)
            except Exception as e:
                print(f"⚠️ Error guardando sesión: {e}")

            print(f"🔒 Cerrando navegador...")
            await browser.close()
        
        print(f"📊 Analizando {len(requests_captured)} requests capturadas...")
        
        # Guardar JSON completo de captura
        capture_file = CAPTURES_DIR / f"{platform_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(capture_file, 'w', encoding='utf-8') as f:
            json.dump({
                "platform": platform_name,
                "captured_at": datetime.now().isoformat(),
                "total_requests": len(requests_captured),
                "requests": requests_captured
            }, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Captura guardada en: {capture_file}")
        session["capture_file"] = str(capture_file)
        
        # Analizar flow capturado
        flow_data = analyze_captured_flow(requests_captured)
        
        session["status"] = "completed"
        session["message"] = f"Captura completada. {len(requests_captured)} requests capturadas."
        session["flow_data"] = flow_data
        session["requests"] = requests_captured
        
        print(f"🔧 Generando worker para {platform_name}...")
        
        # Validar que flow_data no sea None
        if flow_data is None:
            print("⚠️ ADVERTENCIA: analyze_captured_flow devolvió None")
            flow_data = {
                "login": None,
                "create_post": None,
                "upload": None,
                "metadata": None,
                "auth_token": None,
                "all_api_calls": []
            }
        
        # Generar worker automáticamente
        worker_code = generate_worker_from_flow(flow_data, platform_name)
        worker_file = WORKERS_DIR / f"{platform_name}.js"
        worker_file.write_text(worker_code)
        
        session["worker_generated"] = True
        session["worker_path"] = str(worker_file)
        
        print(f"✅ Worker generado: {worker_file}")
        print(f"📁 Ruta completa: {worker_file.absolute()}")
        print(f"📊 Análisis del flujo:")
        print(f"   - Login: {'✅' if flow_data.get('login') else '❌'}")
        print(f"   - Upload: {'✅' if flow_data.get('upload') else '❌'}")
        print(f"   - Metadata: {'✅' if flow_data.get('metadata') else '❌'}")
        
    except Exception as e:
        import traceback
        error_msg = f"❌ Error CRÍTICO en captura: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        session["status"] = "failed"
        session["message"] = f"Error en captura: {str(e)}"

def analyze_captured_flow(requests: List[dict]) -> dict:
    """
    Analiza requests capturadas para identificar endpoints clave
    Busca patrones comunes en APIs de subida de video
    """
    flow = {
        "login": None,
        "upload_token": None,  # Nuevo: para obtener token de subida
        "create_post": None,
        "upload": None,
        "attach_media": None,  # Nuevo: para adjuntar media a post existente
        "metadata": None,
        "auth_token": None,
        "all_api_calls": []
    }
    
    for req in requests:
        url = req["url"].lower()
        method = req["method"]
        
        # Solo analizar llamadas API (ignorar assets estáticos)
        if req.get("resource_type") in ["document", "stylesheet", "image", "font", "media"]:
            continue
            
        # Detectar llamadas API
        if any(x in url for x in ["/api/", "/v1/", "/v2/", "/graphql"]):
            flow["all_api_calls"].append({
                "url": req["url"],
                "method": method,
                "status": req.get("status"),
                "timestamp": req.get("timestamp")
            })
        
        # Detectar obtención de upload-token
        if method == "GET" and "upload-token" in url:
            flow["upload_token"] = {
                "url": req["url"],
                "method": method,
                "headers": req["headers"]
            }
        
        # Detectar login/auth
        if method == "POST" and any(x in url for x in ["/login", "/auth", "/signin", "/session", "/token"]):
            if "upload-token" not in url:  # Evitar confundir con upload-token
                flow["login"] = {
                    "url": req["url"],
                    "method": method,
                    "headers": req["headers"]
                }
                
                # Buscar token en response
                if req.get("response_body"):
                    try:
                        body = json.loads(req["response_body"])
                        if "token" in body:
                            flow["auth_token"] = body["token"]
                        elif "access_token" in body:
                            flow["auth_token"] = body["access_token"]
                        elif isinstance(body.get("data"), dict) and "token" in body["data"]:
                            flow["auth_token"] = body["data"]["token"]
                    except:
                        pass
        
        # Detectar creación de post (sin media)
        if method == "POST" and url.endswith("/post") or "/posts" in url:
            # Debe ser creación de post, no adjuntar media
            if "/media" not in url:
                flow["create_post"] = {
                    "url": req["url"],
                    "method": method,
                    "headers": req["headers"],
                    "post_data": req.get("post_data")
                }
        
        # Detectar adjuntar media a post existente
        if method == "POST" and "/media/upload" in url and "/post/" in url:
            flow["attach_media"] = {
                "url": req["url"],
                "method": method,
                "headers": req["headers"],
                "post_data": req.get("post_data")
            }
        
        # Detectar upload de video/media
        if method in ["POST", "PUT"] and any(x in url for x in ["/upload", "/video", "/media", "/file"]):
            # Priorizar URLs que parecen ser de subida de archivos
            if not flow["upload"] or "fans-media" in url or "/video/upload" in url:
                flow["upload"] = {
                    "url": req["url"],
                    "method": method,
                    "headers": req["headers"],
                    "has_file": req.get("post_data") == "<binary_data>"
                }
        
        # Detectar envío de metadata/detalles
        if method in ["POST", "PUT", "PATCH"] and any(x in url for x in ["/details", "/metadata", "/info", "/update"]):
            if "/media" not in url and "/upload" not in url:  # Evitar confundir con upload
                flow["metadata"] = {
                    "url": req["url"],
                    "method": method,
                    "headers": req["headers"],
                    "post_data": req.get("post_data")
                }
    
    return flow

def generate_worker_from_flow(flow: dict, platform_name: str) -> str:
    """
    Genera código de worker de Playwright desde flow analizado
    Usa el patrón de kams.js como referencia
    """
    
    # Determinar la URL base
    base_url = f"https://{platform_name}.com"
    upload_data = flow.get("upload")
    if upload_data and isinstance(upload_data, dict):
        upload_full_url = upload_data.get("url")
        if upload_full_url:
            # Extraer dominio de la URL de upload
            from urllib.parse import urlparse
            parsed = urlparse(upload_full_url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
    
    # Determinar si hay un flujo de creación de post
    has_create_post = flow.get("create_post") is not None
    
    # URLs detectadas - Manejar None de forma segura
    upload_data = flow.get("upload") or {}
    metadata_data = flow.get("metadata") or {}
    create_post_data = flow.get("create_post") or {}
    
    upload_url = upload_data.get("url", "TODO_REPLACE_WITH_REAL_UPLOAD_URL") if isinstance(upload_data, dict) else "TODO_REPLACE_WITH_REAL_UPLOAD_URL"
    metadata_url = metadata_data.get("url", "TODO_REPLACE_WITH_REAL_METADATA_URL") if isinstance(metadata_data, dict) else "TODO_REPLACE_WITH_REAL_METADATA_URL"
    create_post_url = create_post_data.get("url", "") if (has_create_post and isinstance(create_post_data, dict)) else ""
    
    # Generar código usando template string normal
    template = r"""const { test } = require('@playwright/test');
const path = require('path');
const fs = require('fs');

// ==========================================
// WORKER GENERADO AUTOMÁTICAMENTE
// Plataforma: PLATFORM_NAME_PLACEHOLDER
// Generado: TIMESTAMP_PLACEHOLDER
// ==========================================

const MODEL_NAME = process.env.MODEL_NAME;
const VIDEO_PATH = process.env.VIDEO_PATH;
const VIDEO_TITLE = process.env.VIDEO_TITLE || 'Default Title';
const VIDEO_TAGS = process.env.VIDEO_TAGS || 'tag1,tag2';

if (!MODEL_NAME) {
  throw new Error('❌ ERROR: Debes especificar MODEL_NAME. Ejemplo: MODEL_NAME=yic npx playwright test ...');
}

// Ruta de autenticación
const authFile = path.join(__dirname, `../modelos/${MODEL_NAME}/.auth/PLATFORM_NAME_PLACEHOLDER.json`);

console.log(`🔐 Usando archivo de autenticación para ${MODEL_NAME}: ${authFile}`);

test.describe('Automatización PLATFORM_NAME_PLACEHOLDER', () => {

  test('Subida a PLATFORM_NAME_PLACEHOLDER', async ({ browser }) => {
    // Validaciones previas
    if (!fs.existsSync(authFile)) {
      throw new Error(`❌ No hay credenciales guardadas en ${authFile}. Ejecuta el login manual primero.`);
    }
    if (!VIDEO_PATH || !fs.existsSync(VIDEO_PATH)) {
      console.log('⚠️  No se especificó VIDEO_PATH o no existe. Se saltará la subida real.');
      return;
    }

    console.log('📂 Cargando sesión...');
    const context = await browser.newContext({ storageState: authFile });
    const page = await context.newPage();

    // 1. Navegar a la página principal para cargar cookies/tokens
    const targetUrl = 'BASE_URL_PLACEHOLDER/upload';
    console.log(`🌐 Navegando a ${targetUrl}...`);
    
    try {
        await page.goto(targetUrl);
        await page.waitForLoadState('networkidle');
    } catch (e) {
        console.warn(`⚠️ Advertencia al navegar: ${e.message}. Continuando...`);
    }

    // Verificar si estamos logueados
    if (page.url().includes('login') || page.url().includes('signin')) {
        throw new Error('❌ La sesión ha expirado. Por favor, loguéate de nuevo.');
    }

    // 2. Preparar inyección de archivo (Truco del Input Oculto)
    console.log('🔧 Preparando inyección de archivo...');
    await page.evaluate(() => {
      const input = document.createElement('input');
      input.type = 'file';
      input.id = 'gemini-upload-hack';
      input.style.display = 'none';
      document.body.appendChild(input);
    });

    await page.locator('#gemini-upload-hack').setInputFiles(VIDEO_PATH);

    // 3. Ejecutar la lógica de subida dentro del navegador
    console.log('🚀 Iniciando subida vía API interna...');
    
    const result = await page.evaluate(async ({ title, tags, uploadUrl, metadataUrl, createPostUrl, hasCreatePost }) => {
      // --- CÓDIGO QUE CORRE DENTRO DEL NAVEGADOR ---
      
      const fileInput = document.getElementById('gemini-upload-hack');
      const file = fileInput.files[0];
      if (!file) throw new Error('No se pudo cargar el archivo en el navegador');

      console.log(`📦 Preparando subida de: ${file.name} (${file.size} bytes)`);

      // Obtener token de autorización desde localStorage
      let authToken = null;
      console.log('🔍 Buscando token en localStorage...');
      
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        const value = localStorage.getItem(key);
        
        if (key.toLowerCase().includes('token') || key.toLowerCase().includes('auth')) {
          console.log(`🔑 Token encontrado en localStorage.${key}`);
          authToken = value;
          break;
        }
      }

      if (!authToken) {
        throw new Error('❌ No se encontró el token de autorización en localStorage. Asegúrate de estar logueado.');
      }

      console.log(`🔑 Usando token: ${authToken.substring(0, 30)}...`);

      // Validar URLs
      if (uploadUrl.includes('TODO_REPLACE')) {
        throw new Error('❌ DETENIDO: Las URLs de la API no se detectaron automáticamente. Debes editar el worker manualmente.');
      }

      let postId = null;

      // Paso 0 (opcional): Crear post si es necesario
      if (hasCreatePost && createPostUrl) {
        console.log('📝 Creando post...');
        
        const createResponse = await fetch(createPostUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': `Bearer ${authToken}`
          },
          body: JSON.stringify({
            title: title,
            // Agregar otros campos según sea necesario
          })
        });

        if (!createResponse.ok) {
          throw new Error(`Error creando post: ${createResponse.status}`);
        }

        const createData = await createResponse.json();
        postId = createData.id || createData.postId || (createData.data && createData.data.id);
        console.log(`✅ Post creado con ID: ${postId}`);
      }

      // Paso 1: Subir Video
      console.log(`📡 Subiendo video a ${uploadUrl}...`);
      
      const formData = new FormData();
      formData.append('video', file);
      
      // Si tenemos postId, agregarlo al FormData
      if (postId) {
        formData.append('postId', postId);
      }

      const uploadResponse = await fetch(uploadUrl, {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json, text/plain, */*',
          'Authorization': `Bearer ${authToken}`
        }
      });

      if (!uploadResponse.ok) {
        const errorText = await uploadResponse.text();
        throw new Error(`Error en subida: ${uploadResponse.status} - ${errorText}`);
      }

      const uploadData = await uploadResponse.json();
      console.log('✅ Subida completada. Respuesta:', uploadData);

      // Obtener videoId de la respuesta
      const videoId = uploadData.id || uploadData.videoId || (uploadData.data && uploadData.data.id);

      if (!videoId) {
        return { success: false, step: 'upload', response: uploadData, message: 'No se encontró videoId en la respuesta' };
      }

      // Paso 2: Enviar Metadata (si existe endpoint separado)
      if (metadataUrl && !metadataUrl.includes('TODO_REPLACE')) {
        console.log('📋 Enviando metadata...');
        
        const detailsPayload = {
          videoId: videoId,
          title: title,
          tags: tags,
          is_nsfw: true
        };

        const detailsResponse = await fetch(metadataUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': `Bearer ${authToken}`
          },
          body: JSON.stringify(detailsPayload)
        });

        if (!detailsResponse.ok) {
          const errorText = await detailsResponse.text();
          console.warn(`⚠️ Error en metadata: ${errorText}`);
        } else {
          const detailsData = await detailsResponse.json();
          console.log('✅ Metadata enviada:', detailsData);
        }
      }

      return { success: true, videoId, postId };

    }, { 
      title: VIDEO_TITLE, 
      tags: VIDEO_TAGS,
      uploadUrl: 'UPLOAD_URL_PLACEHOLDER',
      metadataUrl: 'METADATA_URL_PLACEHOLDER',
      createPostUrl: 'CREATE_POST_URL_PLACEHOLDER',
      hasCreatePost: HAS_CREATE_POST_PLACEHOLDER
    });

    console.log('🏁 Resultado final:', JSON.stringify(result, null, 2));

    if (result.success) {
      console.log(`✅ VIDEO PUBLICADO EXITOSAMENTE! ID: ${result.videoId}`);
    } else {
      console.error('❌ Falló la secuencia:', result.message);
      if (result.step === 'upload') {
        console.log('🔍 Respuesta de subida para análisis:', result.response);
      }
    }

    await context.close();
  });
});
"""
    
    # Reemplazar variables
    code = template.replace("PLATFORM_NAME_PLACEHOLDER", platform_name)
    code = code.replace("TIMESTAMP_PLACEHOLDER", datetime.now().isoformat())
    code = code.replace("BASE_URL_PLACEHOLDER", base_url)
    code = code.replace("UPLOAD_URL_PLACEHOLDER", upload_url)
    code = code.replace("METADATA_URL_PLACEHOLDER", metadata_url)
    code = code.replace("CREATE_POST_URL_PLACEHOLDER", create_post_url)
    code = code.replace("HAS_CREATE_POST_PLACEHOLDER", "true" if has_create_post else "false")
    
    return code
