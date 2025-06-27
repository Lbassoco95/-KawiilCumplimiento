import pinecone
import os
from dotenv import load_dotenv

# Cargar variables de entorno
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Inicializa Pinecone antes de usarlo
pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment=os.getenv("PINECONE_ENVIRONMENT")
)

# Inicializar Pinecone
pc = pinecone.Index(os.getenv("PINECONE_INDEX_NAME"))
index_name = "vizum-chieff"

print(f"🔧 Corrigiendo índice de Pinecone: {index_name}")

try:
    # Verificar si el índice existe
    existing_indexes = {index.name: index for index in pinecone.list_indexes()}
    
    if index_name in existing_indexes:
        print(f"🗑️ Eliminando índice existente '{index_name}'...")
        pinecone.delete_index(index_name)
        print(f"✅ Índice '{index_name}' eliminado")
    
    # Crear nuevo índice con dimensión correcta
    print(f"🏗️ Creando nuevo índice '{index_name}' con dimensión 1536...")
    pinecone.create_index(
        name=index_name,
        dimension=1536,  # text-embedding-3-small dimension
        metric="cosine"
    )
    print(f"✅ Índice '{index_name}' creado exitosamente")
    
except Exception as e:
    print(f"❌ Error: {e}") 