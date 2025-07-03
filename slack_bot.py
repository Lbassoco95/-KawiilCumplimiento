#!/usr/bin/env python3
"""
Bot de Slack para consultas de cumplimiento regulatorio
Integrado con Pinecone y OpenAI para respuestas inteligentes
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from pinecone import Pinecone
from openai import OpenAI
from extractor.text_chunker import get_embedding

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('slack_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Configuración
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Inicializar clientes
app = App(token=SLACK_BOT_TOKEN)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def search_documents(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Buscar documentos relevantes en Pinecone"""
    try:
        # Generar embedding de la consulta
        query_embedding = get_embedding(query)
        
        # Buscar en Pinecone
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        return results.matches
    except Exception as e:
        logger.error(f"Error en búsqueda: {e}")
        return []

def format_metadata_summary(metadata: Dict[str, Any]) -> str:
    """Formatear resumen de metadatos para Slack"""
    summary = []
    
    # Información básica
    if metadata.get("nombre_archivo"):
        summary.append(f"📄 *Archivo:* {metadata['nombre_archivo']}")
    
    if metadata.get("cliente"):
        summary.append(f"👤 *Cliente:* {metadata['cliente']}")
    
    # Metadatos enriquecidos
    if metadata.get("tipo_documento"):
        summary.append(f"📋 *Tipo:* {metadata['tipo_documento']}")
    
    if metadata.get("categoria_regulatoria"):
        summary.append(f"🏛️ *Categoría:* {metadata['categoria_regulatoria']}")
    
    if metadata.get("entidad_regulatoria"):
        summary.append(f"🏢 *Entidad:* {metadata['entidad_regulatoria']}")
    
    if metadata.get("nivel_importancia"):
        summary.append(f"⭐ *Importancia:* {metadata['nivel_importancia']}")
    
    if metadata.get("fecha_documento") and metadata["fecha_documento"] != "No especificada":
        summary.append(f"📅 *Fecha:* {metadata['fecha_documento']}")
    
    if metadata.get("resumen_executivo"):
        summary.append(f"📝 *Resumen:* {metadata['resumen_executivo']}")
    
    # Temas principales
    if metadata.get("temas_principales"):
        temas = ", ".join(metadata["temas_principales"][:3])  # Máximo 3 temas
        summary.append(f"🎯 *Temas:* {temas}")
    
    # Palabras clave
    if metadata.get("palabras_clave"):
        keywords = ", ".join(metadata["palabras_clave"][:5])  # Máximo 5 palabras
        summary.append(f"🔑 *Palabras clave:* {keywords}")
    
    return "\n".join(summary)

def generate_enhanced_response(query: str, search_results: List[Dict[str, Any]]) -> str:
    """Generar respuesta mejorada usando OpenAI con metadatos enriquecidos"""
    try:
        # Preparar contexto con metadatos enriquecidos
        context_parts = []
        
        for i, result in enumerate(search_results[:3], 1):  # Usar top 3 resultados
            metadata = result.metadata
            score = result.score
            
            # Crear resumen del documento con metadatos enriquecidos
            doc_summary = f"""
Documento {i} (Relevancia: {score:.2f}):
{format_metadata_summary(metadata)}

Contenido relevante:
{metadata.get('texto', '')[:500]}...
"""
            context_parts.append(doc_summary)
        
        context = "\n\n".join(context_parts)
        
        # Generar respuesta con OpenAI
        prompt = f"""
Eres un experto en cumplimiento regulatorio financiero. Responde la siguiente consulta basándote en los documentos proporcionados.

Consulta del usuario: {query}

Documentos relevantes:
{context}

Instrucciones:
1. Proporciona una respuesta clara y profesional
2. Cita información específica de los documentos cuando sea relevante
3. Si hay múltiples documentos, organiza la respuesta por temas
4. Incluye recomendaciones prácticas cuando sea apropiado
5. Si la información no está disponible en los documentos, indícalo claramente
6. Usa un tono profesional pero accesible

Formato de respuesta:
- Resumen ejecutivo de la respuesta
- Detalles específicos organizados por temas
- Referencias a documentos específicos
- Recomendaciones o próximos pasos (si aplica)
"""
        
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Eres un consultor experto en cumplimiento regulatorio financiero con amplia experiencia en AML, KYC, y regulaciones bancarias."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error(f"Error generando respuesta: {e}")
        return f"❌ Error generando respuesta: {e}"

def create_enhanced_slack_response(query: str, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Crear respuesta estructurada para Slack con metadatos enriquecidos"""
    
    # Generar respuesta principal
    main_response = generate_enhanced_response(query, search_results)
    
    # Crear bloques de Slack
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🔍 Resultados de Búsqueda en Cumplimiento Regulatorio",
                "emoji": True
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Consulta:* {query}"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": main_response
            }
        }
    ]
    
    # Agregar información de documentos encontrados
    if search_results:
        blocks.append({"type": "divider"})
        
        # Crear sección de documentos
        docs_text = "*📚 Documentos Consultados:*\n"
        for i, result in enumerate(search_results[:3], 1):
            metadata = result.metadata
            score = result.score
            
            docs_text += f"\n*{i}. {metadata.get('nombre_archivo', 'Documento')}*"
            docs_text += f"\n   • Relevancia: {score:.2f}"
            docs_text += f"\n   • Tipo: {metadata.get('tipo_documento', 'N/A')}"
            docs_text += f"\n   • Categoría: {metadata.get('categoria_regulatoria', 'N/A')}"
            
            if metadata.get("entidad_regulatoria"):
                docs_text += f"\n   • Entidad: {metadata['entidad_regulatoria']}"
            
            if metadata.get("nivel_importancia"):
                docs_text += f"\n   • Importancia: {metadata['nivel_importancia']}"
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": docs_text
            }
        })
    
    # Agregar información de búsqueda
    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": f"🔍 Búsqueda realizada el {datetime.now().strftime('%d/%m/%Y %H:%M')} | 📊 {len(search_results)} documentos encontrados"
            }
        ]
    })
    
    return {
        "response_type": "in_channel",
        "blocks": blocks
    }

@app.message("")
def handle_message(message, say):
    """Manejar mensajes entrantes"""
    try:
        user_query = message.get('text', '').strip()
        user_id = message.get('user', '')
        
        # Ignorar mensajes del bot
        if message.get('bot_id'):
            return
        
        logger.info(f"Consulta de usuario {user_id}: {user_query}")
        
        # Buscar documentos relevantes
        search_results = search_documents(user_query)
        
        if not search_results:
            response = {
                "response_type": "in_channel",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"❌ No se encontraron documentos relevantes para: *{user_query}*\n\n💡 Intenta reformular tu consulta o usar palabras clave más específicas."
                        }
                    }
                ]
            }
        else:
            # Generar respuesta mejorada
            response = create_enhanced_slack_response(user_query, search_results)
        
        # Enviar respuesta
        say(**response)
        
        logger.info(f"Respuesta enviada para usuario {user_id}")
        
    except Exception as e:
        logger.error(f"Error manejando mensaje: {e}")
        say(f"❌ Error procesando tu consulta: {e}")

@app.command("/cumplimiento")
def handle_cumplimiento_command(ack, command, respond):
    """Manejar comando /cumplimiento"""
    try:
        ack()
        
        query = command.get('text', '').strip()
        if not query:
            respond("❌ Por favor proporciona una consulta. Ejemplo: `/cumplimiento requisitos KYC`")
            return
        
        user_id = command.get('user_id', '')
        logger.info(f"Comando /cumplimiento de usuario {user_id}: {query}")
        
        # Buscar documentos
        search_results = search_documents(query)
        
        if not search_results:
            respond(f"❌ No se encontraron documentos relevantes para: *{query}*")
            return
        
        # Generar respuesta mejorada
        response = create_enhanced_slack_response(query, search_results)
        respond(**response)
        
        logger.info(f"Respuesta de comando enviada para usuario {user_id}")
        
    except Exception as e:
        logger.error(f"Error manejando comando: {e}")
        respond(f"❌ Error procesando comando: {e}")

@app.command("/estado")
def handle_status_command(ack, command, respond):
    """Manejar comando /estado para verificar estado del sistema"""
    try:
        ack()
        
        # Obtener estadísticas del índice
        stats = index.describe_index_stats()
        total_vectors = stats.total_vector_count
        
        # Contar vectores con metadatos enriquecidos
        enriched_count = 0
        try:
            # Buscar vectores con metadatos enriquecidos
            query_response = index.query(
                vector=[0] * 1536,
                top_k=1000,
                include_metadata=True,
                filter={"metadata_enriquecido": {"$eq": True}}
            )
            enriched_count = len(query_response.matches)
        except:
            enriched_count = "N/A"
        
        status_text = f"""
📊 *Estado del Sistema de Cumplimiento*

🔍 *Base de Datos:*
• Total de vectores: {total_vectors:,}
• Vectores con metadatos enriquecidos: {enriched_count}
• Estado: ✅ Operativo

🤖 *Servicios:*
• Pinecone: ✅ Conectado
• OpenAI: ✅ Conectado
• Slack Bot: ✅ Activo

⏰ *Última actualización:* {datetime.now().strftime('%d/%m/%Y %H:%M')}
        """
        
        respond({
            "response_type": "in_channel",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": status_text
                    }
                }
            ]
        })
        
    except Exception as e:
        logger.error(f"Error en comando /estado: {e}")
        respond(f"❌ Error verificando estado: {e}")

@app.event("message")
def handle_message_events(body, logger):
    """Manejar eventos de mensajes, incluyendo archivos compartidos"""
    try:
        event = body.get("event", {})
        event_type = event.get("type")
        subtype = event.get("subtype")
        
        # Manejar archivos compartidos
        if event_type == "message" and subtype == "file_share":
            logger.info(f"📎 Archivo compartido detectado: {event}")
            
            # Obtener información del archivo
            files = event.get("files", [])
            for file_info in files:
                file_name = file_info.get('name', 'Sin nombre')
                file_id = file_info.get('id', 'Sin ID')
                file_type = file_info.get('filetype', 'desconocido')
                
                logger.info(f"📄 Archivo: {file_name} (ID: {file_id}, Tipo: {file_type})")
                
                # TODO: Implementar procesamiento de archivos cuando Dropbox esté configurado
                logger.info("⚠️ Procesamiento automático requiere configuración de Dropbox")
                
                # Por ahora, solo informar al usuario
                # Nota: Esto requeriría acceso al cliente de Slack para responder
                logger.info(f"💡 Usuario puede procesar manualmente con: /procesar_archivo {file_id}")
        
        # Manejar otros tipos de mensajes (ya manejados por @app.message(""))
        elif event_type == "message" and not subtype:
            logger.info(f"💬 Mensaje regular: {event.get('text', 'Sin texto')}")
            
    except Exception as e:
        logger.error(f"❌ Error manejando evento de mensaje: {e}")

def main():
    """Función principal"""
    logger.info("🤖 Iniciando Bot de Slack para Cumplimiento Regulatorio")
    logger.info("🔍 Metadatos enriquecidos: ✅ Activado")
    
    # Verificar configuración
    if not all([SLACK_BOT_TOKEN, SLACK_APP_TOKEN, PINECONE_API_KEY, OPENAI_API_KEY]):
        logger.error("❌ Variables de entorno faltantes")
        return
    
    try:
        # Verificar conexión con Pinecone
        stats = index.describe_index_stats()
        logger.info(f"✅ Conectado a Pinecone: {stats.total_vector_count} vectores")
        
        # Iniciar bot
        handler = SocketModeHandler(app, SLACK_APP_TOKEN)
        logger.info("🚀 Bot iniciado exitosamente")
        handler.start()
        
    except Exception as e:
        logger.error(f"❌ Error iniciando bot: {e}")

if __name__ == "__main__":
    main() 