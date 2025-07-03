#!/usr/bin/env python3
"""
Sistema de Análisis Inicial Completo de Documentos
Revisa todos los documentos existentes en Google Drive y los enriquece con metadatos
"""

import os
import sys
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional
from dotenv import load_dotenv
from google_drive_manager import get_google_drive_client
from metadata_enricher import enrich_document_metadata, generate_document_summary
from extractor.text_chunker import chunk_text, get_embedding
from extractor.extractor_ocr import needs_ocr, extract_text_with_ocr_if_needed
from utils.text_extractor import extract_text_from_file
from pinecone import Pinecone
from uuid import uuid4
import json
import tempfile

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('initial_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class InitialDocumentAnalyzer:
    """Sistema de análisis inicial completo de documentos"""
    
    def __init__(self):
        load_dotenv()
        
        # Inicializar clientes
        self.gdrive = get_google_drive_client()
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index = self.pc.Index(os.getenv("PINECONE_INDEX_NAME"))
        
        # Configuración
        self.folder_id = "1_yXImvvJNbj_hlqR67RInd9hoCLVyRfC"  # ID de la carpeta de Google Drive
        self.analysis_file = "document_analysis_status.json"
        self.supported_extensions = {".pdf", ".docx", ".txt", ".xlsx", ".csv", ".pptx", ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"}
        
        # Cargar estado de análisis previo
        self.analysis_status = self.load_analysis_status()
    
    def load_analysis_status(self) -> Dict:
        """Cargar estado de análisis previo"""
        try:
            if os.path.exists(self.analysis_file):
                with open(self.analysis_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error cargando estado de análisis: {e}")
        
        return {
            "last_analysis": None,
            "analyzed_files": {},
            "total_files": 0,
            "processed_files": 0,
            "failed_files": [],
            "analysis_start": None,
            "analysis_end": None
        }
    
    def save_analysis_status(self):
        """Guardar estado de análisis"""
        try:
            with open(self.analysis_file, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_status, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando estado de análisis: {e}")
    
    def get_file_hash(self, file_id: str) -> str:
        """Obtener hash del archivo para detectar cambios"""
        try:
            # Obtener metadatos del archivo usando Google Drive
            return self.gdrive.get_file_hash(file_id)
        except Exception as e:
            logger.error(f"Error obteniendo hash de {file_id}: {e}")
            return ""
    
    def is_file_modified(self, file_id: str) -> bool:
        """Verificar si el archivo ha sido modificado"""
        current_hash = self.get_file_hash(file_id)
        previous_hash = self.analysis_status["analyzed_files"].get(file_id, {}).get("hash", "")
        
        return current_hash != previous_hash
    
    def scan_all_documents(self) -> List[Dict]:
        """Escanear todos los documentos en la carpeta de Google Drive"""
        logger.info(f"🔍 Escaneando documentos en carpeta: {self.folder_id}")
        
        try:
            # Obtener lista de archivos usando Google Drive
            files = self.gdrive.list_files_in_folder(self.folder_id)
            
            all_files = []
            for file in files:
                file_info = {
                    "id": file["id"],
                    "path": file["path"],
                    "name": file["name"],
                    "size": file["size"],
                    "modified": file["modified_time"],
                    "hash": self.get_file_hash(file["id"]),
                    "needs_analysis": True
                }
                all_files.append(file_info)
            
            logger.info(f"📊 Total de archivos encontrados: {len(all_files)}")
            return all_files
            
        except Exception as e:
            logger.error(f"Error escaneando documentos: {e}")
            return []
    
    def determine_analysis_needs(self, files: List[Dict]) -> List[Dict]:
        """Determinar qué archivos necesitan análisis"""
        logger.info("🔍 Determinando archivos que necesitan análisis...")
        
        files_to_analyze = []
        
        for file_info in files:
            file_id = file_info["id"]
            
            # Verificar si el archivo ya fue analizado
            if file_id in self.analysis_status["analyzed_files"]:
                previous_info = self.analysis_status["analyzed_files"][file_id]
                
                # Verificar si ha sido modificado
                if self.is_file_modified(file_id):
                    logger.info(f"📝 Archivo modificado: {file_info['name']}")
                    file_info["needs_analysis"] = True
                    file_info["reason"] = "modified"
                    files_to_analyze.append(file_info)
                else:
                    logger.info(f"✅ Archivo sin cambios: {file_info['name']}")
                    file_info["needs_analysis"] = False
                    file_info["reason"] = "no_changes"
            else:
                logger.info(f"🆕 Nuevo archivo: {file_info['name']}")
                file_info["needs_analysis"] = True
                file_info["reason"] = "new"
                files_to_analyze.append(file_info)
        
        logger.info(f"📊 Archivos que necesitan análisis: {len(files_to_analyze)}")
        return files_to_analyze
    
    def process_document(self, file_info: Dict) -> bool:
        """Procesar un documento individual"""
        file_id = file_info["id"]
        file_name = file_info["name"]
        
        logger.info(f"🔄 Procesando: {file_name}")
        
        try:
            # Descargar archivo usando Google Drive
            tmp_file_path = self.gdrive.download_file(file_id, file_name)
            
            if not tmp_file_path:
                logger.error(f"❌ No se pudo descargar: {file_name}")
                return False
            
            # Extraer texto
            if needs_ocr(tmp_file_path):
                logger.info(f"🔍 Aplicando OCR a: {file_name}")
                text = extract_text_with_ocr_if_needed(tmp_file_path)
            else:
                text = extract_text_from_file(tmp_file_path)
            
            if not text.strip():
                logger.warning(f"⚠️ No se pudo extraer texto de: {file_name}")
                self.analysis_status["failed_files"].append({
                    "id": file_id,
                    "name": file_name,
                    "error": "No se pudo extraer texto",
                    "date": datetime.now().isoformat()
                })
                return False
            
            # Generar resumen ejecutivo
            logger.info(f"📝 Generando resumen para: {file_name}")
            resumen_ejecutivo = generate_document_summary(text, file_name)
            
            # Enriquecer metadatos
            logger.info(f"🔍 Enriqueciendo metadatos para: {file_name}")
            cliente = self.get_cliente_from_path(file_path)
            enriched_metadata = enrich_document_metadata(text, file_name, file_path, cliente)
            
            # Dividir en chunks y subir a Pinecone
            chunks = chunk_text(text)
            logger.info(f"📊 Dividiendo en {len(chunks)} chunks: {file_name}")
            
            for i, chunk in enumerate(chunks):
                try:
                    embedding = get_embedding(chunk)
                    
                    # Combinar metadatos
                    chunk_metadata = {
                        "cliente": cliente,
                        "nombre_archivo": file_name,
                        "ruta": file_info["path"],
                        "file_id": file_id,
                        "chunk_index": i,
                        "texto": chunk,
                        "procesado_con_ocr": needs_ocr(tmp_file_path),
                        "fecha_procesamiento": datetime.now().isoformat(),
                        "tipo_actualizacion": "analisis_inicial",
                        "resumen_ejecutivo_documento": resumen_ejecutivo,
                        "total_chunks": len(chunks),
                        "chunk_actual": i + 1,
                        "hash_archivo": file_info["hash"],
                        "fecha_modificacion": file_info["modified"]
                    }
                    
                    # Agregar metadatos enriquecidos
                    chunk_metadata.update(enriched_metadata)
                    
                    # Subir a Pinecone
                    self.index.upsert(vectors=[{
                        'id': str(uuid4()),
                        'values': embedding,
                        'metadata': chunk_metadata
                    }])
                    
                except Exception as e:
                    logger.error(f"Error procesando chunk {i} de {file_name}: {e}")
            
            # Actualizar estado de análisis
            self.analysis_status["analyzed_files"][file_id] = {
                "name": file_name,
                "hash": file_info["hash"],
                "size": file_info["size"],
                "modified": file_info["modified"],
                "analyzed_date": datetime.now().isoformat(),
                "chunks_created": len(chunks),
                "status": "success"
            }
            
            # Limpiar archivo temporal
            os.unlink(tmp_file_path)
            
            logger.info(f"✅ Procesado exitosamente: {file_name} ({len(chunks)} chunks)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error procesando {file_name}: {e}")
            self.analysis_status["failed_files"].append({
                "id": file_id,
                "name": file_name,
                "error": str(e),
                "date": datetime.now().isoformat()
            })
            return False
    
    def get_cliente_from_path(self, path: str) -> str:
        """Extraer nombre del cliente desde la ruta"""
        # Para Google Drive, usar el nombre del archivo como indicador
        # En el futuro se puede mejorar para usar estructura de carpetas
        return "Google Drive"
    
    def run_initial_analysis(self, force_full: bool = False):
        """Ejecutar análisis inicial completo"""
        logger.info("🚀 INICIANDO ANÁLISIS INICIAL COMPLETO DE DOCUMENTOS")
        logger.info("=" * 60)
        
        # Actualizar estado
        self.analysis_status["analysis_start"] = datetime.now().isoformat()
        self.analysis_status["total_files"] = 0
        self.analysis_status["processed_files"] = 0
        
        try:
            # Escanear todos los documentos
            all_files = self.scan_all_documents()
            self.analysis_status["total_files"] = len(all_files)
            
            if force_full:
                logger.info("🔄 Modo forzado: Analizando todos los archivos")
                files_to_analyze = all_files
                for file_info in files_to_analyze:
                    file_info["needs_analysis"] = True
                    file_info["reason"] = "forced"
            else:
                # Determinar qué archivos necesitan análisis
                files_to_analyze = self.determine_analysis_needs(all_files)
            
            if not files_to_analyze:
                logger.info("✅ No hay archivos que necesiten análisis")
                return
            
            logger.info(f"📊 Archivos a procesar: {len(files_to_analyze)}")
            
            # Procesar archivos
            for i, file_info in enumerate(files_to_analyze, 1):
                logger.info(f"📋 Progreso: {i}/{len(files_to_analyze)}")
                
                if self.process_document(file_info):
                    self.analysis_status["processed_files"] += 1
                
                # Guardar estado cada 10 archivos
                if i % 10 == 0:
                    self.save_analysis_status()
                    logger.info(f"💾 Estado guardado - Procesados: {i}/{len(files_to_analyze)}")
            
            # Finalizar análisis
            self.analysis_status["analysis_end"] = datetime.now().isoformat()
            self.analysis_status["last_analysis"] = datetime.now().isoformat()
            self.save_analysis_status()
            
            # Generar reporte
            self.generate_analysis_report()
            
            logger.info("🎉 ANÁLISIS INICIAL COMPLETADO")
            
        except Exception as e:
            logger.error(f"❌ Error en análisis inicial: {e}")
            self.analysis_status["analysis_end"] = datetime.now().isoformat()
            self.save_analysis_status()
    
    def generate_analysis_report(self):
        """Generar reporte del análisis inicial"""
        try:
            start_time = datetime.fromisoformat(self.analysis_status["analysis_start"])
            end_time = datetime.fromisoformat(self.analysis_status["analysis_end"])
            duration = end_time - start_time
            
            report = f"""
📊 REPORTE DE ANÁLISIS INICIAL COMPLETO
==========================================
Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Duración: {duration}

📁 ESTADÍSTICAS GENERALES:
• Total de archivos escaneados: {self.analysis_status['total_files']}
• Archivos procesados: {self.analysis_status['processed_files']}
• Archivos fallidos: {len(self.analysis_status['failed_files'])}

📈 RESULTADOS:
• Tasa de éxito: {(self.analysis_status['processed_files'] / max(self.analysis_status['total_files'], 1)) * 100:.1f}%
• Tiempo promedio por archivo: {duration / max(self.analysis_status['processed_files'], 1)} si se procesaron archivos

🔍 ARCHIVOS FALLIDOS:
"""
            
            for failed_file in self.analysis_status["failed_files"]:
                report += f"• {failed_file['name']}: {failed_file['error']}\n"
            
            report += f"""
✅ ESTADO DEL SISTEMA:
• Análisis inicial: COMPLETADO
• Metadatos enriquecidos: ACTIVADO
• Base de datos Pinecone: ACTUALIZADA
• Próximo análisis semanal: PROGRAMADO

🎯 PRÓXIMOS PASOS:
1. Verificar en Slack con: /estado
2. Probar búsquedas con: /cumplimiento [consulta]
3. Monitorear logs: tail -f initial_analysis.log
"""
            
            # Guardar reporte
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"reporte_analisis_inicial_{timestamp}.txt"
            
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info(f"📄 Reporte guardado: {report_filename}")
            print(report)
            
        except Exception as e:
            logger.error(f"Error generando reporte: {e}")
    
    def check_weekly_updates(self):
        """Verificar actualizaciones semanales"""
        logger.info("📅 Verificando actualizaciones semanales...")
        
        # Verificar si es necesario hacer análisis semanal
        last_analysis = self.analysis_status.get("last_analysis")
        if last_analysis:
            last_date = datetime.fromisoformat(last_analysis)
            days_since = (datetime.now() - last_date).days
            
            if days_since < 7:
                logger.info(f"⏰ Último análisis hace {days_since} días. Análisis semanal no necesario.")
                return
        
        logger.info("🔄 Ejecutando análisis semanal...")
        self.run_initial_analysis(force_full=False)

def main():
    """Función principal"""
    print("🔍 Sistema de Análisis Inicial de Documentos")
    print("=" * 50)
    
    analyzer = InitialDocumentAnalyzer()
    
    print("\n📋 Opciones disponibles:")
    print("1. Análisis inicial completo (todos los archivos)")
    print("2. Análisis incremental (solo archivos nuevos/modificados)")
    print("3. Verificar estado de análisis")
    print("4. Análisis semanal automático")
    
    try:
        option = input("\nSelecciona una opción (1-4): ").strip()
        
        if option == "1":
            print("\n🚀 Iniciando análisis inicial completo...")
            print("⚠️ Esto puede tomar tiempo dependiendo del número de archivos")
            
            confirm = input("¿Continuar? (s/n): ").lower()
            if confirm == 's':
                analyzer.run_initial_analysis(force_full=True)
            else:
                print("❌ Análisis cancelado")
        
        elif option == "2":
            print("\n🔄 Iniciando análisis incremental...")
            analyzer.run_initial_analysis(force_full=False)
        
        elif option == "3":
            print("\n📊 Estado del análisis:")
            status = analyzer.analysis_status
            print(f"• Último análisis: {status.get('last_analysis', 'Nunca')}")
            print(f"• Archivos analizados: {len(status.get('analyzed_files', {}))}")
            print(f"• Archivos fallidos: {len(status.get('failed_files', []))}")
            print(f"• Total procesados: {status.get('processed_files', 0)}")
        
        elif option == "4":
            print("\n📅 Ejecutando análisis semanal...")
            analyzer.check_weekly_updates()
        
        else:
            print("❌ Opción no válida")
    
    except KeyboardInterrupt:
        print("\n❌ Análisis cancelado por el usuario")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 