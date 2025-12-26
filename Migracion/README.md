📌 Alignment Brief — Proyecto 100-Tráfico (para Cursor AI)

Contexto general
Estás trabajando en el proyecto 100-Tráfico, un sistema para automatizar y optimizar la distribución de contenido de modelos webcam hacia múltiples plataformas, con foco en convertir publicaciones en tráfico medible hacia transmisiones en vivo.

Este proyecto ya tiene un PRD cerrado. No estamos explorando ideas: estamos ejecutando.

🎯 Objetivo del MVP (v1.0)

Construir un sistema end-to-end funcional que:

Telegram (ingreso de video)
→ procesamiento mínimo (caption/tags opcionales)
→ publicación automática en al menos 1 plataforma
→ dashboard con estado de publicaciones (programada / procesando / publicada / fallida)

Nada más. Nada menos.

🧱 Stack técnico decidido (no proponer alternativas)

Node.js + TypeScript (unificación total).

Supabase (DB + auth simple).

Publicaciones vía HTTP puro usando Got.

Playwright solo para:

login inicial

captura de .har

Scheduler:

cron simple o BullMQ (preferir simplicidad para MVP).

Dashboard en Next.js / TS (ya existe, solo extender).

🧠 Principios de diseño

El sistema debe ser operativo antes que inteligente.

Cero IA predictiva en MVP.

Cero scrapers en MVP.

Todo lo complejo se posterga si no bloquea publicaciones reales.

Preferir código explícito y legible sobre abstracciones elegantes.

🔑 Concepto central del sistema

Workers de plataforma generados a partir de .har

Flujo clave:

Botón “Crear Plataforma”

Playwright visible → publicación manual

Captura .har

IA analiza .har

Se genera automáticamente un worker HTTP con Got

El worker queda versionado y reutilizable

Esto NO es opcional. Es el núcleo estratégico del sistema.

📦 Entidades de datos (alineadas al PRD)

modelos

plataformas

cuentas_plataforma

contenidos

publicaciones

metricas_publicacion (futuro)

eventos_sistema

No inventar nuevas tablas para el MVP.

🚫 Qué NO hacer

No introducir microservicios.

No proponer cambiar Supabase.

No agregar “optimización futura” en el código del MVP.

No diseñar UI compleja.

No crear roles adicionales.

✅ Qué sí hacer

Implementar poster.ts que:

lea publicaciones programada

ejecute workers

maneje estados y errores

Workers con contrato claro (input/output).

Dashboard que muestre la verdad operativa del sistema.

Código preparado para crecer, pero no inflado.

🧭 Fase actual

Estamos antes de la migración técnica.
El próximo paso inmediato es:

Crear el starter técnico (Sesión 1):
repo Node + TS + Supabase + scheduler + poster.ts (aunque el worker sea mock).