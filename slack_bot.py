from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
from dotenv import load_dotenv
from openai import OpenAI
import pinecone
from extractor.text_chunker import get_embedding, chunk_text
from extractor.pinecone_uploader import query_pinecone
from extractor.extractor_ocr import needs_ocr, extract_text_with_ocr_if_needed
from utils.text_extractor import extract_text_from_file
from conversation_manager import ConversationManager
from personality_manager import PersonalityManager
import tempfile
import requests
from uuid import uuid4
import logging
import time
import certifi

load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializa clientes
app = App(token=os.getenv("SLACK_BOT_TOKEN"), signing_secret=os.getenv("SLACK_SIGNING_SECRET"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Inicializa Pinecone antes de usarlo
pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment=os.getenv("PINECONE_ENVIRONMENT")
)
# Cuando necesites el índice:
index = pinecone.Index(os.getenv("PINECONE_INDEX_NAME"))

# Inicializar gestores
conversation_manager = ConversationManager(auto_close_minutes=3)
personality_manager = PersonalityManager()

os.environ["SSL_CERT_FILE"] = certifi.where()

def generate_response_with_context(user_question: str, thread_ts: str, channel_id: str, user_id: str) -> str:
    """Generar respuesta considerando contexto de conversación y Pinecone"""
    
    # Obtener contexto de la conversación
    conversation_context = conversation_manager.get_conversation_context(thread_ts)
    
    # Obtener información relevante de Pinecone
    embedding = get_embedding(user_question)
    results = query_pinecone(index, embedding, top_k=5)
    pinecone_context = "\n\n".join([match['metadata']['texto'] for match in results['matches']])
    
    # Generar prompt mejorado
    prompts = personality_manager.get_enhanced_prompt(
        user_question=user_question,
        conversation_context=conversation_context,
        pinecone_context=pinecone_context
    )
    
    # Generar respuesta con OpenAI
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompts["system"]},
            {"role": "user", "content": prompts["user"]}
        ],
        max_tokens=1000,
        temperature=0.7
    )
    
    return response.choices[0].message.content

def update_conversation_summary(thread_ts: str, user_question: str, bot_response: str):
    """Actualizar resumen de la conversación"""
    try:
        # Generar resumen de la conversación actual
        summary_prompt = personality_manager.get_conversation_summary_prompt(
            f"Usuario: {user_question}\nAsistente: {bot_response}"
        )
        
        summary_response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Eres un asistente que genera resúmenes concisos y profesionales."},
                {"role": "user", "content": summary_prompt}
            ],
            max_tokens=200,
            temperature=0.3
        )
        
        summary = summary_response.choices[0].message.content
        conversation_manager.update_context_summary(thread_ts, summary)
        
    except Exception as e:
        logger.error(f"Error actualizando resumen de conversación: {e}")

def responder_en_hilo(event, say, pregunta):
    """Responder en hilo con contexto de conversación"""
    thread_ts = event.get("thread_ts", event.get("ts"))
    channel_id = event.get("channel_id", "")
    user_id = event.get("user_id", "")
    
    # Obtener o crear conversación
    conversation = conversation_manager.get_or_create_conversation(thread_ts, channel_id, user_id)
    
    # Determinar si es una nueva conversación
    is_new_conversation = len(conversation.messages) == 0
    
    # Agregar mensaje del usuario
    conversation_manager.add_message(thread_ts, user_id, pregunta, "user")
    
    try:
        # Generar respuesta con contexto
        respuesta = generate_response_with_context(pregunta, thread_ts, channel_id, user_id)
        
        # Agregar respuesta del bot
        conversation_manager.add_message(thread_ts, user_id, respuesta, "assistant")
        
        # Actualizar resumen de conversación
        update_conversation_summary(thread_ts, pregunta, respuesta)
        
        # Formatear respuesta final
        if is_new_conversation:
            # Para nuevas conversaciones, incluir saludo
            final_response = personality_manager.format_professional_response(respuesta, include_greeting=True)
        else:
            # Para conversaciones continuas, solo la respuesta
            final_response = respuesta
        
        # Enviar respuesta
        say(final_response, thread_ts=thread_ts)
        
    except Exception as e:
        logger.error(f"Error generando respuesta: {e}")
        error_message = personality_manager.get_error_message(str(e))
        say(error_message, thread_ts=thread_ts)

@app.event("app_mention")
def handle_app_mention_events(body, say):
    event = body["event"]
    pregunta = event["text"].replace(f"<@{os.getenv('SLACK_BOT_TOKEN')}>", "").strip()
    responder_en_hilo(event, say, pregunta)

@app.message("")
def handle_message_events(message, say):
    # Solo responder a mensajes directos o en hilos donde el bot ya participó
    thread_ts = message.get("thread_ts", message.get("ts"))
    
    # Verificar si hay una conversación activa en este hilo
    if thread_ts in conversation_manager.conversations:
        responder_en_hilo(message, say, message["text"])
    else:
        # Para mensajes directos sin conversación previa, crear una nueva
        responder_en_hilo(message, say, message["text"])

@app.event("file_shared")
def handle_file_shared_events(body, client, say):
    event = body["event"]
    file_id = event["file_id"]
    user_id = event.get("user_id", "")
    channel_id = event.get("channel_id", "")
    thread_ts = event.get("thread_ts") or event.get("ts")

    # Obtener información del archivo
    file_info = client.files_info(file=file_id)["file"]
    file_url = file_info["url_private_download"]
    file_name = file_info["name"]

    # Mensaje inmediato de procesamiento con personalidad
    processing_message = personality_manager.get_file_processing_message(file_name, needs_ocr(file_name))
    say(processing_message, thread_ts=thread_ts or event.get("ts"))

    # Descargar el archivo usando el token del bot
    headers = {"Authorization": f"Bearer {os.getenv('SLACK_BOT_TOKEN')}"}
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        response = requests.get(file_url, headers=headers)
        tmp_file.write(response.content)
        tmp_file_path = tmp_file.name

    try:
        # Determinar si el archivo necesita OCR
        if needs_ocr(file_name):
            text = extract_text_with_ocr_if_needed(tmp_file_path)
        else:
            # Procesar el archivo normalmente
            text = extract_text_from_file(tmp_file_path)
        
        if not text.strip():
            say(f"⚠️ No se pudo extraer texto del archivo *{file_name}*. Verifica que el archivo contenga texto legible.", thread_ts=thread_ts or event.get("ts"))
            return
            
        chunks = chunk_text(text)
        cliente = user_id or "slack_user"
        
        # Subir chunks a Pinecone
        for i, chunk in enumerate(chunks):
            embedding = get_embedding(chunk)
            index.upsert(vectors=[{
                'id': str(uuid4()),
                'values': embedding,
                'metadata': {
                    "cliente": cliente,
                    "nombre_archivo": file_name,
                    "ruta": file_name,
                    "chunk_index": i,
                    "texto": chunk,
                    "procesado_con_ocr": needs_ocr(file_name)
                }
            }])
        
        # Mensaje de confirmación con personalidad
        completion_message = personality_manager.get_file_completion_message(file_name, len(chunks), needs_ocr(file_name))
        say(completion_message, thread_ts=thread_ts or event.get("ts"))
            
    except Exception as e:
        logger.error(f"Error procesando archivo {file_name}: {str(e)}")
        error_message = personality_manager.get_error_message(str(e))
        say(error_message, thread_ts=thread_ts or event.get("ts"))
    finally:
        if tmp_file_path and os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

@app.command("/conversation-stats")
def handle_conversation_stats(ack, respond):
    """Comando para ver estadísticas de conversaciones"""
    ack()
    stats = conversation_manager.get_conversation_stats()
    
    response = f"""
📊 *Estadísticas de Conversaciones*

• Conversaciones activas: {stats['active_conversations']}
• Total de conversaciones: {stats['total_conversations']}
• Archivo de almacenamiento: {stats['storage_file']}

Las conversaciones se cierran automáticamente después de 3 minutos de inactividad.
    """
    
    respond(response)

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    handler.start() 