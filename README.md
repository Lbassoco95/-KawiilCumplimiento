# KawiilVizumCumplimiento - Bot de Slack con IA

Bot inteligente de Slack que procesa documentos, extrae información usando OCR y responde preguntas usando IA con memoria conversacional.

## Características

- **Procesamiento de documentos**: PDF, Word, Excel, CSV, PowerPoint
- **OCR integrado**: Extracción de texto de imágenes y PDFs escaneados
- **Memoria conversacional**: Mantiene contexto por hilo de conversación
- **Integración con Pinecone**: Búsqueda semántica en documentos procesados
- **Integración con Dropbox**: Procesamiento automático de archivos compartidos
- **Personalidad profesional**: Respuestas contextuales y humanas

## Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/tuusuario/KawiilVizumCumplimiento.git
cd KawiilVizumCumplimiento
```

2. Crea un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
# o
venv\Scripts\activate  # En Windows
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

4. Configura las variables de entorno:
```bash
cp config_env_example.txt .env
# Edita .env con tus credenciales
```

5. Ejecuta el bot:
```bash
python slack_bot.py
```

## Configuración

Necesitas configurar las siguientes variables de entorno en el archivo `.env`:

- `SLACK_BOT_TOKEN`: Token del bot de Slack
- `SLACK_APP_TOKEN`: Token de la app de Slack
- `OPENAI_API_KEY`: API key de OpenAI
- `PINECONE_API_KEY`: API key de Pinecone
- `PINECONE_INDEX_NAME`: Nombre del índice de Pinecone
- `DROPBOX_ACCESS_TOKEN`: Token de acceso de Dropbox

## Uso

El bot responde a menciones (`@bot`) en Slack y puede:
- Procesar archivos compartidos
- Responder preguntas sobre documentos
- Mantener conversaciones contextuales
- Procesar archivos desde Dropbox

## Estructura del Proyecto

- `slack_bot.py`: Bot principal de Slack
- `extractor/`: Módulos de extracción de texto
- `utils/`: Utilidades generales
- `conversation_manager.py`: Gestor de conversaciones
- `personality_manager.py`: Gestor de personalidad
- `dropbox_processor.py`: Procesador de archivos de Dropbox

## Despliegue en Google Cloud

Ver la documentación en `README_CONVERSATION_SYSTEM.md` para instrucciones de despliegue en la nube. 