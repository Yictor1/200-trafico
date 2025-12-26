"""
Router para abrir navegador con perfil persistente usando userDataDir de Chromium.
Todas las sesiones (cookies, localStorage, sessionStorage, etc.) se guardan automáticamente.
"""
from fastapi import APIRouter, HTTPException
from pathlib import Path
import sys
import asyncio
from playwright.async_api import async_playwright

TRAFICO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(TRAFICO_ROOT / "src"))

router = APIRouter()

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

