from dotenv import load_dotenv  # NUEVO: para cargar variables de entorno
import os
from openai import OpenAI  # NUEVO: importar OpenAI client
import pinecone  # type: ignore
from typing import List, Dict
import uuid
from datetime import datetime

# Cargar variables de entorno desde .env
load_dotenv()

def upload_chunks_to_pinecone(chunks: List[str], metadata: Dict) -> bool:
    """
    Sube chunks de texto a Pinecone usando embeddings de OpenAI.
    Args:
        chunks (List[str]): Lista de chunks de texto a procesar.
        metadata (Dict): Diccionario con metadatos (cliente, archivo, tipo, fecha).
    Returns:
        bool: True si la operación fue exitosa, False en caso contrario.
    """
    try:
        # Leer variables de entorno
        openai_api_key = os.getenv('OPENAI_API_KEY')
        pinecone_api_key = os.getenv('PINECONE_API_KEY')
        pinecone_environment = os.getenv('PINECONE_ENVIRONMENT')
        pinecone_index_name = os.getenv('PINECONE_INDEX_NAME', 'default-index')
        
        if not all([openai_api_key, pinecone_api_key, pinecone_environment]):
            print("Error: Faltan variables de entorno requeridas")
            print("OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_ENVIRONMENT")
            return False
        
        # Configurar OpenAI (nueva API)
        client = OpenAI(api_key=openai_api_key)
        
        # Configurar Pinecone (nueva API)
        pinecone.init(api_key=pinecone_api_key, environment=pinecone_environment)
        
        # Verificar si el índice existe y su dimensión
        existing_indexes = pinecone.list_indexes()
        if pinecone_index_name in existing_indexes:
            index_info = pinecone.describe_index(pinecone_index_name)
            if hasattr(index_info, 'dimension') and index_info.dimension != 1536:
                print(f"Eliminando índice '{pinecone_index_name}' con dimensión incorrecta ({index_info.dimension})...")
                pinecone.delete_index(pinecone_index_name)
                print(f"Índice '{pinecone_index_name}' eliminado.")
        
        # Crear el índice si no existe
        existing_indexes = pinecone.list_indexes()
        if pinecone_index_name not in existing_indexes:
            print(f"Creando índice: {pinecone_index_name}")
            pinecone.create_index(
                name=pinecone_index_name,
                dimension=1536,  # text-embedding-3-small dimension
                metric='cosine'
            )
        
        # Obtener el índice
        index = pinecone.Index(pinecone_index_name)
        
        # Generar embeddings para todos los chunks
        print(f"Generando embeddings para {len(chunks)} chunks...")
        
        # Usar text-embedding-3-small para generar embeddings (nueva API)
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=chunks
        )
        
        embeddings = response.data
        
        # Preparar vectores para Pinecone
        vectors = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            # Crear ID único para el vector
            vector_id = str(uuid.uuid4())
            
            # Preparar metadatos del vector
            vector_metadata = {
                'texto': chunk,  # Cambiado de 'text' a 'texto' para consistencia
                'chunk_index': i,
                'total_chunks': len(chunks),
                'cliente': metadata.get('cliente', ''),
                'archivo': metadata.get('archivo', ''),
                'tipo': metadata.get('tipo', ''),
                'fecha': metadata.get('fecha', datetime.now().isoformat()),
                'timestamp': datetime.now().isoformat()
            }
            
            # Crear vector para Pinecone (nueva API)
            vector = {
                'id': vector_id,
                'values': embedding.embedding,
                'metadata': vector_metadata
            }
            
            vectors.append(vector)
        
        # Subir vectores a Pinecone en lotes
        batch_size = 100  # Pinecone recomienda lotes de hasta 100 vectores
        total_uploaded = 0
        
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            print(f"Subiendo lote {i//batch_size + 1}/{(len(vectors) + batch_size - 1)//batch_size}...")
            
            # Usar namespace basado en cliente y tipo de archivo
            namespace = f"{metadata.get('cliente', 'default')}_{metadata.get('tipo', 'unknown')}"
            
            # Subir el lote a Pinecone (nueva API)
            index.upsert(vectors=batch, namespace=namespace)
            total_uploaded += len(batch)
        
        print(f"✅ Subidos exitosamente {total_uploaded} vectores a Pinecone")
        print(f"📁 Namespace: {namespace}")
        print(f"📊 Total de chunks procesados: {len(chunks)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al subir chunks a Pinecone: {str(e)}")
        return False

def query_pinecone(index, embedding, top_k=5, namespace=None):
    """
    Realiza una consulta semántica en Pinecone y devuelve los matches más relevantes.
    Args:
        index: Objeto de índice de Pinecone.
        embedding: Vector embedding de la consulta.
        top_k (int): Número de resultados a devolver.
        namespace (str, opcional): Namespace a consultar.
    Returns:
        dict: Resultados de la consulta (matches).
    """
    query_kwargs = {
        "vector": embedding,
        "top_k": top_k,
        "include_metadata": True
    }
    if namespace:
        query_kwargs["namespace"] = namespace
    return index.query(**query_kwargs) 