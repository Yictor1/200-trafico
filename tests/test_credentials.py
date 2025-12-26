#!/usr/bin/env python3
"""
Script para probar credenciales guardadas
Abre el navegador con las credenciales de un modelo
"""
import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

async def test_credentials(modelo: str, plataforma: str):
    """Abre navegador con credenciales guardadas"""
    
    # Rutas
    TRAFICO_ROOT = Path(__file__).resolve().parent
    auth_file = TRAFICO_ROOT / "modelos" / modelo / ".auth" / f"{plataforma}.json"
    
    if not auth_file.exists():
        print(f"❌ No se encontraron credenciales para {modelo} en {plataforma}")
        print(f"   Buscando en: {auth_file}")
        return
    
    print(f"✅ Credenciales encontradas: {auth_file}")
    print(f"🌐 Abriendo navegador con sesión de {modelo}...")
    
    # URLs por plataforma
    urls = {
        "kams": "https://kams.com",
        "xxxfollow": "https://xxxfollow.com",
    }
    
    url = urls.get(plataforma, f"https://{plataforma}.com")
    
    async with async_playwright() as p:
        # Abrir navegador con credenciales guardadas
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(storage_state=str(auth_file))
        page = await context.new_page()
        
        print(f"📱 Navegando a {url}...")
        await page.goto(url)
        
        print(f"\n✅ Navegador abierto con credenciales de {modelo}")
        print(f"   Si estás logueado automáticamente, las credenciales funcionan! 🎉")
        print(f"\n⏸️  El navegador permanecerá abierto.")
        print(f"   Cierra la ventana cuando termines de verificar.\n")
        
        # Esperar a que el usuario cierre el navegador
        try:
            await page.wait_for_timeout(600000)  # 10 minutos
        except:
            pass
        
        await browser.close()
        print("👋 Navegador cerrado")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python test_credentials.py <modelo> <plataforma>")
        print("Ejemplo: python test_credentials.py amberhudson kams")
        sys.exit(1)
    
    modelo = sys.argv[1]
    plataforma = sys.argv[2]
    
    asyncio.run(test_credentials(modelo, plataforma))
