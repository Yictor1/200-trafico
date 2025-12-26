# 🚀 Inicio Rápido - 100 Tráfico

¿Primera vez usando el sistema? Sigue estos pasos para comenzar en 5 minutos.

---

## ⚡ Instalación Express

```bash
# 1. Ir al directorio del proyecto
cd ~/Escritorio/SkyFlow_Porn-master/100-trafico

# 2. Crear y activar entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 3. Instalar dependencias Python
pip install -r requirements.txt
pip install -r admin_panel/backend/requirements.txt
playwright install chromium

# 4. Instalar dependencias Node.js
npm install
cd admin_panel/frontend && npm install && cd ../..

# 5. Configurar variables de entorno
cp src/.env.example src/.env
nano src/.env  # Edita con tus credenciales
```

---

## 🔑 Configuración Mínima

Edita `src/.env` y completa **solo esto**:

```bash
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=tu_clave_aqui
GEMINI_API_KEY=tu_api_key_aqui
```

---

## 🎬 Iniciar el Sistema

### Opción A: Usando Scripts (Recomendado)

```bash
# Terminal 1: Backend
./scripts/start_backend.sh

# Terminal 2: Frontend
./scripts/start_frontend.sh
```

### Opción B: Manual

```bash
# Terminal 1: Backend
cd admin_panel/backend
source ../../.venv/bin/activate
python -m uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd admin_panel/frontend
npm run dev
```

---

## 📱 Acceder al Panel

1. Abre tu navegador
2. Ve a: **http://localhost:3000**
3. ¡Listo! 🎉

---

## ✅ Primeros Pasos

### 1. Crear tu Primera Modelo

1. Haz clic en **"+ Crear Modelo"**
2. Completa el formulario (mínimo: nombre y foto)
3. Haz clic en **"Crear Modelo"**

### 2. Guardar Sesiones de Plataformas

1. En la tarjeta de la modelo, haz clic en **"🌐 Abrir Navegador"**
2. Inicia sesión en tus plataformas (OnlyFans, Fansly, etc.)
3. Cierra el navegador
4. ✅ ¡Sesiones guardadas automáticamente!

### 3. Verificar que Funciona

1. Vuelve a hacer clic en **"🌐 Abrir Navegador"**
2. Deberías estar automáticamente logueado
3. 🎉 ¡Funciona!

---

## 🆘 Problemas Comunes

### Backend no inicia

```bash
# Ver si hay algo en el puerto 8000
lsof -i :8000

# Matar el proceso si existe
kill -9 [PID]

# Reintentar
./scripts/start_backend.sh
```

### Frontend no carga datos

```bash
# Verifica que el backend esté corriendo
curl http://localhost:8000/api/models

# Debería devolver: []
# Si da error de conexión, reinicia el backend
```

### No encuentra Playwright

```bash
source .venv/bin/activate
playwright install chromium
```

---

## 📚 Siguiente Paso

Lee el **[Manual de Instalación Completo](INSTALACION.md)** para:
- Configuración avanzada
- Solución de problemas detallada
- Documentación completa de funcionalidades

---

**¿Listo?** ¡Tu sistema está funcionando! 🚀

Usa `./scripts/start_backend.sh` y `./scripts/start_frontend.sh` cada vez que quieras usar el sistema.





