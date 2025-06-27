#!/usr/bin/env python3
"""
Sistema de actualización automática de la base de datos de Pinecone
Se ejecuta cada viernes a las 00:01 para procesar nueva información de Dropbox
"""

import os
import schedule
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
import dropbox
from pinecone import Pinecone
from extractor.text_chunker import chunk_text, get_embedding
from extractor.extractor_ocr import needs_ocr, extract_text_with_ocr_if_needed
from utils.text_extractor import extract_text_from_file

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_updater.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Configuración
DROPBOX_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
FOLDER_PATH = "/IA/PRUEBAS/Auditorías Vizum CNBV y anuales"

# Inicializar clientes
dbx = dropbox.Dropbox(DROPBOX_TOKEN)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

def is_supported_file(filename):
    """Verificar si el archivo es compatible"""
    return filename.endswith((".pdf", ".docx", ".txt", ".xlsx", ".csv", ".pptx", ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"))

def get_cliente_from_path(path):
    """Extraer nombre del cliente desde la ruta del archivo"""
    parts = path.strip("/").split("/")
    return parts[0] if parts else "desconocido"

def process_file(file_path):
    """Procesar un archivo individual"""
    logger.info(f"🔄 Procesando archivo: {file_path}")
    
    try:
        # Descargar archivo
        _, res = dbx.files_download(file_path)
        local_path = f"/tmp/{os.path.basename(file_path)}"
        
        with open(local_path, "wb") as f:
            f.write(res.content)
        
        # Extraer texto
        if needs_ocr(file_path):
            logger.info(f"🔍 Archivo {file_path} requiere OCR")
            text = extract_text_with_ocr_if_needed(local_path)
        else:
            text = extract_text_from_file(local_path)
        
        if not text.strip():
            logger.warning(f"⚠️ No se pudo extraer texto del archivo {file_path}")
            return False
        
        # Dividir en chunks
        chunks = chunk_text(text)
        cliente = get_cliente_from_path(file_path)
        
        # Subir chunks a Pinecone
        from uuid import uuid4
        for i, chunk in enumerate(chunks):
            try:
                embedding = get_embedding(chunk)
                index.upsert(vectors=[{
                    'id': str(uuid4()),
                    'values': embedding,
                    'metadata': {
                        "cliente": cliente,
                        "nombre_archivo": os.path.basename(file_path),
                        "ruta": file_path,
                        "chunk_index": i,
                        "texto": chunk,
                        "procesado_con_ocr": needs_ocr(file_path),
                        "fecha_procesamiento": datetime.now().isoformat(),
                        "tipo_actualizacion": "automatica"
                    }
                }])
            except Exception as e:
                logger.error(f"Error procesando chunk {i} de {file_path}: {e}")
        
        logger.info(f"✅ {file_path} procesado exitosamente ({len(chunks)} chunks)")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error procesando {file_path}: {e}")
        return False
    finally:
        # Limpiar archivo temporal
        if os.path.exists(local_path):
            os.remove(local_path)

def scan_for_new_files():
    """Escanear Dropbox en busca de archivos nuevos"""
    logger.info("🔍 Iniciando escaneo de archivos en Dropbox...")
    
    try:
        # Obtener lista de archivos en la carpeta
        result = dbx.files_list_folder(FOLDER_PATH, recursive=True)
        
        new_files = 0
        total_files = 0
        
        for entry in result.entries:
            if isinstance(entry, dropbox.files.FileMetadata) and is_supported_file(entry.path_lower):
                total_files += 1
                logger.info(f"📄 Procesando archivo: {entry.path_lower}")
                if process_file(entry.path_lower):
                    new_files += 1
        
        logger.info(f"📊 Resumen del escaneo:")
        logger.info(f"   - Total de archivos: {total_files}")
        logger.info(f"   - Archivos procesados: {new_files}")
        
        return new_files
        
    except Exception as e:
        logger.error(f"❌ Error escaneando Dropbox: {e}")
        return 0

def weekly_update():
    """Función principal de actualización semanal"""
    logger.info("🚀 Iniciando actualización semanal automática")
    logger.info(f"📅 Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Verificar conexión con Dropbox
        account = dbx.users_get_current_account()
        logger.info(f"👤 Conectado a Dropbox como: {account.name.display_name}")
        
        # Verificar conexión con Pinecone
        index_stats = index.describe_index_stats()
        logger.info(f"📊 Índice Pinecone: {index_stats.total_vector_count} vectores totales")
        
        # Escanear archivos nuevos
        new_files = scan_for_new_files()
        
        # Generar reporte
        report = f"""
📋 REPORTE DE ACTUALIZACIÓN SEMANAL
====================================
Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Archivos procesados: {new_files}
Estado: {'✅ Exitoso' if new_files >= 0 else '❌ Error'}
        """
        
        logger.info(report)
        
        # Guardar reporte en archivo
        with open(f"update_report_{datetime.now().strftime('%Y%m%d')}.txt", "w") as f:
            f.write(report)
        
        logger.info("🎉 Actualización semanal completada exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error en actualización semanal: {e}")

def test_update():
    """Función de prueba para verificar la configuración"""
    logger.info("🧪 Ejecutando prueba de actualización...")
    weekly_update()

def main():
    """Función principal del programa"""
    logger.info("🤖 Sistema de actualización automática iniciado")
    logger.info(f"📁 Carpeta monitoreada: {FOLDER_PATH}")
    logger.info("⏰ Programado para ejecutarse cada viernes a las 00:01")
    
    # Programar actualización semanal (viernes a las 00:01)
    schedule.every().friday.at("00:01").do(weekly_update)
    
    logger.info("🔄 Esperando próximas ejecuciones programadas...")
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Verificar cada minuto
        except KeyboardInterrupt:
            logger.info("🛑 Sistema detenido por el usuario")
            break
        except Exception as e:
            logger.error(f"❌ Error en el bucle principal: {e}")
            time.sleep(300)  # Esperar 5 minutos antes de reintentar

if __name__ == "__main__":
    # Verificar si se ejecuta como prueba
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_update()
    else:
        main()
