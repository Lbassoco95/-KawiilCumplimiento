#!/usr/bin/env python3
"""
Sistema de Enriquecimiento Automático de Metadatos
Usa OpenAI para analizar documentos y mejorar la información en Pinecone
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone
import re

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('metadata_enricher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MetadataEnricher:
    """Sistema de enriquecimiento automático de metadatos"""
    
    def __init__(self):
        load_dotenv()
        
        # Inicializar clientes
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index = self.pc.Index(os.getenv("PINECONE_INDEX_NAME"))
        
        # Configuración
        self.max_chunk_size = 4000  # Tamaño máximo para análisis
        self.batch_size = 10  # Procesar en lotes
        
    def analyze_document_content(self, text: str, filename: str, file_path: str) -> Dict[str, Any]:
        """Analizar contenido del documento usando OpenAI"""
        try:
            logger.info(f"🔍 Analizando documento: {filename}")
            
            # Truncar texto si es muy largo
            if len(text) > self.max_chunk_size:
                text = text[:self.max_chunk_size] + "..."
            
            prompt = f"""
            Analiza el siguiente documento de cumplimiento regulatorio y genera metadatos estructurados.
            
            Nombre del archivo: {filename}
            Ruta: {file_path}
            
            Contenido del documento:
            {text}
            
            Genera un JSON con la siguiente estructura:
            {{
                "tipo_documento": "Tipo específico del documento (ej: Ley, Reglamento, Manual, Política, etc.)",
                "categoria_regulatoria": "Categoría principal (ej: AML, KYC, Riesgo Operacional, etc.)",
                "entidad_regulatoria": "Entidad que emite o regula (ej: CNBV, SHCP, Banco de México, etc.)",
                "fecha_documento": "Fecha si se encuentra en el texto, o 'No especificada'",
                "nivel_importancia": "Alto/Medio/Bajo basado en el contenido",
                "resumen_executivo": "Resumen de 2-3 oraciones del contenido principal",
                "palabras_clave": ["palabra1", "palabra2", "palabra3", "palabra4", "palabra5"],
                "temas_principales": ["tema1", "tema2", "tema3"],
                "riesgos_identificados": ["riesgo1", "riesgo2"],
                "obligaciones_principales": ["obligacion1", "obligacion2"],
                "sanciones_mencionadas": ["sancion1", "sancion2"],
                "plazos_importantes": ["plazo1", "plazo2"],
                "entidades_mencionadas": ["entidad1", "entidad2"],
                "referencias_normativas": ["referencia1", "referencia2"],
                "nivel_tecnico": "Básico/Intermedio/Avanzado",
                "aplicabilidad": "General/Específica por sector/Específica por tamaño",
                "estado_vigencia": "Vigente/Obsoleto/En revisión"
            }}
            
            Responde SOLO con el JSON válido, sin texto adicional.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Eres un experto en análisis de documentos regulatorios y cumplimiento financiero. Genera metadatos precisos y estructurados."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            # Extraer JSON de la respuesta
            content = response.choices[0].message.content.strip()
            
            # Limpiar y parsear JSON
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                metadata = json.loads(json_match.group())
                logger.info(f"✅ Metadatos generados para {filename}")
                return metadata
            else:
                logger.error(f"❌ No se pudo extraer JSON de la respuesta para {filename}")
                return self._generate_fallback_metadata(filename, text)
                
        except Exception as e:
            logger.error(f"❌ Error analizando {filename}: {e}")
            return self._generate_fallback_metadata(filename, text)
    
    def _generate_fallback_metadata(self, filename: str, text: str) -> Dict[str, Any]:
        """Generar metadatos básicos en caso de error"""
        return {
            "tipo_documento": "Documento",
            "categoria_regulatoria": "General",
            "entidad_regulatoria": "No especificada",
            "fecha_documento": "No especificada",
            "nivel_importancia": "Medio",
            "resumen_executivo": f"Documento {filename} procesado automáticamente",
            "palabras_clave": ["documento", "regulatorio"],
            "temas_principales": ["cumplimiento"],
            "riesgos_identificados": [],
            "obligaciones_principales": [],
            "sanciones_mencionadas": [],
            "plazos_importantes": [],
            "entidades_mencionadas": [],
            "referencias_normativas": [],
            "nivel_tecnico": "Básico",
            "aplicabilidad": "General",
            "estado_vigencia": "Vigente"
        }
    
    def enrich_existing_vectors(self, folder_path: str = None):
        """Enriquecer metadatos de vectores existentes en Pinecone"""
        logger.info("🚀 Iniciando enriquecimiento de metadatos existentes...")
        
        try:
            # Obtener estadísticas del índice
            stats = self.index.describe_index_stats()
            total_vectors = stats.total_vector_count
            
            logger.info(f"📊 Total de vectores en Pinecone: {total_vectors}")
            
            # Obtener vectores en lotes
            batch_size = 100
            enriched_count = 0
            
            for offset in range(0, total_vectors, batch_size):
                try:
                    # Obtener vectores del índice
                    query_response = self.index.query(
                        vector=[0] * 1536,  # Vector dummy para obtener metadatos
                        top_k=batch_size,
                        include_metadata=True,
                        filter={}  # Sin filtros para obtener todos
                    )
                    
                    if not query_response.matches:
                        break
                    
                    # Procesar cada vector
                    for match in query_response.matches:
                        metadata = match.metadata
                        
                        # Verificar si ya tiene metadatos enriquecidos
                        if metadata.get("resumen_executivo") and metadata.get("categoria_regulatoria"):
                            continue
                        
                        # Obtener texto del vector
                        texto = metadata.get("texto", "")
                        if not texto or len(texto) < 50:
                            continue
                        
                        # Analizar y enriquecer
                        enriched_metadata = self.analyze_document_content(
                            texto,
                            metadata.get("nombre_archivo", "desconocido"),
                            metadata.get("ruta", "")
                        )
                        
                        # Combinar metadatos existentes con enriquecidos
                        updated_metadata = {**metadata, **enriched_metadata}
                        updated_metadata["metadata_enriquecido"] = True
                        updated_metadata["fecha_enriquecimiento"] = datetime.now().isoformat()
                        
                        # Actualizar vector en Pinecone
                        self.index.update(
                            id=match.id,
                            set_metadata=updated_metadata
                        )
                        
                        enriched_count += 1
                        logger.info(f"✅ Vector {match.id} enriquecido ({enriched_count})")
                        
                        # Rate limiting
                        if enriched_count % 10 == 0:
                            import time
                            time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"❌ Error procesando lote {offset}: {e}")
                    continue
            
            logger.info(f"🎉 Enriquecimiento completado: {enriched_count} vectores actualizados")
            
        except Exception as e:
            logger.error(f"❌ Error en enriquecimiento masivo: {e}")
    
    def enrich_new_document(self, text: str, filename: str, file_path: str, cliente: str) -> Dict[str, Any]:
        """Enriquecer metadatos de un documento nuevo antes de subirlo a Pinecone"""
        logger.info(f"🔍 Enriqueciendo documento nuevo: {filename}")
        
        # Analizar contenido
        enriched_metadata = self.analyze_document_content(text, filename, file_path)
        
        # Agregar metadatos adicionales
        enriched_metadata.update({
            "cliente": cliente,
            "nombre_archivo": filename,
            "ruta": file_path,
            "metadata_enriquecido": True,
            "fecha_enriquecimiento": datetime.now().isoformat(),
            "version_metadata": "2.0"
        })
        
        return enriched_metadata
    
    def generate_document_summary(self, text: str, filename: str) -> str:
        """Generar resumen ejecutivo del documento"""
        try:
            prompt = f"""
            Genera un resumen ejecutivo profesional del siguiente documento de cumplimiento regulatorio.
            
            Nombre del archivo: {filename}
            
            Contenido:
            {text[:3000]}  # Limitar a 3000 caracteres
            
            El resumen debe incluir:
            1. Objetivo principal del documento
            2. Entidades involucradas
            3. Obligaciones principales
            4. Plazos importantes (si los hay)
            5. Riesgos o sanciones mencionadas
            
            Formato: Párrafo profesional de 3-4 oraciones.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Eres un experto en cumplimiento regulatorio financiero. Genera resúmenes claros y profesionales."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"❌ Error generando resumen para {filename}: {e}")
            return f"Resumen no disponible para {filename}"
    
    def analyze_folder_structure(self, folder_path: str) -> Dict[str, Any]:
        """Analizar estructura de carpetas y generar insights"""
        logger.info(f"📁 Analizando estructura de carpeta: {folder_path}")
        
        try:
            from dropbox_auth_manager import get_dropbox_client
            dbx = get_dropbox_client()
            
            # Obtener lista de archivos
            result = dbx.files_list_folder(folder_path, recursive=True)
            
            file_types = {}
            total_files = 0
            total_size = 0
            
            for entry in result.entries:
                if hasattr(entry, 'size'):
                    total_files += 1
                    total_size += entry.size
                    
                    # Contar tipos de archivo
                    ext = os.path.splitext(entry.name)[1].lower()
                    file_types[ext] = file_types.get(ext, 0) + 1
            
            analysis = {
                "total_archivos": total_files,
                "tamaño_total_mb": round(total_size / (1024 * 1024), 2),
                "tipos_archivo": file_types,
                "carpeta_analizada": folder_path,
                "fecha_analisis": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Análisis de carpeta completado: {total_files} archivos")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error analizando carpeta {folder_path}: {e}")
            return {}
    
    def generate_folder_report(self, folder_path: str) -> str:
        """Generar reporte completo de una carpeta"""
        logger.info(f"📋 Generando reporte de carpeta: {folder_path}")
        
        try:
            # Analizar estructura
            analysis = self.analyze_folder_structure(folder_path)
            
            if not analysis:
                return "No se pudo generar el reporte"
            
            # Generar reporte con OpenAI
            prompt = f"""
            Genera un reporte ejecutivo de la siguiente carpeta de documentos regulatorios:
            
            Análisis de la carpeta:
            {json.dumps(analysis, indent=2, ensure_ascii=False)}
            
            El reporte debe incluir:
            1. Resumen ejecutivo de la carpeta
            2. Tipos de documentos predominantes
            3. Recomendaciones de organización
            4. Posibles mejoras en la estructura
            
            Formato: Reporte profesional de 4-5 párrafos.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Eres un consultor experto en gestión documental y cumplimiento regulatorio."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"❌ Error generando reporte: {e}")
            return f"Error generando reporte: {e}"

# Instancia global
metadata_enricher = MetadataEnricher()

def enrich_document_metadata(text: str, filename: str, file_path: str, cliente: str) -> Dict[str, Any]:
    """Función helper para enriquecer metadatos de un documento"""
    return metadata_enricher.enrich_new_document(text, filename, file_path, cliente)

def generate_document_summary(text: str, filename: str) -> str:
    """Función helper para generar resumen de documento"""
    return metadata_enricher.generate_document_summary(text, filename)

def enrich_existing_vectors():
    """Función helper para enriquecer vectores existentes"""
    metadata_enricher.enrich_existing_vectors()

def generate_folder_report(folder_path: str) -> str:
    """Función helper para generar reporte de carpeta"""
    return metadata_enricher.generate_folder_report(folder_path) 