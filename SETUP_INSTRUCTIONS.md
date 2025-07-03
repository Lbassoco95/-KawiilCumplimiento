
# 🚀 Configuración del Sistema de Cumplimiento Regulatorio

## Variables Requeridas

### Dropbox
1. Ve a https://www.dropbox.com/developers/apps
2. Selecciona tu aplicación
3. En "OAuth 2":
   - OAuth 2 type: Full Dropbox
   - Permissions: files.metadata.read, files.content.read, team_data.member
   - App permissions: Team member file access
4. Copia App key y App secret

### Pinecone
1. Ve a https://app.pinecone.io/
2. Obtén tu API Key
3. Anota el nombre de tu índice

### OpenAI
1. Ve a https://platform.openai.com/api-keys
2. Genera una nueva API Key

### Slack
1. Ve a https://api.slack.com/apps
2. Crea una nueva app o selecciona existente
3. Obtén Bot Token y Signing Secret

## Configuración en .env

```bash
# Dropbox
DROPBOX_ACCESS_TOKEN=tu_token_actual
DROPBOX_APP_KEY=tu_app_key
DROPBOX_APP_SECRET=tu_app_secret
DROPBOX_USER_EMAIL=leopoldo.bassoco@vizum.com.mx
DROPBOX_TEAM_MODE=1

# Pinecone
PINECONE_API_KEY=tu_pinecone_key
PINECONE_INDEX_NAME=tu_index_name

# OpenAI
OPENAI_API_KEY=tu_openai_key

# Slack
SLACK_BOT_TOKEN=tu_slack_bot_token
SLACK_SIGNING_SECRET=tu_slack_signing_secret
```

## Comandos de Verificación

```bash
# Probar conexiones
python optimize_app.py

# Configurar OAuth
python setup_dropbox_auth.py

# Probar sistema completo
python auto_updater.py --test
```
