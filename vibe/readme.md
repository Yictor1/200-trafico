📘 README — Fábrica Inteligente 100-Tráfico
Motor de desarrollo por PRDs, Router de intención y Agentes IA

Versión: 1.0
Proyecto: 100-Tráfico
Autor: Victor + IA

🎯 ¿Qué es esta fábrica?

La carpeta `vibe/` es el sistema operativo de inteligencia del proyecto 100-Tráfico.
Aquí viven tus:

Reglas del sistema

PRDs

Router de intención

Agentes especializados

Instrucciones internas

Memoria contextual

Convenciones y arquitectura

Cuando tú escribes una idea en Cursor o ChatGPT, este sistema permite:

Idea → Router → PRD → Agente → Plan → Código en Cursor


Es desarrollo asistido pero ordenado, escalable y siempre consistente.

🧠 Filosofía del sistema

No existe feature sin PRD.

No existe código sin intención explícita.

El router siempre decide qué tipo de tarea es.

Los agentes hacen el trabajo técnico y te hacen preguntas.

Cursor solo escribe código cuando todo está claro.

Nada se rompe, todo se diseña.

Esto elimina la parálisis por análisis y te lleva a un loop de construcción fluida pero sólida.

🗂️ Contenido de la carpeta `vibe/`
1. system.context.md

Define la personalidad técnica del sistema, las reglas universales y la misión del proyecto.
Es lo primero que lee la IA.

2. cursor.rules.yaml

Controla a Cursor:

qué carpetas incluir

qué carpetas ignorar

reglas al escribir código

cuándo exigir PRD

cuándo activar agentes

Sin esto, Cursor es “genérico”; con esto, Cursor es parte del equipo.

3. router.md

El cerebro.
Selecciona automáticamente:

qué PRD usar

qué agente activar

cómo empezar la conversación

Ejemplos claros:

Tú escribes	El router detecta	Activa
“quiero una métrica nueva”	KPI	kpi.md + KPI agent
“quiero un worker para Fansly”	Worker	worker.md + worker_agent
“quiero revisar por qué falla scheduler”	Auditoría	audit.md + prd_agent
“quiero una nueva vista en el panel”	UI/Admin	admin_panel.md + ui_agent
4. /prompts/prd/ — Plantillas PRD

Aquí están los PRDs completos:

feature.md

worker.md

kpi.md

scheduler.md

admin_panel.md

bot.md

refactor.md

audit.md

db_model.md

Cada uno tiene su flujo de preguntas y estructura para generar el documento final.

5. /agents/ — Agentes de ejecución

Los agentes son “IA con especialidad”, por módulo:

prd_agent.md — guía la conversación y hace preguntas

worker_agent.md — experto en Playwright

api_agent.md — experto en FastAPI

ui_agent.md — experto en Next.js

refactor_agent.md — limpia y reorganiza

db_agent.md — experto en Supabase

El router los activa automáticamente cuando detecta intención.

6. /prompts/instructions/ — Manuales internos

Son documentos normativos:

architecture.md

refactor_rules.md

troubleshooting.md

code_style.md

Definen cómo debe construirse y mantenerse el proyecto.

7. /prompts/meta/ — Memoria y Alcance

Estos documentos actúan como “conciencia” del sistema:

memory.md

project_scope.md

conventions.md

Mantienen coherencia en decisiones futuras.

🚀 ¿Cómo usar la fábrica?
⭐ PASO 1 — Escribes tu idea en ChatGPT o Cursor

Ejemplos:

“Quiero un worker que suba videos a Kams.com”

“Quiero leer métricas nuevas de FikFap”

“Quiero una tabla en el panel con los videos virales”

“Quiero optimizar el scheduler, está duplicando tareas”

“Quiero agregar un KPI que compare CTR entre plataformas”

No necesitas pensar en PRDs.
Solo expresas la intención.

⭐ PASO 2 — El router detecta la intención

Ejemplo:

→ intención detectada: worker automation
→ PRD seleccionado: worker.md
→ agente activado: worker_agent
→ primera pregunta: “¿para qué plataforma es el worker?”


Todo automático.

⭐ PASO 3 — El agente te hace preguntas

Ejemplo del worker_agent:

¿Cuál es el objetivo del worker?

¿Qué datos debe capturar?

¿Qué pasos realiza la plataforma?

¿Debemos generar endpoints en FastAPI?

Hasta que se complete el PRD.

⭐ PASO 4 — PRD final generado

Cuando respondes todo, dices:

“Genera el PRD final.”

Y obtienes:

documento estructurado

modelo de datos

flujos

dependencias

riesgos

MVP

Listo para usar.

⭐ PASO 5 — Enviar a Cursor

Pegas el PRD en Cursor y escribes:

Implementar este PRD. 
Respeta cursor.rules.yaml.


Cursor:

abre los archivos correctos

crea o modifica solo lo necesario

mantiene la arquitectura

no rompe nada

genera código limpio

🔁 Flujo completo (resumen)
idea
 ↓
router (detecta intención)
 ↓
PRD (preguntas guiadas)
 ↓
agente especializado
 ↓
PRD final
 ↓
Cursor implementa código


Ya no hay:

❌ caos
❌ improvisación
❌ código sin contexto
❌ decisiones sin arquitectura

Ahora hay:

✔ diseño
✔ claridad
✔ modularidad
✔ consistencia
✔ velocidad
✔ vibecoding con dirección

💡 Notas finales

La fábrica está pensada para evolucionar contigo.

Cada PRD termina en una funcionalidad real.

Cada agente es una extensión del equipo.

Las reglas del sistema protegen el proyecto.

Y tú mantienes el control absoluto con ideas claras.