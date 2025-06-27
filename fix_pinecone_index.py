import os
from dotenv import load_dotenv
from pinecone import Pinecone

# Cargar variables de entorno
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Inicializar Pinecone con la nueva sintaxis
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = "vizum-chieff"

print(f"🔧 Corrigiendo índice de Pinecone: {index_name}")

try:
    # Verificar si el índice existe
    existing_indexes = pc.list_indexes().names()
    
    if index_name in existing_indexes:
        print(f"🗑️ Eliminando índice existente '{index_name}'...")
        pc.delete_index(index_name)
        print(f"✅ Índice '{index_name}' eliminado")
    
    # Crear nuevo índice con dimensión correcta
    print(f"🏗️ Creando nuevo índice '{index_name}' con dimensión 1536...")
    pc.create_index(
        name=index_name,
        dimension=1536,  # text-embedding-3-small dimension
        metric="cosine"
    )
    print(f"✅ Índice '{index_name}' creado exitosamente")
    
except Exception as e:
    print(f"❌ Error: {e}") 