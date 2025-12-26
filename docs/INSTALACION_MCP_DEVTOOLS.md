# 🔧 Instalación del MCP de Chrome DevTools

## ⚠️ Requisito Previo

El servidor MCP de Chrome DevTools requiere **Node.js 20.19.0 LTS o superior**.

Tu versión actual: `v18.19.1` ❌

## 📦 Opción 1: Actualizar Node.js (Recomendado)

### Usando NVM (Node Version Manager)

```bash
# Instalar NVM si no lo tienes
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Recargar shell
source ~/.bashrc

# Instalar Node 20 LTS
nvm install 20
nvm use 20
nvm alias default 20

# Verificar
node --version  # Debe mostrar v20.x.x
```

### Usando el instalador oficial

```bash
# Descargar e instalar Node 20 LTS desde nodejs.org
# O usar el gestor de paquetes de tu distribución
```

## 🚀 Instalación del MCP de DevTools

### 1. Instalar el paquete

```bash
# Verificar que Node >= 20
node --version

# Instalar chrome-devtools-mcp
npm install -g chrome-devtools-mcp
```

### 2. Configurar en Cursor

En Cursor, los servidores MCP se configuran a través de la interfaz de usuario:

1. Abre Cursor
2. Ve a **Settings** (Ctrl+,)
3. Busca "MCP" o "Model Context Protocol"
4. Agrega un nuevo servidor MCP con:
   - **Name**: `chrome-devtools`
   - **Command**: `npx`
   - **Args**: `["-y", "chrome-devtools-mcp"]`

O edita manualmente el archivo de configuración (si existe):
`~/.config/Cursor/User/settings.json`

```json
{
  "mcp.servers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp"]
    }
  }
}
```

### 3. Verificar instalación

Después de configurar, reinicia Cursor y verifica que el servidor MCP esté disponible.

## 🔍 Alternativa: Usar versión local

Si no puedes actualizar Node globalmente:

```bash
# En el proyecto
cd /home/victor/100-trafico
npm install chrome-devtools-mcp --save-dev

# Configurar en Cursor con ruta local
# Command: node
# Args: ["node_modules/.bin/chrome-devtools-mcp"]
```

## 📚 Recursos

- [Chrome DevTools MCP GitHub](https://github.com/benjaminr/chrome-devtools-mcp)
- [MCP Servers Directory](https://product.makr.io/mcp-servers/chrome-devtools)

## ✅ Verificación

Una vez instalado, deberías poder usar comandos como:
- Inspeccionar elementos del navegador
- Capturar screenshots
- Navegar páginas
- Ejecutar JavaScript en el contexto del navegador




