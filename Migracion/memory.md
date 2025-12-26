PRD: 100-Tráfico
1. Problema
Automatizar y optimizar la distribución de contenido de modelos webcam en múltiples plataformas, convirtiendo publicaciones en tráfico medible hacia transmisiones en vivo y permitiendo decisiones basadas en datos para maximizar ingresos.
2. Usuarios
Usuario Principal
Administrador del tráfico (gestor del estudio o responsable de tráfico).
Proceso actual sin la app: Recibe videos de forma desestructurada, publica manualmente en múltiples plataformas usando sesiones de navegador persistentes, y realiza seguimiento disperso y tardío de métricas básicas. Las decisiones se basan en intuición y experiencia, limitando escalabilidad y eficiencia.
Usuarios Secundarios
Modelos webcam.
Proceso actual sin la app: Producen y envían contenido sin visibilidad clara del rendimiento en plataformas externas ni feedback estructurado sobre qué funciona mejor. Dependen completamente del administrador para publicación y optimización.
(No tienen acceso directo a la app; interactúan exclusivamente vía bot de Telegram).
3. Flujo del Usuario Principal (5 pasos)
Accede al dashboard y estado general El administrador abre la app y visualiza el estado del sistema: publicaciones programadas, publicaciones recientes y alertas básicas.
Confirma contenido y programación El sistema muestra el contenido listo para publicar y su programación automática; el administrador solo valida que el flujo esté activo.
Ejecución automática de publicaciones La app publica el contenido en las plataformas configuradas de forma automática, sin intervención manual.
Monitorea rendimiento en tiempo casi real El administrador observa métricas clave (views, likes, clics, tráfico a transmisión) recolectadas periódicamente.
Ajusta distribución según resultados En base al rendimiento observado, el administrador ajusta prioridades, horarios o plataformas para optimizar tráfico e ingresos futuros.
(Opcional) Flujo del Usuario Secundario
No existe flujo directo en la app. Las modelos envían contenido exclusivamente vía bot de Telegram (vídeo + contexto opcional). El sistema procesa automáticamente y no requiere interacción adicional de las modelos en el MVP.
4. Modelo de Datos
modelos
id (PK)
nombre (string, único)
estado (enum: activa, pausada, en_prueba)
configuracion_distribucion (jsonb: reglas fijas como frecuencia máxima, plataformas permitidas, etc.)
created_at, updated_at
plataformas
id (PK)
nombre (string, único)
capacidades (jsonb)
configuracion_tecnica (jsonb)
activa (boolean)
cuentas_plataforma
id (PK)
modelo_id (FK → modelos)
plataforma_id (FK → plataformas)
username_en_plataforma (string)
enlace_perfil (url)
enlace_stream (url)
enlace_tracking (url)
sesion_guardada (boolean)
ultima_autenticacion (timestamp)
datos_auth (jsonb)
contenidos
id (PK)
modelo_id (FK → modelos)
archivo_path (string)
enviado_por (string)
recibido_at (timestamp)
contexto_original (text)
caption_generado (text)
tags_generados (array string)
estado (enum: nuevo, aprobado, rechazado, reutilizable)
approved_at (timestamp)
approved_by (string)
contenido_origen_id (FK → contenidos, nullable) → para rastrear reutilización/reposts
publicaciones
id (PK)
contenido_id (FK → contenidos)
cuenta_plataforma_id (FK → cuentas_plataforma)
scheduled_time (timestamp)
published_at (timestamp)
caption_usado (text)
tags_usados (array string)
url_publicacion (url)
estado (enum: programada, procesando, publicado, fallido)
intentos (integer)
ultimo_error (text)
metricas_publicacion (timeseries)
id (PK)
publicacion_id (FK → publicaciones)
timestamp (timestamp)
views (integer)
likes (integer)
seguidores_plataforma (integer)
clics_tracking (integer)
fuente (string)
clics_atribucion (timeseries)
id (PK)
publicacion_id (FK → publicaciones, nullable)
cuenta_plataforma_id (FK)
timestamp (timestamp)
clics_totales (integer)
clics_unicos (integer)
pais (string)
ciudad (string)
origen_referrer (string)
dispositivo (string)
transmisiones
id (PK)
modelo_id (FK → modelos)
timestamp (timestamp)
plataforma (string)
show_type (enum: public, private, offline)
viewers (integer)
rank (integer)
gender_rank (integer)
followers_start (integer)
followers_end (integer)
growth (integer)
ingresos
id (PK)
modelo_id (FK → modelos)
timestamp (timestamp)
periodo (string)
ingresos_totales (decimal)
tips_publicos (decimal)
tips_privados (decimal)
fuente (string)
eventos_sistema
id (PK)
tipo (enum: publicacion_fallida, reintento, ajuste_manual, estrategia_cambiada, etc.)
modelo_id (FK, nullable)
publicacion_id (FK, nullable)
descripcion (text)
realizado_por (string)
timestamp (timestamp)
Notas importantes
Estrategias versionadas: En el futuro, se podrá crear una entidad estrategias_distribucion para versionar reglas cambiantes por modelo y periodo.
Reutilización de contenido: El campo contenido_origen_id permite rastrear reposts y longevidad.
Agregación de métricas: Las tablas de timeseries podrán resumirse (por hora/día) en vistas o tablas materializadas para análisis de largo plazo.
5. Roles & Permisos
Administrador del tráfico (único rol en MVP): Acceso completo a todas las funcionalidades (visualización, creación/edición de modelos/plataformas/contenido, configuración, auditoría y ajustes estratégicos). (Roles adicionales como solo-lectura o colaboradores limitados se consideran para fases posteriores).
6. Panel de Administración
El sistema cuenta con un único panel interno, que es el dashboard principal utilizado por el Administrador del tráfico. Este panel centraliza tanto el monitoreo del rendimiento como las funciones administrativas.
Funciones clave:
Visualizar estado general del sistema (publicaciones programadas/en proceso/fallidas, últimas publicaciones, alertas críticas).
Ver rendimiento agregado y métricas clave por periodo, con comparación básica entre plataformas y modelos.
Gestionar modelos (crear/editar/pausar, ajustar configuración de distribución).
Gestionar contenido y publicaciones (aprobar/rechazar opcional, reprogramar, forzar reintentos).
Configurar plataformas y cuentas (crear plataformas, vincular sesiones, activar/desactivar scrapers/trackers).
Ver eventos del sistema y auditoría básica.
7. MVP (v1.0)
Incluye:
Automatización end-to-end del flujo de contenido desde Telegram hasta la publicación en plataforma(s), con visibilidad básica del estado de cada publicación (pendiente/procesando/publicado/fallido) en un dashboard simple para el Administrador del tráfico. (Incluye: ingreso vía Telegram, procesamiento mínimo, publicación automática en al menos una plataforma, dashboard con lista de publicaciones y errores básicos).
No incluye (v2.0 y posteriores):
Métricas avanzadas y monitoreo en tiempo real detallado.
Ajustes estratégicos complejos, recomendaciones IA o A/B testing.
Aprobaciones complejas de contenido.
Panel o acceso directo para modelos.
Scrapers completos, tracking avanzado (getmy.link detallado) o integración ingresos/transmisiones.
8. Branding
Nombre: 100-Tráfico
Tono: Profesional, eficiente y data-driven (minimalista, directo, enfocado en resultados operativos).
Colores: Por definir (sugerencia: tonos oscuros con acentos verdes/rojos para estados positivo/negativo, estilo dashboard moderno y limpio).

