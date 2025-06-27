import os
import dropbox
from dotenv import load_dotenv
from extractor.text_chunker import chunk_text, get_embedding
from extractor.extractor_ocr import needs_ocr, extract_text_with_ocr_if_needed
from utils.text_extractor import extract_text_from_file
from pinecone import Pinecone
from uuid import uuid4
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

DROPBOX_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")
INDEX_NAME = "vizum-chieff"
FOLDER_PATH = "/IA/PRUEBAS/Auditorías Vizum CNBV y anuales"

# Inicializar Dropbox
dbx = dropbox.Dropbox(DROPBOX_TOKEN)

# Inicializar Pinecone (nueva API)
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENVIRONMENT"))
index = pc.Index(INDEX_NAME)

def is_supported_file(filename):
    # Incluir extensiones de imagen para OCR
    return filename.endswith((".pdf", ".docx", ".txt", ".xlsx", ".csv", ".pptx", ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"))

def get_cliente_from_path(path):
    parts = path.strip("/").split("/")
    return parts[0] if parts else "desconocido"

def process_file(path):
    _, res = dbx.files_download(path)
    local_path = f"/tmp/{os.path.basename(path)}"

    with open(local_path, "wb") as f:
        f.write(res.content)

    try:
        # Determinar si el archivo necesita OCR
        if needs_ocr(path):
            logger.info(f"🔍 Archivo {path} requiere OCR")
            text = extract_text_with_ocr_if_needed(local_path)
        else:
            # Procesar el archivo normalmente
            text = extract_text_from_file(local_path)
        
        if not text.strip():
            logger.warning(f"⚠️ No se pudo extraer texto del archivo {path}")
            return
            
        chunks = chunk_text(text)
        cliente = get_cliente_from_path(path)

        for i, chunk in enumerate(chunks):
            embedding = get_embedding(chunk)
            index.upsert(vectors=[{
                'id': str(uuid4()),
                'values': embedding,
                'metadata': {
                    "cliente": cliente,
                    "nombre_archivo": os.path.basename(path),
                    "ruta": path,
                    "chunk_index": i,
                    "texto": chunk,
                    "procesado_con_ocr": needs_ocr(path)
                }
            }])
        
        # Mensaje de confirmación
        if needs_ocr(path):
            print(f"✅ {path} procesado con OCR ({len(chunks)} chunks)")
        else:
            print(f"✅ {path} procesado ({len(chunks)} chunks)")
            
    except Exception as e:
        logger.error(f"Error procesando {path}: {str(e)}")
        print(f"⚠️ Error procesando {path}: {e}")
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)

def crawl_and_process_folder(folder_path=""):
    try:
        res = dbx.files_list_folder(folder_path, recursive=True)
        for entry in res.entries:
            if isinstance(entry, dropbox.files.FileMetadata) and is_supported_file(entry.path_lower):
                process_file(entry.path_lower)
    except Exception as e:
        logger.error(f"Error al recorrer Dropbox: {str(e)}")
        print(f"❌ Error al recorrer Dropbox: {e}")

if __name__ == "__main__":
    print(f"🚀 Iniciando procesamiento de archivos en: {FOLDER_PATH}")
    crawl_and_process_folder(FOLDER_PATH)
    print("✅ Procesamiento completado!") 