# 📋 LISTA DE VERIFICACIÓN - PUESTA EN MARCHA DEL SISTEMA

## 🔧 CONFIGURACIÓN DEL ENTORNO

### ✅ Entorno Virtual y Dependencias
- [ ] Crear entorno virtual: `python3 -m venv venv`
- [ ] Activar entorno virtual: `source venv/bin/activate`
- [ ] Instalar dependencias: `pip install -r requirements.txt`

### ✅ Variables de Entorno
- [ ] Crear archivo `.env` basado en `config_env_example.txt`
- [ ] Configurar `OPENAI_API_KEY`
- [ ] Configurar `PINECONE_API_KEY`
- [ ] Configurar `PINECONE_ENVIRONMENT`
- [ ] Configurar `PINECONE_INDEX_NAME`

---

## 🔐 CONFIGURACIÓN DE DROPBOX

### ✅ App de Dropbox
- [ ] Verificar app en Dropbox App Console
- [ ] Confirmar permisos de Team habilitados
- [ ] Verificar permisos: `files.metadata.read`, `files.content.read`, `team_data.member`

### ✅ Tokens de Dropbox
- [ ] **Para carpetas personales:**
  - [ ] Generar token de usuario personal
  - [ ] Configurar `DROPBOX_ACCESS_TOKEN`
  - [ ] Configurar `DROPBOX_TEAM_MODE=0`

- [ ] **Para carpetas colaborativas:**
  - [ ] Generar token de equipo
  - [ ] Configurar `DROPBOX_APP_KEY`, `DROPBOX_APP_SECRET`, `DROPBOX_REFRESH_TOKEN`
  - [ ] Configurar `DROPBOX_TEAM_MODE=1`, `DROPBOX_USER_EMAIL`

### ✅ Configuración de Carpetas
- [ ] Verificar ruta en `auto_updater.py` línea 35
- [ ] Confirmar que la carpeta existe y es accesible

---

## 🌲 CONFIGURACIÓN DE PINECONE

### ✅ Cuenta y API
- [ ] Verificar cuenta activa
- [ ] Confirmar API key válido
- [ ] Verificar environment correcto

### ✅ Índice
- [ ] Confirmar que el índice existe
- [ ] Verificar que está activo
- [ ] Confirmar dimensiones compatibles

---

## 🤖 CONFIGURACIÓN DE SLACK

### ✅ App de Slack
- [ ] Crear app en Slack API
- [ ] Configurar permisos del bot
- [ ] Configurar `SLACK_BOT_TOKEN` y `SLACK_APP_TOKEN`

### ✅ Instalación del Bot
- [ ] Instalar app en workspace
- [ ] Invitar bot a canales necesarios

---

## 🧪 PRUEBAS DE CONECTIVIDAD

### ✅ Dropbox
- [ ] Ejecutar: `python test_dropbox.py`

### ✅ Pinecone
- [ ] Ejecutar: `python test_pinecone.py`

### ✅ OpenAI
- [ ] Ejecutar: `python test_openai.py`

### ✅ Slack Bot
- [ ] Ejecutar: `python slack_bot.py`

---

## 🔄 SISTEMA DE ACTUALIZACIÓN AUTOMÁTICA

### ✅ Configuración de Cron
- [ ] Ejecutar: `./setup_cron.sh`
- [ ] Verificar: `crontab -l`

### ✅ Pruebas del Sistema
- [ ] Ejecutar: `python auto_updater.py`
- [ ] Verificar logs en `auto_updater.log`

---

## 📊 MONITOREO Y LOGS

### ✅ Archivos de Log
- [ ] Verificar: `auto_updater.log`, `slack_bot.log`, `dropbox_auth.log`

---

## 🚀 PRUEBAS FINALES

### ✅ Flujo Completo
- [ ] Subir documento de prueba a Dropbox
- [ ] Ejecutar procesamiento automático
- [ ] Verificar documento en Pinecone
- [ ] Hacer consulta en Slack
- [ ] Verificar respuesta del bot

---

## 🔒 SEGURIDAD

### ✅ Protección de Credenciales
- [ ] Verificar `.env` en `.gitignore`
- [ ] Confirmar no hay credenciales hardcodeadas

---

## ✅ VERIFICACIÓN FINAL

### Estado General del Sistema
- [ ] **Dropbox:** ✅ Conectado y funcionando
- [ ] **Pinecone:** ✅ Conectado y funcionando  
- [ ] **OpenAI:** ✅ Conectado y funcionando
- [ ] **Slack Bot:** ✅ Conectado y funcionando
- [ ] **Actualización Automática:** ✅ Configurada y funcionando 