"""
Router para abrir navegador con perfil persistente usando userDataDir de Chromium.
Todas las sesiones (cookies, localStorage, sessionStorage, etc.) se guardan automáticamente.
Además, exporta storageState a .auth/ para compatibilidad con workers.
"""
from fastapi import APIRouter, HTTPException
from pathlib import Path
import sys
import asyncio
from playwright.async_api import async_playwright

TRAFICO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(TRAFICO_ROOT / "src"))

router = APIRouter()

# Mapeo de dominios a nombres de plataformas
PLATFORM_DOMAINS = {
    'kams.com': 'kams',
    'xxxfollow.com': 'xxxfollow',
    'fikfap.com': 'fikfap',
    'myclub.com': 'myclub',
    'fansly.com': 'fansly',
    'onlyfans.com': 'onlyfans',
}

async def export_storage_state_to_auth(modelo_id: str, user_data_dir: str):
    """
    Exporta storageState desde browser_profile a .auth/ para todas las plataformas conocidas.
    Esto permite que los workers usen las sesiones guardadas.
    
    Estrategia: Exporta el storageState completo para todas las plataformas conocidas.
    Si una plataforma no tiene sesión, el archivo se crea igual pero estará vacío.
    Los workers verificarán si existe y si tiene datos válidos.
    """
    try:
        MODELOS_DIR = TRAFICO_ROOT / "modelos"
        modelo_dir = MODELOS_DIR / modelo_id
        auth_dir = modelo_dir / ".auth"
        auth_dir.mkdir(parents=True, exist_ok=True)
        
        # Crear un contexto temporal para leer el storageState
        async with async_playwright() as p:
            # Abrir contexto persistente temporalmente solo para leer
            context = await p.chromium.launch_persistent_context(
                user_data_dir,
                headless=True,  # Headless para solo leer
            )
            
            # Obtener storageState completo
            storage_state = await context.storage_state()
            
            # Detectar plataformas desde las cookies y localStorage
            detected_platforms = set()
            cookies = storage_state.get('cookies', [])
            origins = storage_state.get('origins', [])
            
            # Detectar por cookies
            for cookie in cookies:
                domain = cookie.get('domain', '')
                for platform_domain, platform_name in PLATFORM_DOMAINS.items():
                    if platform_domain in domain:
                        detected_platforms.add(platform_name)
            
            # Detectar por origins (localStorage/sessionStorage)
            for origin in origins:
                origin_url = origin.get('origin', '')
                for platform_domain, platform_name in PLATFORM_DOMAINS.items():
                    if platform_domain in origin_url:
                        detected_platforms.add(platform_name)
            
            # Exportar para todas las plataformas detectadas
            if detected_platforms:
                import json
                for platform in detected_platforms:
                    auth_file = auth_dir / f"{platform}.json"
                    with open(auth_file, 'w', encoding='utf-8') as f:
                        json.dump(storage_state, f, indent=2, ensure_ascii=False)
                    file_size = auth_file.stat().st_size
                    print(f"✅ StorageState exportado para {platform}: {auth_file} ({file_size} bytes)")
            
            # Si no detectamos ninguna plataforma, exportar para las principales por defecto
            # Esto es útil si el usuario hizo login pero no detectamos la plataforma
            if not detected_platforms:
                import json
                # Exportar para las plataformas más comunes
                default_platforms = ['kams', 'xxxfollow']
                for platform in default_platforms:
                    auth_file = auth_dir / f"{platform}.json"
                    with open(auth_file, 'w', encoding='utf-8') as f:
                        json.dump(storage_state, f, indent=2, ensure_ascii=False)
                    file_size = auth_file.stat().st_size
                    if file_size > 100:  # Solo mostrar si tiene contenido significativo
                        print(f"✅ StorageState exportado (por defecto) para {platform}: {auth_file} ({file_size} bytes)")
                    else:
                        print(f"ℹ️  Archivo creado para {platform} pero sin sesión activa: {auth_file}")
            
            await context.close()
            
    except Exception as e:
        print(f"⚠️  Error exportando storageState (no crítico): {e}")
        import traceback
        print(traceback.format_exc())

@router.post("/navegador/abrir/{modelo_id}")
async def abrir_navegador(modelo_id: str):
    """
    Abre un navegador Playwright con persistencia usando userDataDir.
    Todas las sesiones, cookies, localStorage, etc. se guardan automáticamente.
    """
    try:
        MODELOS_DIR = TRAFICO_ROOT / "modelos"
        modelo_dir = MODELOS_DIR / modelo_id
        
        if not modelo_dir.exists():
            raise HTTPException(status_code=404, detail=f"Modelo '{modelo_id}' no encontrado")
        
        browser_profile_dir = modelo_dir / "browser_profile"
        browser_profile_dir.mkdir(parents=True, exist_ok=True)
        
        # Usar el browser_profile como userDataDir para persistencia automática
        # Esto guarda TODO: cookies, localStorage, sessionStorage, cache, etc.
        user_data_dir = str(browser_profile_dir)
        
        print(f"🌐 Abriendo navegador persistente para modelo '{modelo_id}'")
        print(f"   📁 Perfil del navegador: {user_data_dir}")
        
        # Ejecutar Playwright en background
        async def run_browser():
            browser = None
            context = None
            try:
                async with async_playwright() as p:
                    # Lanzar navegador con userDataDir persistente
                    # Esto hace que TODAS las sesiones se guarden automáticamente
                    context = await p.chromium.launch_persistent_context(
                        user_data_dir,
                        headless=False,
                        viewport={"width": 1920, "height": 1080},
                        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
                    )
                    
                    # Abrir una página inicial
                    if len(context.pages) == 0:
                        page = await context.new_page()
                    else:
                        page = context.pages[0]
                    
                    # Navegar a about:blank
                    await page.goto("about:blank")
                    
                    print(f"✅ Navegador abierto para modelo '{modelo_id}'")
                    print(f"   💡 Inicia sesión en las plataformas que necesites.")
                    print(f"   💡 Todas las sesiones se guardan AUTOMÁTICAMENTE.")
                    print(f"   💡 Cierra el navegador cuando termines.")
                    
                    # Esperar a que el usuario cierre todas las páginas
                    try:
                        while True:
                            await asyncio.sleep(1)
                            # Verificar si quedan páginas abiertas
                            if len(context.pages) == 0:
                                print(f"🔒 Todas las páginas cerradas por el usuario")
                                break
                    except Exception as e:
                        print(f"⚠️ Error monitoreando navegador: {e}")
                    
                    # Cerrar context (esto guarda automáticamente todo)
                    print(f"💾 Cerrando navegador y guardando sesiones...")
                    try:
                        await context.close()
                        print(f"✅ Navegador cerrado. Sesiones guardadas automáticamente en:")
                        print(f"   {user_data_dir}")
                    except Exception as close_error:
                        # El context puede ya estar cerrado si el usuario cerró todas las pestañas
                        # Esto es normal con launch_persistent_context
                        if "closed" in str(close_error).lower() or "target" in str(close_error).lower():
                            print(f"✅ Navegador ya estaba cerrado. Sesiones guardadas automáticamente en:")
                            print(f"   {user_data_dir}")
                        else:
                            print(f"⚠️ Error cerrando context (no crítico): {close_error}")
                    
                    print(f"📋 Sesiones persistentes guardadas en el perfil del navegador")
                    
                    # Exportar storageState a .auth/ para compatibilidad con workers
                    print(f"🔄 Exportando storageState a .auth/ para workers...")
                    await export_storage_state_to_auth(modelo_id, user_data_dir)
                        
            except Exception as e:
                print(f"❌ Error en run_browser: {e}")
                import traceback
                print(traceback.format_exc())
                if context:
                    try:
                        await context.close()
                    except Exception as close_error:
                        # Ignorar errores al cerrar si ya está cerrado
                        if "closed" not in str(close_error).lower():
                            print(f"⚠️ Error cerrando context después de error: {close_error}")
        
        # Ejecutar en background (no bloquea la respuesta)
        asyncio.create_task(run_browser())
        
        return {
            "success": True,
            "message": f"Navegador persistente abierto para '{modelo_id}'. Todas las sesiones se guardan automáticamente.",
            "modelo": modelo_id,
            "profile_dir": user_data_dir
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error abriendo navegador: {str(e)}")

