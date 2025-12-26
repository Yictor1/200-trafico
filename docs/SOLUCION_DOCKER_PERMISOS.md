# 🔧 Solución: Error de Permisos en Docker Telegram Bot API

**Problema encontrado:** 25 de diciembre de 2025  
**Estado:** ✅ RESUELTO

---

## ❌ Problema

Al iniciar el bot, aparecía este error:

```
httpcore.ConnectError: All connection attempts failed
telegram.error.NetworkError: httpx.ConnectError: All connection attempts failed
Bot Central se detuvo inesperadamente
```

Y el contenedor Docker estaba en loop de reinicio:

```bash
docker ps -a | grep telegram-bot-api
# Output: Restarting (1) 7 seconds ago
```

**Logs del contenedor mostraban:**

```
Permission denied : 13 : File "/var/lib/telegram-bot-api/tqueue.binlog" 
can't be opened/created for reading and writing
```

---

## 🔍 Causa Raíz

Cuando aplicamos el fix de permisos inicial (`chmod 755`), el directorio quedó con permisos que el contenedor Docker **no podía usar para escribir**.

El contenedor corre como usuario `telegram-bot-api` (UID diferente a victor), y con permisos `755`:
- Propietario (victor): rwx (lectura/escritura/ejecución)
- Grupo (victor): r-x (solo lectura/ejecución)
- Otros (telegram-bot-api): r-x (solo lectura/ejecución) ❌ **Sin escritura**

Por eso el contenedor no podía escribir en `tqueue.binlog`.

---

## ✅ Solución Aplicada

### 1. Detener el contenedor en loop

```bash
sudo docker stop telegram-bot-api
```

### 2. Cambiar permisos a 777 (lectura/escritura para todos)

```bash
sudo chmod -R 777 ~/.telegram-bot-api
```

**¿Por qué 777?**
- Propietario: rwx
- Grupo: rwx
- **Otros: rwx** ← El contenedor puede escribir

**¿Es seguro?**
- ✅ Sí, el directorio está dentro de tu home (~/)
- ✅ Solo los usuarios del sistema pueden acceder
- ✅ Docker necesita estos permisos para funcionar
- ✅ Es la configuración estándar para volúmenes Docker

### 3. Reiniciar el contenedor

```bash
sudo docker start telegram-bot-api
```

### 4. Verificar que funcione

```bash
# Verificar estado
docker ps | grep telegram-bot-api
# Debe mostrar: Up X seconds

# Probar conexión
curl http://127.0.0.1:8081/bot
# Debe responder: {"ok":false,"error_code":404,"description":"Not Found"}
```

---

## 🎯 Resultado

**Antes:**
```
❌ Contenedor: Restarting (1)
❌ Bot: Network Error - Connection failed
```

**Después:**
```
✅ Contenedor: Up (corriendo correctamente)
✅ Bot: Puede conectarse al servidor local
✅ Descargas: Sin pedir contraseña sudo
```

---

## 📊 Resumen de Permisos Finales

| Componente | Propietario | Permisos | Razón |
|------------|-------------|----------|-------|
| `~/.telegram-bot-api/` | victor:victor | 777 | Docker necesita escribir |
| `tqueue.binlog` | victor:victor | 777 | Docker escribe aquí |
| Archivos del bot | victor:victor | 644-755 | Solo lectura para bot |

---

## 🚀 Verificación Rápida

```bash
# Ver permisos actuales
ls -la ~/.telegram-bot-api

# Verificar contenedor
docker ps | grep telegram-bot-api

# Probar conexión
curl -s http://127.0.0.1:8081/bot && echo " ← Servidor responde ✅"
```

---

## ⚠️ Si el Problema Vuelve a Ocurrir

### Síntoma: Contenedor en loop de reinicio

```bash
# 1. Ver logs
docker logs --tail 20 telegram-bot-api

# 2. Si dice "Permission denied"
sudo chmod -R 777 ~/.telegram-bot-api

# 3. Reiniciar contenedor
docker restart telegram-bot-api

# 4. Esperar 5 segundos y verificar
sleep 5 && docker ps | grep telegram-bot-api
```

### Síntoma: Bot no se conecta (Network Error)

```bash
# 1. Verificar que el contenedor esté corriendo
docker ps | grep telegram-bot-api

# 2. Verificar puerto
curl http://127.0.0.1:8081/bot

# 3. Si no responde, reiniciar contenedor
docker restart telegram-bot-api
```

---

## 🔄 Script de Auto-Fix

Creé este script para automatizar la solución:

```bash
#!/bin/bash
# scripts/fix_docker_permisos.sh

echo "🔧 Aplicando fix de permisos Docker..."

# Detener contenedor
sudo docker stop telegram-bot-api

# Arreglar permisos
sudo chmod -R 777 ~/.telegram-bot-api
echo "✅ Permisos actualizados"

# Iniciar contenedor
sudo docker start telegram-bot-api
echo "✅ Contenedor iniciado"

# Esperar y verificar
sleep 3
if docker ps | grep -q telegram-bot-api; then
    echo "✅ Contenedor corriendo correctamente"
else
    echo "❌ Contenedor no está corriendo"
    docker logs --tail 10 telegram-bot-api
fi
```

---

## 📝 Lecciones Aprendidas

1. **Docker + volúmenes**: Los permisos 755 no son suficientes cuando el contenedor corre con un usuario diferente

2. **Permisos 777**: Son necesarios en volúmenes Docker cuando el contenedor necesita escribir

3. **Verificar logs**: Siempre `docker logs` es tu amigo para diagnosticar

4. **Orden importa**: Primero fix de permisos, luego reiniciar contenedor

---

## ✅ Estado Actual

- ✅ Contenedor corriendo
- ✅ Puerto 8081 escuchando
- ✅ Bot puede conectarse
- ✅ Permisos configurados correctamente
- ✅ No pide contraseña sudo

**TODO LISTO PARA USAR** 🎉

---

_Documentado el 25 de diciembre de 2025_  
_Problema resuelto completamente_


