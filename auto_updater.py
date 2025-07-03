#!/usr/bin/env python3
"""
Sistema de actualización automática de la base de datos de Pinecone
Se ejecuta cada viernes a las 00:01 para procesar nueva información de Dropbox
Integrado con análisis inicial completo y seguimiento semanal
"""

import os
import schedule
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
from pinecone import Pinecone
from extractor.text_chunker import chunk_text, get_embedding
from extractor.extractor_ocr import needs_ocr, extract_text_with_ocr_if_needed
from utils.text_extractor import extract_text_from_file
from uuid import uuid4
from typing import Optional
from dropbox_auth_manager import get_dropbox_client, test_dropbox_connection
from metadata_enricher import enrich_document_metadata, generate_document_summary
from initial_document_analysis import InitialDocumentAnalyzer
from weekly_document_monitor import WeeklyDocumentMonitor

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
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
# Configuración de carpetas múltiples
FOLDER_PATHS = [
    "/Leopoldo Bassoco Nova/IA/PRUEBAS/VIZUM TECHNOLOGIES",
    "/IA/PRUEBAS/Auditorías Vizum CNBV y anuales",
    "/Leopoldo Bassoco Nova/IA/PRUEBAS/VIZUM TECHNOLOGIES/Auditorías",
    "/Leopoldo Bassoco Nova/IA/PRUEBAS/VIZUM TECHNOLOGIES/Regulaciones",
    "/Leopoldo Bassoco Nova/IA/PRUEBAS/VIZUM TECHNOLOGIES/Compliance",
    "/Leopoldo Bassoco Nova/IA/PRUEBAS/VIZUM TECHNOLOGIES/Documentos",
    "/Leopoldo Bassoco Nova/IA/PRUEBAS/VIZUM TECHNOLOGIES/Reportes",
    "/Leopoldo Bassoco Nova/IA/PRUEBAS/VIZUM TECHNOLOGIES/Manuales",
    "/Leopoldo Bassoco Nova/IA/PRUEBAS/VIZUM TECHNOLOGIES/Políticas",
    "/Leopoldo Bassoco Nova/IA/PRUEBAS/VIZUM TECHNOLOGIES/Procedimientos"
]

# Carpeta principal para compatibilidad
FOLDER_PATH = "/Leopoldo Bassoco Nova/IA/PRUEBAS/VIZUM TECHNOLOGIES"

# Inicializar Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

# Inicializar analizadores
initial_analyzer = InitialDocumentAnalyzer()
weekly_monitor = WeeklyDocumentMonitor()

def is_supported_file(filename):
    """Verificar si el archivo es compatible"""
    return filename.endswith((".pdf", ".docx", ".txt", ".xlsx", ".csv", ".pptx", ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"))

def get_cliente_from_path(path):
    """Extraer nombre del cliente desde la ruta del archivo"""
    parts = path.strip("/").split("/")
    return parts[0] if parts else "desconocido"

def process_file(file_path):
    """Procesar un archivo individual con enriquecimiento de metadatos"""
    logger.info(f"🔄 Procesando archivo: {file_path}")
    
    try:
        # Obtener cliente de Dropbox válido
        dbx = get_dropbox_client()
        
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
        
        # Generar resumen ejecutivo del documento completo
        filename = os.path.basename(file_path)
        logger.info(f"📝 Generando resumen ejecutivo para {filename}")
        resumen_ejecutivo = generate_document_summary(text, filename)
        
        # Dividir en chunks
        chunks = chunk_text(text)
        cliente = get_cliente_from_path(file_path)
        
        # Enriquecer metadatos del documento
        logger.info(f"🔍 Enriqueciendo metadatos para {filename}")
        enriched_metadata = enrich_document_metadata(text, filename, file_path, cliente)
        
        # Subir chunks a Pinecone con metadatos enriquecidos
        for i, chunk in enumerate(chunks):
            try:
                embedding = get_embedding(chunk)
                
                # Combinar metadatos básicos con enriquecidos
                chunk_metadata = {
                    "cliente": cliente,
                    "nombre_archivo": filename,
                    "ruta": file_path,
                    "chunk_index": i,
                    "texto": chunk,
                    "procesado_con_ocr": needs_ocr(file_path),
                    "fecha_procesamiento": datetime.now().isoformat(),
                    "tipo_actualizacion": "automatica",
                    "resumen_ejecutivo_documento": resumen_ejecutivo,
                    "total_chunks": len(chunks),
                    "chunk_actual": i + 1
                }
                
                # Agregar metadatos enriquecidos
                chunk_metadata.update(enriched_metadata)
                
                index.upsert(vectors=[{
                    'id': str(uuid4()),
                    'values': embedding,
                    'metadata': chunk_metadata
                }])
                
                logger.info(f"✅ Chunk {i+1}/{len(chunks)} de {filename} procesado con metadatos enriquecidos")
                
            except Exception as e:
                logger.error(f"Error procesando chunk {i} de {file_path}: {e}")
        
        logger.info(f"✅ {file_path} procesado exitosamente ({len(chunks)} chunks con metadatos enriquecidos)")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error procesando {file_path}: {e}")
        return False
    finally:
        # Limpiar archivo temporal
        if os.path.exists(local_path):
            os.remove(local_path)

def scan_for_new_files():
    """Escanear múltiples carpetas de Dropbox en busca de archivos nuevos"""
    logger.info("🔍 Iniciando escaneo de archivos en múltiples carpetas de Dropbox...")
    
    try:
        # Obtener cliente de Dropbox válido
        dbx = get_dropbox_client()
        
        total_files = 0
        processed_files = 0
        
        # Escanear cada carpeta configurada
        for folder_path in FOLDER_PATHS:
            try:
                logger.info(f"📁 Escaneando carpeta: {folder_path}")
                
                # Obtener lista de archivos en la carpeta
                result = dbx.files_list_folder(folder_path, recursive=True)
                
                for entry in result.entries:
                    if isinstance(entry, dropbox.files.FileMetadata) and is_supported_file(entry.path_lower):
                        total_files += 1
                        logger.info(f"📄 Procesando archivo: {entry.path_lower}")
                        if process_file(entry.path_lower):
                            processed_files += 1
                            
            except dropbox.exceptions.ApiError as e:
                if e.error.is_path():
                    logger.warning(f"⚠️ Carpeta no encontrada: {folder_path}")
                else:
                    logger.error(f"❌ Error accediendo a {folder_path}: {e}")
            except Exception as e:
                logger.error(f"❌ Error escaneando {folder_path}: {e}")
        
        logger.info(f"📊 Resumen del escaneo múltiple:")
        logger.info(f"   - Carpetas escaneadas: {len(FOLDER_PATHS)}")
        logger.info(f"   - Total de archivos encontrados: {total_files}")
        logger.info(f"   - Archivos procesados exitosamente: {processed_files}")
        
        return processed_files
        
    except Exception as e:
        logger.error(f"❌ Error en escaneo múltiple: {e}")
        return 0
def weekly_update():
    """Función principal de actualización semanal con análisis completo"""
    logger.info("🚀 Iniciando actualización semanal automática")
    logger.info(f"📅 Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Verificar conexión con Dropbox
        if not test_dropbox_connection():
            logger.error("❌ No se pudo conectar a Dropbox")
            return
        
        # Verificar conexión con Pinecone
        index_stats = index.describe_index_stats()
        logger.info(f"📊 Índice Pinecone: {index_stats.total_vector_count} vectores totales")
        
        # Ejecutar análisis semanal completo
        logger.info("🔄 Ejecutando análisis semanal completo...")
        initial_analyzer.run_initial_analysis(force_full=False)
        
        # Generar reporte semanal
        logger.info("📄 Generando reporte semanal...")
        weekly_report = weekly_monitor.generate_weekly_report()
        
        # Generar reporte adicional
        report = f"""
📋 REPORTE DE ACTUALIZACIÓN SEMANAL
====================================
Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Vectores en Pinecone: {index_stats.total_vector_count}
Metadatos enriquecidos: ✅ Activado
Análisis semanal: ✅ Completado
Estado: ✅ Exitoso

{weekly_report}
        """
        
        logger.info(report)
        
        # Guardar reporte en archivo
        with open(f"update_report_{datetime.now().strftime('%Y%m%d')}.txt", "w") as f:
            f.write(report)
        
        logger.info("🎉 Actualización semanal completada exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error en actualización semanal: {e}")

def initial_complete_analysis():
    """Ejecutar análisis inicial completo de todos los documentos"""
    logger.info("🔍 INICIANDO ANÁLISIS INICIAL COMPLETO")
    logger.info("=" * 50)
    
    try:
        # Verificar conexiones
        if not test_dropbox_connection():
            logger.error("❌ No se pudo conectar a Dropbox")
            return
        
        # Ejecutar análisis inicial completo
        initial_analyzer.run_initial_analysis(force_full=True)
        
        logger.info("🎉 Análisis inicial completo finalizado")
        
    except Exception as e:
        logger.error(f"❌ Error en análisis inicial: {e}")

def test_update():
    """Función de prueba para verificar la configuración"""
    logger.info("🧪 Ejecutando prueba de actualización...")
    weekly_update()

def start_monitoring():
    """Iniciar monitoreo automático"""
    logger.info("🚀 Iniciando monitoreo automático del sistema")
    
    # Verificar si es la primera ejecución
    if not initial_analyzer.analysis_status.get("last_analysis"):
        logger.info("🆕 Primera ejecución detectada - Iniciando análisis inicial completo")
        initial_complete_analysis()
    
    # Programar actualizaciones semanales
    schedule.every().friday.at("00:01").do(weekly_update)
    
    # Programar verificación diaria de estado
    schedule.every().day.at("09:00").do(weekly_monitor.daily_status_check)
    
    logger.info("✅ Monitoreo programado:")
    logger.info("   📅 Actualización semanal: Viernes 00:01")
    logger.info("   📊 Verificación diaria: 09:00")
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Verificar cada minuto
        except KeyboardInterrupt:
            logger.info("🛑 Monitoreo detenido por el usuario")
            break
        except Exception as e:
            logger.error(f"❌ Error en el bucle principal: {e}")
            time.sleep(300)  # Esperar 5 minutos antes de reintentar

def main():
    """Función principal del programa"""
    logger.info("🤖 Sistema de actualización automática iniciado")
    logger.info(f"📁 Carpeta monitoreada: {FOLDER_PATH}")
    logger.info("⏰ Programado para ejecutarse cada viernes a las 00:01")
    logger.info("🔍 Enriquecimiento de metadatos: ✅ Activado")
    logger.info("📅 Análisis inicial completo: ✅ Disponible")
    logger.info("🔄 Seguimiento semanal: ✅ Activado")
    
    # Verificar conexión inicial
    if not test_dropbox_connection():
        logger.error("❌ No se pudo conectar a Dropbox. Verifica la configuración.")
        return
    
    # Mostrar opciones
    print("\n📋 Opciones disponibles:")
    print("1. Iniciar monitoreo automático (recomendado)")
    print("2. Ejecutar análisis inicial completo")
    print("3. Ejecutar actualización semanal manual")
    print("4. Prueba de configuración")
    print("5. Verificar estado del sistema")
    
    try:
        option = input("\nSelecciona una opción (1-5): ").strip()
        
        if option == "1":
            print("\n🚀 Iniciando monitoreo automático...")
            start_monitoring()
        
        elif option == "2":
            print("\n🔍 Ejecutando análisis inicial completo...")
            initial_complete_analysis()
        
        elif option == "3":
            print("\n🔄 Ejecutando actualización semanal manual...")
            weekly_update()
        
        elif option == "4":
            print("\n🧪 Ejecutando prueba de configuración...")
            test_update()
        
        elif option == "5":
            print("\n📊 Verificando estado del sistema...")
            weekly_monitor.daily_status_check()
        
        else:
            print("❌ Opción no válida")
    
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada por el usuario")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
