import tiktoken  # type: ignore
import re
from typing import List
import os
import certifi
import ssl

# Configurar SSL para MacOS
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

# Configurar contexto SSL
ssl_context = ssl.create_default_context(cafile=certifi.where())
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

def chunk_text(text: str, max_tokens: int = 500) -> List[str]:
    """
    Divide un texto largo en bloques de hasta max_tokens, procurando no cortar frases o párrafos.
    Args:
        text (str): Texto a dividir en chunks.
        max_tokens (int): Número máximo de tokens por chunk (default: 500).
    Returns:
        List[str]: Lista con los chunks de texto.
    """
    # Inicializar el tokenizador para el modelo text-embedding-3-small
    try:
        encoding = tiktoken.encoding_for_model("text-embedding-3-small")
    except KeyError:
        # Fallback a cl100k_base si text-embedding-3-small no está disponible
        encoding = tiktoken.get_encoding("cl100k_base")
    
    # Dividir el texto en párrafos
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    current_tokens = 0
    
    for paragraph in paragraphs:
        # Limpiar el párrafo
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        
        # Contar tokens del párrafo
        paragraph_tokens = len(encoding.encode(paragraph))
        
        # Si el párrafo completo cabe en el chunk actual
        if current_tokens + paragraph_tokens <= max_tokens:
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph
            current_tokens += paragraph_tokens
        else:
            # Si el párrafo es muy largo, dividirlo en frases
            if paragraph_tokens > max_tokens:
                # Guardar el chunk actual si existe
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""
                    current_tokens = 0
                
                # Dividir el párrafo largo en frases
                sentences = re.split(r'[.!?]+', paragraph)
                temp_chunk = ""
                temp_tokens = 0
                
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                    
                    # Agregar puntuación de cierre si es necesario
                    if not sentence.endswith(('.', '!', '?')):
                        sentence += '.'
                    
                    sentence_tokens = len(encoding.encode(sentence))
                    
                    if temp_tokens + sentence_tokens <= max_tokens:
                        if temp_chunk:
                            temp_chunk += " " + sentence
                        else:
                            temp_chunk = sentence
                        temp_tokens += sentence_tokens
                    else:
                        # Guardar el chunk temporal si existe
                        if temp_chunk:
                            chunks.append(temp_chunk)
                        temp_chunk = sentence
                        temp_tokens = sentence_tokens
                
                # Agregar el último chunk temporal si existe
                if temp_chunk:
                    chunks.append(temp_chunk)
            else:
                # Guardar el chunk actual y comenzar uno nuevo con el párrafo
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = paragraph
                current_tokens = paragraph_tokens
    
    # Agregar el último chunk si existe
    if current_chunk:
        chunks.append(current_chunk)
    
    # Limpiar chunks vacíos y normalizar
    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    
    return chunks

# NUEVO: Función para obtener el embedding de un texto usando la nueva API de OpenAI
def get_embedding(text, model="text-embedding-3-small", api_key=None):
    """
    Obtiene el embedding de un texto usando la API de OpenAI (nueva versión).
    Args:
        text (str): Texto a vectorizar.
        model (str): Modelo de embedding a usar.
        api_key (str, opcional): API key de OpenAI. Si no se pasa, se toma de la variable de entorno.
    Returns:
        list: Vector embedding del texto.
    """
    from openai import OpenAI
    import os
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")
    
    try:
        client = OpenAI(api_key=api_key)
        response = client.embeddings.create(
            model=model,
            input=[text]
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error obteniendo embedding: {e}")
        # Retornar un embedding vacío en caso de error
        return [0.0] * 1536  # Dimensiones del modelo text-embedding-3-small 