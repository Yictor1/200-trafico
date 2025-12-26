📌 PROMPT PARA CURSOR (COPIAR / PEGAR)

Estás trabajando en un sistema llamado 100-Tráfico, un framework de automatización de tráfico para modelos webcam.

IMPORTANTE:

No hay datos críticos en producción.

Puede borrarse o ignorarse cualquier estado previo si es necesario.

Existen backups en repositorios externos, por lo que no debes optimizar para compatibilidad hacia atrás, sino para claridad y corrección.

Tu objetivo es dejar el sistema alineado con el PRD, no preservar decisiones antiguas.

Debes entrar en bucle agéntico (plan → ejecutar → validar → corregir) hasta completar la tarea sin errores lógicos ni técnicos. No te detengas ante el primer resultado: revisa, valida y ajusta.

🧠 CONTEXTO DEL SISTEMA (ESTADO ACTUAL)

Sistema híbrido:

Backend / Scheduler: Python (FastAPI, poster.py, scheduler.py)

Bot Telegram: Python

Workers: Node.js con Playwright

DB: Supabase (Postgres)

Arquitectura antigua:

Una tabla modelos

Tablas dinámicas por modelo (ej: yic, demo) que contienen videos, captions, plataformas, estado, scheduled_time

Problemas actuales:

Tablas dinámicas → no escalable

Mezcla de lenguajes

Workers acoplados a Playwright

Modelo de datos débil para análisis futuro

🎯 OBJETIVO GLOBAL (VISIÓN 2025)

Un sistema unificado, escalable y data-driven que:

Reciba contenido vía Telegram

Publique automáticamente en múltiples plataformas

Convierta publicaciones en tráfico medible a transmisiones en vivo

Genere datos temporales para futura IA predictiva

🧩 DECISIÓN ACTUAL

Vamos a empezar EXCLUSIVAMENTE con FASE 1:

FASE 1 — Crear el esquema de base de datos definitivo según el PRD

Nada más.
No migración de código aún.
No refactors de workers.
No bot nuevo todavía.

📐 PRD — MODELO DE DATOS DEFINITIVO

Debes crear el esquema SQL exacto para Supabase/Postgres con estas tablas:

modelos

id (uuid, PK)

nombre (text, unique)

estado (enum: activa, pausada, en_prueba) → migrar todos como activa

configuracion_distribucion (jsonb)

created_at

updated_at

plataformas

id

nombre (unique) — ej: kams, xxxfollow

capacidades (jsonb)

configuracion_tecnica (jsonb)

activa (boolean)

created_at

updated_at

cuentas_plataforma

id

modelo_id (FK → modelos)

plataforma_id (FK → plataformas)

username_en_plataforma

enlace_perfil

enlace_stream

enlace_tracking

sesion_guardada (boolean)

ultima_autenticacion

datos_auth (jsonb) → aquí se guardan cookies / storageState de Playwright

unique(modelo_id, plataforma_id)

created_at

updated_at

contenidos

id

modelo_id (FK)

archivo_path

enviado_por

recibido_at

contexto_original

caption_generado

tags_generados (text[])

estado (nuevo, aprobado, rechazado, reutilizable)
→ migrar legacy como aprobado

approved_at

approved_by

contenido_origen_id (FK → contenidos, nullable)

created_at

updated_at

publicaciones

id

contenido_id (FK)

cuenta_plataforma_id (FK)

scheduled_time

published_at

caption_usado

tags_usados (text[])

url_publicacion

estado (programada, procesando, publicado, fallido)

intentos

ultimo_error

created_at

updated_at

eventos_sistema

id

tipo

modelo_id (FK, nullable)

publicacion_id (FK, nullable)

descripcion

realizado_por

timestamp

Incluye:

índices mínimos (estado, scheduled_time, FKs)

updated_at automático si lo consideras correcto

🧪 ALCANCE DE LA TAREA (MUY IMPORTANTE)

Tu trabajo termina cuando:

Produces:

Script SQL completo y ordenado

Compatible con Supabase/Postgres

Validas:

Relaciones correctas

Inserciones de prueba posibles

Queries típicas del scheduler funcionarían

Documentas:

Decisiones clave

Supuestos

Qué queda listo para FASE 2

Devuelves:

Un plan claro y aprobado para continuar

Qué se haría en FASE 2 (sin implementarlo)

🔁 MODO DE TRABAJO (AGÉNTICO)

Debes:

Pensar antes de escribir SQL

Revisar el SQL como si fueras a mantenerlo 1 año

Corregirte si detectas inconsistencias

No asumir cosas no explícitas

No hacer preguntas al usuario salvo que sea absolutamente bloqueante

Trabaja como arquitecto senior, no como generador de snippets.

📦 OUTPUT ESPERADO

Devuélveme, en este orden:

Resumen corto de entendimiento (5–6 líneas)

Script SQL completo

Checklist de validación

Plan propuesto para FASE 2 (solo plan, no código)

Empieza ahora.
No pares hasta tenerlo bien.
Entra en bucle agéntico hasta estar satisfecho.