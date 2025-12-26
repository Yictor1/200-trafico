import sys, os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[2]
VENV_PYTHON = BASE_DIR / ".venv" / "bin" / "python3"
if VENV_PYTHON.exists() and not sys.executable.startswith(str(BASE_DIR / ".venv")):
    print(f"⚠️  Ejecuta siempre en el entorno virtual:\n    source {BASE_DIR}/.venv/bin/activate\n")
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), __file__] + sys.argv[1:])

import os, json, pathlib, logging
from datetime import datetime
import secrets
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# NOTA: Imports legacy eliminados (FASE 5 ETAPA 2)
# - scheduler.plan → Eliminado (scheduler.py eliminado)
# - caption.generate_and_update → No se usa (deprecated)
# Este bot usa contenidos_prd.create_contenido() directamente (esquema PRD)
# Ver: Migracion/FASE4A_COMPLETADA.md, FASE5_ETAPA2_COMPLETADA.md

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
NOMBRE_POR_USER_ID = {} # opcional: puedes mapear ids a nombres

# Configuración de modelos (carpeta en BASE_DIR)
MODELOS_DIR = BASE_DIR / "modelos"
MODELOS_DIR.mkdir(parents=True, exist_ok=True)

# Mapeo de telegram_user_id -> nombre_normalizado del modelo
TELEGRAM_USER_ID_TO_MODEL = {}

def load_models_mapping():
    """Carga todos los config.json y crea mapeo telegram_user_id -> nombre_normalizado"""
    global TELEGRAM_USER_ID_TO_MODEL
    TELEGRAM_USER_ID_TO_MODEL = {}
    
    if not MODELOS_DIR.exists():
        print(f"⚠️  Directorio de modelos no existe: {MODELOS_DIR}")
        return
    
    print(f"🔍 Cargando mapeo de modelos desde {MODELOS_DIR}...")
    modelos_encontrados = 0
    
    for modelo_dir in MODELOS_DIR.iterdir():
        if not modelo_dir.is_dir():
            continue
        
        config_path = modelo_dir / "config.json"
        if not config_path.exists():
            continue
        
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            telegram_user_id = config.get("telegram_user_id", "").strip()
            nombre_normalizado = modelo_dir.name
            
            if telegram_user_id:
                # Guardar mapeo usando user_id como string (para comparación fácil)
                TELEGRAM_USER_ID_TO_MODEL[telegram_user_id] = nombre_normalizado
                # También guardar como int por si acaso
                try:
                    TELEGRAM_USER_ID_TO_MODEL[int(telegram_user_id)] = nombre_normalizado
                except ValueError:
                    pass
                
                modelos_encontrados += 1
                print(f"  ✅ User ID {telegram_user_id} -> {nombre_normalizado}")
        except Exception as e:
            print(f"  ⚠️  Error cargando {config_path}: {e}")
            continue
    
    print(f"✅ Mapeo cargado: {modelos_encontrados} modelos encontrados")
    if modelos_encontrados == 0:
        print("  ⚠️  No se encontraron modelos con telegram_user_id configurado")

def get_modelo_by_telegram_user(user) -> str:
    """
    Busca el nombre normalizado del modelo basado en el usuario de Telegram.
    
    Intenta:
    1. Buscar por user.id (comparando con telegram_user_id en config.json)
    2. Buscar por user.id en NOMBRE_POR_USER_ID (fallback manual)
    3. Usar user.first_name normalizado (último recurso)
    
    Returns:
        str: nombre normalizado del modelo
    """
    # Buscar por user.id (método principal)
    user_id_str = str(user.id)
    user_id_int = user.id
    
    modelo = TELEGRAM_USER_ID_TO_MODEL.get(user_id_str) or \
             TELEGRAM_USER_ID_TO_MODEL.get(user_id_int)
    
    if modelo:
        return modelo
    
    # Fallback: buscar por user.id en mapeo manual
    if user.id in NOMBRE_POR_USER_ID:
        return NOMBRE_POR_USER_ID[user.id]
    
    # Último recurso: usar first_name normalizado
    nombre_fallback = (user.first_name or "modelo").lower().replace(" ", "_")
    return nombre_fallback

# Cargar mapeo al iniciar
load_models_mapping()

# Opciones disponibles para botones interactivos
QUE_VENDES_OPCIONES = [
    ("tetas", "🍑 Tetas"),
    ("culo", "🍑 Culo"),
    ("pies", "👣 Pies"),
    ("cara", "😍 Cara"),
    ("vagina", "🌸 Vagina"),
    ("cuerpo completo", "👤 Cuerpo completo"),
]

OUTFIT_OPCIONES = [
    ("lenceria", "👙 Lencería"),
    ("tanga", "🩲 Tanga"),
    ("topless", "👔 Topless"),
    ("tacones", "👠 Tacones"),
    ("tenis", "👟 Tenis"),
    ("falda", "👗 Falda"),
    ("desnuda", "✨ Desnuda"),
]

def build_que_vendes_keyboard(seleccionados: list) -> InlineKeyboardMarkup:
    """Construye teclado para seleccionar qué vendes (múltiple selección)"""
    botones = []
    for valor, etiqueta in QUE_VENDES_OPCIONES:
        check = "✅" if valor in seleccionados else "⬜"
        botones.append([InlineKeyboardButton(
            f"{check} {etiqueta}",
            callback_data=f"qv_toggle_{valor}"
        )])
    botones.append([InlineKeyboardButton("➡️ Continuar a Outfit", callback_data="qv_done")])
    return InlineKeyboardMarkup(botones)

def build_outfit_keyboard(seleccionados: list) -> InlineKeyboardMarkup:
    """Construye teclado para seleccionar outfit (múltiple selección)"""
    botones = []
    for valor, etiqueta in OUTFIT_OPCIONES:
        check = "✅" if valor in seleccionados else "⬜"
        botones.append([InlineKeyboardButton(
            f"{check} {etiqueta}",
            callback_data=f"outfit_toggle_{valor}"
        )])
    botones.append([InlineKeyboardButton("✅ Procesar Video", callback_data="process_video")])
    return InlineKeyboardMarkup(botones)

async def start(update: Update, context):
    user = update.effective_user
    modelo = get_modelo_by_telegram_user(user)
    
    # Verificar si el modelo existe
    modelo_dir = MODELOS_DIR / modelo
    modelo_existe = modelo_dir.exists()
    
    mensaje = f"¡Hola {user.first_name}! ✨\n"
    mensaje += "Este es tu chat privado y 100% seguro con el bot central.\n\n"
    
    if modelo_existe:
        mensaje += f"✅ **Modelo identificado:** `{modelo}`\n"
        mensaje += f"📱 User ID: {user.id}\n"
    else:
        mensaje += f"⚠️ **Advertencia:** No se encontró modelo configurado\n"
        mensaje += f"📱 User ID: {user.id}\n"
        mensaje += f"📁 Se usará: `{modelo}`\n\n"
        mensaje += f"💡 **Importante:** Asegúrate de crear el modelo desde el panel admin con tu Telegram User ID ({user.id}) para que los videos se guarden en la carpeta correcta.\n"
    
    mensaje += "\nEnvíame el vídeo cuando quieras (hasta 4 GB) y luego dime qué vendes + outfit."
    
    await update.message.reply_text(
        mensaje,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📹 Enviar vídeo nuevo", callback_data="nuevo")]]),
        parse_mode="Markdown"
    )

async def reload_models(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando para recargar el mapeo de modelos (solo admin)"""
    user = update.effective_user
    if str(user.id) != ADMIN_ID:
        await update.message.reply_text("❌ Solo el administrador puede usar este comando.")
        return
    
    load_models_mapping()
    total = len(set(TELEGRAM_USER_ID_TO_MODEL.values()))  # Contar modelos únicos
    await update.message.reply_text(
        f"✅ **Mapeo recargado**\n\n"
        f"📊 Modelos encontrados: {total}\n"
        f"💡 El bot ahora reconoce todos los modelos actualizados.",
        parse_mode="Markdown"
    )

async def video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    modelo = get_modelo_by_telegram_user(user)
    
    # Verificar si el modelo existe y mostrar advertencia si no
    modelo_dir = MODELOS_DIR / modelo
    modelo_existe = modelo_dir.exists()
    
    if not modelo_existe:
        # Recargar mapeo por si se creó un modelo nuevo
        load_models_mapping()
        modelo = get_modelo_by_telegram_user(user)
        modelo_dir = MODELOS_DIR / modelo
        modelo_existe = modelo_dir.exists()
        
        if not modelo_existe:
            warning_msg = (
                f"⚠️ **Advertencia:** No se encontró modelo configurado para tu usuario.\n"
                f"User ID: {user.id}\n"
                f"Se usará: `{modelo}`\n\n"
                f"💡 Asegúrate de crear el modelo desde el panel admin con tu Telegram User ID ({user.id})."
            )
            await update.message.reply_text(warning_msg, parse_mode="Markdown")
    
    file = update.message.video or update.message.document
    await update.message.reply_text("Descargando vídeo grande…")
    
    # Ruta absoluta dentro de Trafico/modelos/
    modelo_dir.mkdir(parents=True, exist_ok=True)
    
    # Generar nombre único: timestamp + random (ej: 20251118_190015_a3f2b1.mp4)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_suffix = secrets.token_hex(3)  # 6 caracteres hexadecimales
    video_nombre = f"{timestamp}_{random_suffix}.mp4"
    ruta = str(modelo_dir / video_nombre)
    
    telegram_file = await file.get_file()
    logger.info(f"🔍 DEBUG: file_path={telegram_file.file_path}")
    logger.info(f"🔍 DEBUG: file_size={telegram_file.file_size}")
    
    file_path = telegram_file.file_path
    
    # Con local_mode=True, el servidor devuelve rutas del contenedor Docker
    # Necesitamos mapear las rutas y copiar el archivo
    if "/var/lib/telegram-bot-api/" in file_path:
        # Extraer solo la parte de la ruta (eliminar prefijo de URL si existe)
        import shutil
        if "//var/lib/telegram-bot-api/" in file_path:
            # Caso: https://api.telegram.org/file/bot...//var/lib/telegram-bot-api/...
            local_container_path = "/var/lib/telegram-bot-api/" + file_path.split("//var/lib/telegram-bot-api/")[1]
        else:
            # Caso: /var/lib/telegram-bot-api/...
            local_container_path = file_path
        
        # Mapear del contenedor al host
        home_dir = os.path.expanduser("~")
        local_path = local_container_path.replace("/var/lib/telegram-bot-api", f"{home_dir}/.telegram-bot-api")
        
        logger.info(f"📥 Copiando desde: {local_path}")
        
        try:
            # Copiar directamente (permisos 777 ya configurados)
            shutil.copy2(local_path, ruta)
            logger.info(f"✅ Archivo copiado exitosamente: {os.path.getsize(ruta)} bytes")
        except PermissionError as e:
            logger.warning(f"⚠️ Error de permisos detectado, aplicando fix automático...")
            # Fix automático: cambiar permisos del archivo específico
            # Usa sudoers configurado en /etc/sudoers.d/100trafico (sin contraseña)
            import subprocess
            try:
                subprocess.run(
                    ['sudo', 'chmod', '777', local_path],
                    check=True,
                    capture_output=True,
                    timeout=5
                )
                # Intentar copiar nuevamente
                shutil.copy2(local_path, ruta)
                logger.info(f"✅ Archivo copiado exitosamente después de fix: {os.path.getsize(ruta)} bytes")
            except subprocess.TimeoutExpired:
                logger.error(f"❌ Timeout al ejecutar chmod (¿sudoers configurado?)")
                logger.error(f"   Verifica: sudo visudo -c")
                raise
            except subprocess.CalledProcessError as e2:
                logger.error(f"❌ Error al aplicar permisos: {e2}")
                logger.error(f"   Salida: {e2.stderr.decode() if e2.stderr else 'N/A'}")
                logger.error(f"   Verifica configuración en /etc/sudoers.d/100trafico")
                raise
            except Exception as e2:
                logger.error(f"❌ Error inesperado: {e2}")
                raise
        except Exception as e:
            logger.error(f"❌ Error al copiar: {e}")
            raise
    else:
        # Fallback: descarga HTTP normal
        logger.info(f"📥 Descargando vía HTTP...")
        await telegram_file.download_to_drive(ruta)
        logger.info(f"✅ Archivo descargado: {os.path.getsize(ruta)} bytes")
    context.user_data["video_ruta"] = ruta
    context.user_data["modelo"] = modelo
    context.user_data["que_vendes"] = []  # Inicializar selección
    context.user_data["outfit"] = []  # Inicializar selección
    context.user_data["step"] = "que_vendes"  # Paso actual
    
    await update.message.reply_text(
        "¡Vídeo recibido! ✅\n\n"
        "Ahora selecciona **qué vendes** (puedes elegir varios):",
        reply_markup=build_que_vendes_keyboard([]),
        parse_mode="Markdown"
    )

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja todos los callbacks de los botones interactivos"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_data = context.user_data
    
    # Botón "Enviar vídeo nuevo"
    if data == "nuevo":
        await query.edit_message_text("¡Genial! Mándame el vídeo ahora 😈")
        user_data["esperando"] = True
        return
    
    # Verificar que hay video pendiente
    if not user_data.get("video_ruta"):
        await query.edit_message_text("❌ Error: No hay video pendiente.")
        return
    
    # Toggle de qué vendes
    if data.startswith("qv_toggle_"):
        valor = data.replace("qv_toggle_", "")
        seleccionados = user_data.get("que_vendes", [])
        if valor in seleccionados:
            seleccionados.remove(valor)
        else:
            seleccionados.append(valor)
        user_data["que_vendes"] = seleccionados
        
        await query.edit_message_text(
            f"**Qué vendes** (seleccionados: {len(seleccionados)})\n\n"
            "Toca los botones para seleccionar/deseleccionar:",
            reply_markup=build_que_vendes_keyboard(seleccionados),
            parse_mode="Markdown"
        )
    
    # Continuar a outfit
    elif data == "qv_done":
        if not user_data.get("que_vendes"):
            await query.answer("⚠️ Selecciona al menos una opción", show_alert=True)
            return
        
        user_data["step"] = "outfit"
        await query.edit_message_text(
            f"✅ **Qué vendes seleccionado:** {', '.join(user_data['que_vendes'])}\n\n"
            "Ahora selecciona **outfit** (puedes elegir varios):",
            reply_markup=build_outfit_keyboard([]),
            parse_mode="Markdown"
        )
    
    # Toggle de outfit
    elif data.startswith("outfit_toggle_"):
        valor = data.replace("outfit_toggle_", "")
        seleccionados = user_data.get("outfit", [])
        if valor in seleccionados:
            seleccionados.remove(valor)
        else:
            seleccionados.append(valor)
        user_data["outfit"] = seleccionados
        
        await query.edit_message_text(
            f"**Outfit** (seleccionados: {len(seleccionados)})\n\n"
            "Toca los botones para seleccionar/deseleccionar:",
            reply_markup=build_outfit_keyboard(seleccionados),
            parse_mode="Markdown"
        )
    
    # Procesar video
    elif data == "process_video":
        if not user_data.get("outfit"):
            await query.answer("⚠️ Selecciona al menos un outfit", show_alert=True)
            return
        
        await query.edit_message_text("⏳ Procesando video...")
        
        # Procesar igual que antes
        modelo = user_data["modelo"]
        video_ruta = user_data["video_ruta"]
        video_nombre = pathlib.Path(video_ruta).name
        meta_path = video_ruta.replace(".mp4", ".json")
        
        que_vendes = user_data.get("que_vendes", [])
        outfit = user_data.get("outfit", [])
        
        # Guardar metadata
        metadata = {
            "que_vendes": que_vendes,
            "outfit": outfit,
            "video_filename": video_nombre
        }
        json.dump(metadata, open(meta_path, "w"), ensure_ascii=False, indent=2)
        
        # Construir contexto original para el contenido
        contexto_original = f"Qué vendes: {', '.join(que_vendes)}\nOutfit: {', '.join(outfit)}"
        
        # Construir archivo_path relativo (ej: "modelos/{modelo}/{video}")
        archivo_path = f"modelos/{modelo}/{video_nombre}"
        
        # Obtener telegram_user_id para enviado_por
        user = update.effective_user
        enviado_por = f"telegram_{user.id}" if user else "unknown"
        
        # FASE 4A: Crear contenido en PRD (antes de generar caption)
        # Esto asegura que el contenido existe aunque falle la generación de caption
        try:
            if str(BASE_DIR / "src") not in sys.path:
                sys.path.append(str(BASE_DIR / "src"))
            from database.contenidos_prd import create_contenido, update_contenido_caption_tags
            
            contenido_id = create_contenido(
                modelo_nombre=modelo,
                archivo_path=archivo_path,
                contexto_original=contexto_original,
                enviado_por=enviado_por
            )
            
            if not contenido_id:
                logger.error(f"❌ No se pudo crear contenido para {archivo_path}")
                await query.edit_message_text(
                    f"❌ **Error:** No se pudo crear el contenido en la base de datos.\n\n"
                    f"Contacta al administrador.",
                    parse_mode="Markdown"
                )
                user_data.clear()
                return
        except Exception as e:
            logger.error(f"❌ Error creando contenido: {e}")
            import traceback
            traceback.print_exc()
            await query.edit_message_text(
                f"❌ **Error:** Error al crear contenido: {str(e)[:100]}\n\n"
                f"Contacta al administrador.",
                parse_mode="Markdown"
            )
            user_data.clear()
            return
        
        # Generar caption y tags (sin insertar en tabla dinámica)
        try:
            from caption import generate_caption_and_tags
            
            result = generate_caption_and_tags(modelo, meta_path)
            
            if result.success:
                # Actualizar contenido con caption y tags
                update_contenido_caption_tags(
                    contenido_id=contenido_id,
                    caption_generado=result.caption,
                    tags_generados=result.tags
                )
                
                # Guardar backup local (compatibilidad)
                from caption import persist_caption_result
                persist_caption_result(meta_path, result.caption, result.tags)
                
                caption_msg = "✅ Caption y tags generados"
            else:
                caption_msg = f"⚠️ Caption: {result.error[:50]}"
                logger.warning(f"Error generando caption: {result.error}")
        except Exception as e:
            caption_msg = f"⚠️ Error generando caption: {str(e)[:50]}"
            logger.error(f"Error en generación de caption: {e}")
            import traceback
            traceback.print_exc()
        
        # FASE 4A: NO crear publicaciones ni llamar a scheduler
        # Eso se hará en FASE 4B
        
        await query.edit_message_text(
            f"✅ **¡Contenido creado!**\n\n"
            f"📝 Qué vendes: {', '.join(que_vendes)}\n"
            f"👗 Outfit: {', '.join(outfit)}\n"
            f"📄 {caption_msg}\n\n"
            f"💡 El contenido está listo. Las publicaciones se programarán después.\n\n"
            "¿Otro vídeo?",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Sí, otro", callback_data="nuevo")]]),
            parse_mode="Markdown"
        )
        user_data.clear()

# Configurar URL del API para usar servidor local (soporte archivos >50MB)
# El servidor local debe estar corriendo en puerto 8081
# NOTA: local_mode=True NO es necesario (obsoleto según docs/TELEGRAM_ARCHIVOS_GRANDES.md)
# El bot hace peticiones HTTP normales al servidor local, evitando problemas de permisos
TELEGRAM_BASE_URL = "http://127.0.0.1:8081/bot"

# Crear HTTPXRequest con timeouts más largos para archivos grandes
from telegram.request import HTTPXRequest
request = HTTPXRequest(
    connection_pool_size=8,
    connect_timeout=30.0,
    read_timeout=120.0,  # 2 minutos para archivos muy grandes
    write_timeout=120.0,
    pool_timeout=30.0
)

app = (
    Application.builder()
    .token(TOKEN)
    .base_url(TELEGRAM_BASE_URL)
    .local_mode(True)  # ✅ NECESARIO cuando el servidor usa --local
    .request(request)
    .build()
)
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("reload", reload_models))  # Comando para recargar modelos
app.add_handler(CallbackQueryHandler(callback_handler))  # Maneja todos los botones
app.add_handler(MessageHandler(filters.VIDEO | filters.Document.ALL, video_handler))
# Ya no necesitamos texto_handler, todo es con botones
print("BOT CENTRAL corriendo – recibe de todas las modelos al mismo tiempo")
total_modelos = len(set(TELEGRAM_USER_ID_TO_MODEL.values()))  # Contar modelos únicos
print(f"📊 Modelos mapeados: {total_modelos} modelos")
if total_modelos > 0:
    print("💡 Usa /reload para recargar el mapeo después de crear un modelo nuevo")
app.run_polling()
