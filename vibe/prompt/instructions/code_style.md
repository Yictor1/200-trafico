# ✨ Estilo de Código Unificado — 100-Tráfico

## Python
- snake_case para variables y funciones
- PascalCase para clases
- Cada archivo con docstring inicial
- Tipado opcional pero recomendado
- Evitar funciones > 40 líneas

## JavaScript / TypeScript
- camelCase para todo
- Interfaces en `types/`
- Services definidos en `/services/`
- Hooks en `/hooks/`
- Componentes puros, sin side-effects

## Workers (JS)
- No usar var, siempre let/const
- async/await obligatorio
- Logs descriptivos, no genéricos
- Evitar sleeps largos sin necesidad

## Comunes
- Nombres descriptivos
- Arquitectura limpia
- Uso mínimo de magia
