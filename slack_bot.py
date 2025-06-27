from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone
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
import ssl
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
import re

load_dotenv()

print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar SSL para MacOS
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

# Configurar contexto SSL
ssl_context = ssl.create_default_context(cafile=certifi.where())
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Inicializa clientes
app = App(token=os.getenv("SLACK_BOT_TOKEN"), signing_secret=os.getenv("SLACK_SIGNING_SECRET"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Inicializa Pinecone y Assistant
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = os.getenv("PINECONE_INDEX_NAME")
index = pc.Index(index_name)

# Instrucciones personalizadas para el Assistant
ASSISTANT_INSTRUCTIONS = (
    "Responde como un experto en cumplimiento regulatorio mexicano. "
    "Analiza la información considerando la legislación mexicana, manuales internos de la empresa, disposiciones generales, reglamentos y cualquier normativa aplicable. "
    "Sé claro, profesional y cita la fuente o el documento cuando sea posible. "
    "Si la información no es suficiente, sugiere qué datos adicionales serían útiles."
)

# Crear (o reutilizar) el Assistant de Pinecone
try:
    assistant = pc.assistant.create_assistant(
        assistant_name="vizumcumplimiento",
        instructions=ASSISTANT_INSTRUCTIONS,
        timeout=30
    )
except Exception as e:
    # Si ya existe, obtener el objeto assistant real usando describe_assistant
    assistant = pc.assistant.describe_assistant("vizumcumplimiento")

# Inicializar gestores
conversation_manager = ConversationManager(auto_close_minutes=3)
personality_manager = PersonalityManager()

# Thread pool para procesamiento en background
file_processing_executor = ThreadPoolExecutor(max_workers=3)

# Diccionario para rastrear temporizadores de inactividad por hilo
inactivity_timers = {}
INACTIVITY_WARNING_SECONDS = 180  # 3 minutos antes del mensaje de advertencia
INACTIVITY_CLOSE_SECONDS = 120    # 2 minutos después del mensaje de advertencia para cerrar

def limpiar_texto(texto):
    """Limpia y formatea el texto de los chunks para mayor claridad."""
    # Elimina tabulaciones y múltiples espacios
    texto = re.sub(r'\t+', ' ', texto)
    texto = re.sub(r' +', ' ', texto)
    # Elimina saltos de línea excesivos
    texto = re.sub(r'\n{2,}', '\n', texto)
    # Limita la longitud de cada chunk para evitar contexto demasiado grande
    return texto.strip()[:1200]

def generate_response_with_context(user_question: str, thread_ts: str, channel_id: str, user_id: str, is_new_conversation: bool = False) -> str:
    print("DEBUG: generate_response_with_context llamada con pregunta:", user_question)
    try:
        # 1. Pinecone Assistant hace el análisis exhaustivo
        pinecone_response = assistant.query(
            query=user_question,
            top_k=10,
            index_name=index_name
        )
        pinecone_analysis = pinecone_response["answer"]

        # 2. Obtener contexto de la conversación
        conversation_context = conversation_manager.get_conversation_context(thread_ts)

        # 3. OpenAI filtra, resume o pide aclaraciones
        prompt = f"""
Eres un asistente profesional de cumplimiento, pero responde de manera natural, cercana y sin repetir saludos innecesarios. 
Adapta tu lenguaje al contexto de la conversación y evita sonar robótico. Si ya saludaste, no lo repitas.

--- CONTEXTO DE LA CONVERSACIÓN ---
{conversation_context}

--- CONSULTA DEL USUARIO ---
{user_question}

--- ANÁLISIS DE PINECONE ---
{pinecone_analysis}

1. Si la información es suficiente y clara, resume y entrega la mejor respuesta posible.
2. Si detectas dudas, vacíos o información insuficiente, indícalo y sugiere qué datos adicionales serían útiles o qué se debería consultar de nuevo.

Responde de forma clara, estructurada y útil para un profesional de cumplimiento.
"""
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Eres un asistente profesional de cumplimiento."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        print("DEBUG: Respuesta de OpenAI:", response.choices[0].message.content)
        return response.choices[0].message.content
    except Exception as e:
        import traceback
        print("ERROR en generate_response_with_context:", e)
        print(traceback.format_exc())
        logger.error(f"Error con Pinecone Assistant + OpenAI: {e}")
        return "Kawiller, hubo un problema técnico al analizar la información. Por favor, intenta nuevamente o contacta al equipo de soporte."

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
    print("DEBUG: responder_en_hilo llamada con pregunta:", pregunta)
    thread_ts = event.get("thread_ts") or event.get("ts")
    print("DEBUG: thread_ts usado en responder_en_hilo:", thread_ts)
    channel_id = event.get("channel_id", "")
    user_id = event.get("user_id", "")
    
    # Obtener o crear conversación
    conversation = conversation_manager.get_or_create_conversation(thread_ts, channel_id, user_id)
    
    # Determinar si es una nueva conversación
    is_new_conversation = len(conversation.messages) == 0
    
    # Agregar mensaje del usuario
    conversation_manager.add_message(thread_ts, user_id, pregunta, "user")
    
    # Cancelar temporizador de inactividad si existe
    if thread_ts in inactivity_timers:
        try:
            inactivity_timers[thread_ts].cancel()
            del inactivity_timers[thread_ts]
            print(f"DEBUG: Temporizador cancelado para thread {thread_ts}")
        except Exception as e:
            print(f"DEBUG: Error cancelando temporizador: {e}")
            # Limpiar de todas formas
            if thread_ts in inactivity_timers:
                del inactivity_timers[thread_ts]

    try:
        # Generar respuesta con contexto
        respuesta = generate_response_with_context(pregunta, thread_ts, channel_id, user_id, is_new_conversation)
        
        # Agregar respuesta del bot
        conversation_manager.add_message(thread_ts, user_id, respuesta, "assistant")
        
        # Actualizar resumen de conversación
        update_conversation_summary(thread_ts, pregunta, respuesta)
        
        # No agregar saludo extra, solo la respuesta de OpenAI
        final_response = respuesta
        
        # Sugerencias proactivas
        proactive_suggestions = get_proactive_suggestions(pregunta, respuesta)
        if proactive_suggestions:
            final_response += f"\n\n🤖 *Sugerencias para kawiller:*\n" + "\n".join([f"• {s}" for s in proactive_suggestions])
        
        print("DEBUG: Respuesta final que se enviará a Slack:", final_response)
        # Enviar respuesta
        say(final_response, thread_ts=thread_ts)
        
        # Iniciar temporizador de inactividad
        def inactivity_warning():
            print(f"DEBUG: Función inactivity_warning ejecutada para thread {thread_ts}")
            # Verificar si la conversación sigue activa antes de mostrar el mensaje
            if thread_ts in conversation_manager.conversations:
                conv = conversation_manager.conversations[thread_ts]
                time_since_last_activity = time.time() - conv.last_activity
                print(f"DEBUG: Tiempo desde última actividad: {time_since_last_activity:.1f}s")
                
                # Solo mostrar advertencia si realmente han pasado 3 minutos sin actividad
                if time_since_last_activity >= INACTIVITY_WARNING_SECONDS:
                    print(f"DEBUG: Mostrando mensaje de advertencia para thread {thread_ts}")
                    say(personality_manager.get_inactivity_warning_message(), thread_ts=thread_ts)
                    # Segundo temporizador para cerrar si no hay respuesta
                    def close_thread():
                        print(f"DEBUG: Función close_thread ejecutada para thread {thread_ts}")
                        # Verificar nuevamente antes de cerrar
                        if thread_ts in conversation_manager.conversations:
                            conv = conversation_manager.conversations[thread_ts]
                            time_since_warning = time.time() - conv.last_activity
                            print(f"DEBUG: Tiempo desde advertencia: {time_since_warning:.1f}s")
                            if time_since_warning >= INACTIVITY_CLOSE_SECONDS:
                                print(f"DEBUG: Cerrando conversación por inactividad: {thread_ts}")
                                conversation_manager.close_conversation(thread_ts)
                                say(personality_manager.get_thread_closed_message(), thread_ts=thread_ts)
                                # Limpiar el temporizador
                                if thread_ts in inactivity_timers:
                                    del inactivity_timers[thread_ts]
                            else:
                                print(f"DEBUG: Conversación reactivada, no cerrando: {thread_ts}")
                        else:
                            print(f"DEBUG: Conversación ya no existe: {thread_ts}")
                    inactivity_timers[thread_ts] = threading.Timer(INACTIVITY_CLOSE_SECONDS, close_thread)
                    inactivity_timers[thread_ts].start()
                    print(f"DEBUG: Temporizador de cierre iniciado para thread {thread_ts}")
                else:
                    # Si hay actividad reciente, reprogramar el temporizador
                    remaining_time = INACTIVITY_WARNING_SECONDS - time_since_last_activity
                    print(f"DEBUG: Reprogramando temporizador para thread {thread_ts}, tiempo restante: {remaining_time:.1f}s")
                    inactivity_timers[thread_ts] = threading.Timer(remaining_time, inactivity_warning)
                    inactivity_timers[thread_ts].start()
            else:
                # La conversación ya no existe, limpiar el temporizador
                print(f"DEBUG: Conversación no encontrada, limpiando temporizador: {thread_ts}")
                if thread_ts in inactivity_timers:
                    del inactivity_timers[thread_ts]
        
        inactivity_timers[thread_ts] = threading.Timer(INACTIVITY_WARNING_SECONDS, inactivity_warning)
        inactivity_timers[thread_ts].start()
        print(f"DEBUG: Temporizador de inactividad iniciado para thread {thread_ts} ({INACTIVITY_WARNING_SECONDS}s)")
        
    except Exception as e:
        import traceback
        print("ERROR en responder_en_hilo:", e)
        print(traceback.format_exc())
        logger.error(f"Error generando respuesta: {e}")
        error_message = personality_manager.get_error_message(str(e))
        say(error_message, thread_ts=thread_ts)

def get_proactive_suggestions(user_question, bot_response):
    """Generar sugerencias proactivas basadas en la pregunta y respuesta"""
    # Sugerencias básicas, pueden mejorarse con IA
    suggestions = []
    if "ley" in user_question.lower() or "regulación" in user_question.lower():
        suggestions.append("¿Quieres consultar la legislación mexicana con /legislacion-mexicana?")
    if "documento" in user_question.lower() or "archivo" in user_question.lower():
        suggestions.append("Puedes subir otro archivo para analizarlo o preguntar sobre su contenido.")
    suggestions.append("Consulta el estado de procesamiento con /processing-status.")
    suggestions.append("Obtén insights de tus conversaciones con /conversation-insights.")
    return suggestions

@app.event("app_mention")
def handle_app_mention_events(body, say):
    event = body["event"]
    pregunta = (event.get("text") or "").replace(f"<@{os.getenv('SLACK_BOT_TOKEN')}>", "").strip()
    print("Texto recibido:", event.get("text"))
    print("Pregunta extraída:", pregunta)
    if not pregunta:
        say("Kawiller, por favor escribe tu pregunta después de mencionarme.")
        return
    responder_en_hilo(event, say, pregunta)

@app.message("")
def handle_message_events(message, say):
    thread_ts = message.get("thread_ts") or message.get("ts")
    channel_id = message.get("channel", "")
    user_id = message.get("user", "")
    texto = message.get("text", "")
    print("DEBUG: Texto recibido en mensaje:", texto)
    print("DEBUG: thread_ts usado en handler:", thread_ts)

    # No procesar mensajes vacíos
    if not texto or not texto.strip():
        print("DEBUG: Mensaje vacío, no se responde.")
        return

    # Si el mensaje es en un hilo, responde siempre
    if thread_ts:
        responder_en_hilo(message, say, texto)
    # Si es mensaje directo, responde siempre
    elif channel_id.startswith("D"):
        responder_en_hilo(message, say, texto)
    # Si no, ignora mensajes en canales públicos fuera de hilos

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

    # Mensaje inmediato de confirmación de recepción
    say(f"📥 Kawiller, he recibido tu archivo *{file_name}*. Comenzando el procesamiento en background...", thread_ts=thread_ts or event.get("ts"))

    # Descargar el archivo usando el token del bot
    headers = {"Authorization": f"Bearer {os.getenv('SLACK_BOT_TOKEN')}"}
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        response = requests.get(file_url, headers=headers)
        tmp_file.write(response.content)
        tmp_file_path = tmp_file.name

    # Procesar archivo en background
    file_processing_executor.submit(
        process_file_in_background,
        tmp_file_path,
        file_name,
        user_id,
        channel_id,
        thread_ts or event.get("ts"),
        client
    )

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

Las conversaciones se cierran automáticamente después de 5 minutos de inactividad total.
    """
    
    respond(response)

@app.command("/processing-status")
def handle_processing_status(ack, respond):
    """Comando para ver el estado de archivos en procesamiento"""
    ack()
    
    # Obtener información del thread pool
    active_threads = file_processing_executor._threads
    queue_size = file_processing_executor._work_queue.qsize()
    
    response = f"""
🔄 *Estado de Procesamiento de Archivos*

• Hilos activos: {len(active_threads)}
• Archivos en cola: {queue_size}
• Hilos máximos: 3

Los archivos se procesan en background para no bloquear el bot.
    """
    
    respond(response)

@app.command("/legislacion-mexicana")
def handle_mexican_legislation(ack, body, respond):
    """Comando para consultar legislación mexicana específica"""
    ack()
    
    command_text = (body.get('text') or '').replace('/legislacion-mexicana', '').strip()
    
    if not command_text:
        response = """
🇲🇽 *Consulta de Legislación Mexicana*

Uso: `/legislacion-mexicana [tema o pregunta]`

Ejemplos:
• `/legislacion-mexicana LFT`
• `/legislacion-mexicana Ley Federal del Trabajo vacaciones`
• `/legislacion-mexicana ISR personas físicas`
• `/legislacion-mexicana Ley General de Sociedades Mercantiles`

Puedo ayudarte con:
• Ley Federal del Trabajo (LFT)
• Código Fiscal de la Federación (CFF)
• Ley del Impuesto sobre la Renta (LISR)
• Ley General de Sociedades Mercantiles (LGSM)
• Ley de Protección al Consumidor
• Y más...
        """
        respond(response)
        return
    
    try:
        # Generar respuesta específica sobre legislación mexicana
        legislation_prompt = f"""
        Como experto en legislación mexicana, responde la siguiente consulta sobre cumplimiento regulatorio en México.
        
        Consulta: {command_text}
        
        Proporciona:
        1. Información relevante de la legislación mexicana
        2. Artículos específicos aplicables
        3. Obligaciones y requisitos
        4. Sanciones o consecuencias por incumplimiento
        5. Recomendaciones prácticas
        
        Mantén un tono profesional pero accesible, dirigido a "kawiller".
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Eres un experto en legislación mexicana y cumplimiento regulatorio. Proporciona información precisa y actualizada sobre leyes mexicanas."},
                {"role": "user", "content": legislation_prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        legislation_response = response.choices[0].message.content
        
        # Formatear respuesta
        formatted_response = f"🇲🇽 *Consulta: {command_text}*\n\n{legislation_response}"
        
        respond(formatted_response)
        
    except Exception as e:
        logger.error(f"Error consultando legislación mexicana: {e}")
        error_msg = f"Kawiller, lamento los inconvenientes. He encontrado un problema técnico al consultar la legislación: {str(e)}"
        respond(error_msg)

@app.command("/conversation-insights")
def handle_conversation_insights(ack, body, respond):
    """Comando para ver insights de conversaciones"""
    ack()
    
    command_text = (body.get('text') or '').replace('/conversation-insights', '').strip()
    
    if not command_text:
        # Mostrar insights generales
        patterns = conversation_manager.analyze_conversation_patterns()
        
        response = f"""
📊 *Insights de Conversaciones*

• Total de mensajes de usuarios: {patterns.get('total_user_messages', 0)}
• Usuarios únicos: {patterns.get('unique_users', 0)}
• Promedio de mensajes por usuario: {patterns.get('avg_messages_per_user', 0):.1f}

*Usuarios más activos:*
"""
        
        for user_id, count in patterns.get('most_active_users', []):
            response += f"• <@{user_id}>: {count} mensajes\n"
        
        response += "\nUsa `/conversation-insights [thread_ts]` para ver detalles de una conversación específica."
        
        respond(response)
        return
    
    # Mostrar insights de una conversación específica
    thread_ts = command_text
    insights = conversation_manager.get_conversation_insights(thread_ts)
    
    if not insights:
        respond("❌ Kawiller, no encontré una conversación con ese identificador.")
        return
    
    response = f"""
📈 *Insights de Conversación*

• Duración: {insights.get('duration_minutes', 0):.1f} minutos
• Total de mensajes: {insights.get('message_count', 0)}
• Mensajes del usuario: {insights.get('user_messages', 0)}
• Respuestas del bot: {insights.get('assistant_messages', 0)}

*Temas discutidos:*
"""
    
    topics = insights.get('topics_discussed', [])
    if topics:
        for topic in topics:
            response += f"• {topic}\n"
    else:
        response += "• No se identificaron temas específicos\n"
    
    respond(response)

def process_file_in_background(file_path: str, file_name: str, user_id: str, channel_id: str, thread_ts: str, client):
    """Procesar archivo en background y enviar actualizaciones de estado"""
    try:
        processing_message = personality_manager.get_file_processing_message(file_name, needs_ocr(file_name))
        client.chat_postMessage(
            channel=channel_id,
            thread_ts=thread_ts,
            text=processing_message
        )
        needs_ocr_processing = needs_ocr(file_name)
        if needs_ocr_processing:
            text = extract_text_with_ocr_if_needed(file_path)
        else:
            text = extract_text_from_file(file_path)
        if not text.strip():
            error_msg = f"⚠️ Kawiller, no se pudo extraer texto del archivo *{file_name}*. Verifica que el archivo contenga texto legible."
            client.chat_postMessage(
                channel=channel_id,
                thread_ts=thread_ts,
                text=error_msg
            )
            return
        chunks = chunk_text(text)
        analysis = analyze_document_content(text, file_name)
        progress_msg = f"📊 Kawiller, he extraído {len(chunks)} secciones del archivo *{file_name}*."\
                      f"\n\n📋 *Análisis del documento:*\n"\
                      f"• Tipo: {analysis.get('tipo_documento', 'Documento')}\n"\
                      f"• Temas regulatorios: {', '.join(analysis.get('temas_regulatorios', ['No identificados']))}\n"\
                      f"• Riesgos detectados: {len(analysis.get('riesgos', []) )}\n\n"\
                      "Ahora estoy agregando la información a la base de conocimiento..."
        client.chat_postMessage(
            channel=channel_id,
            thread_ts=thread_ts,
            text=progress_msg
        )
        for i, chunk in enumerate(chunks):
            try:
                embedding = get_embedding(chunk)
                index.upsert(vectors=[{
                    'id': str(uuid4()),
                    'values': embedding,
                    'metadata': {
                        "cliente": user_id or "slack_user",
                        "nombre_archivo": file_name,
                        "ruta": file_name,
                        "chunk_index": i,
                        "texto": chunk,
                        "procesado_con_ocr": needs_ocr_processing
                    }
                }])
            except Exception as chunk_e:
                logger.error(f"Error subiendo chunk {i} de {file_name}: {chunk_e}")
                client.chat_postMessage(
                    channel=channel_id,
                    thread_ts=thread_ts,
                    text=f"⚠️ Error subiendo chunk {i} de {file_name}: {chunk_e}"
                )
        completion_message = personality_manager.get_file_completion_message(file_name, len(chunks), needs_ocr_processing)
        client.chat_postMessage(
            channel=channel_id,
            thread_ts=thread_ts,
            text=completion_message
        )
    except Exception as e:
        logger.error(f"Error procesando archivo {file_name} en background: {str(e)}", exc_info=True)
        import traceback
        tb = traceback.format_exc()
        error_message = personality_manager.get_error_message(str(e))
        client.chat_postMessage(
            channel=channel_id,
            thread_ts=thread_ts,
            text=f"{error_message}\n\n*Detalles técnicos:*\n```{tb}```"
        )
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

def analyze_document_content(text: str, file_name: str) -> dict:
    """Analizar contenido del documento para extraer información relevante"""
    try:
        # Prompt para análisis de contenido
        analysis_prompt = f"""
        Analiza el siguiente documento y extrae información relevante para cumplimiento regulatorio.
        
        Nombre del archivo: {file_name}
        Contenido: {text[:2000]}...  # Primeros 2000 caracteres para análisis
        
        Proporciona un análisis estructurado con:
        1. Tipo de documento (política, reporte, contrato, etc.)
        2. Entidades mencionadas (empresas, personas, fechas)
        3. Temas regulatorios identificados
        4. Riesgos de cumplimiento detectados
        5. Acciones recomendadas
        
        Responde en formato JSON.
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Eres un analista experto en cumplimiento regulatorio. Analiza documentos y extrae información relevante de manera estructurada."},
                {"role": "user", "content": analysis_prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        # Intentar parsear la respuesta como JSON
        try:
            import json
            analysis = json.loads(response.choices[0].message.content)
            return analysis
        except:
            # Si no es JSON válido, crear estructura básica
            return {
                "tipo_documento": "documento",
                "entidades": [],
                "temas_regulatorios": [],
                "riesgos": [],
                "acciones_recomendadas": []
            }
            
    except Exception as e:
        logger.error(f"Error analizando documento {file_name}: {e}")
        return {
            "tipo_documento": "documento",
            "entidades": [],
            "temas_regulatorios": [],
            "riesgos": [],
            "acciones_recomendadas": []
        }

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    handler.start() 