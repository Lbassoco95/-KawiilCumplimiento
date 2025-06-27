import os
import pytesseract
from PIL import Image
import pdf2image
import tempfile
from typing import List, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_image(image_path: str) -> str:
    """
    Extrae texto de una imagen usando OCR
    
    Args:
        image_path: Ruta al archivo de imagen
        
    Returns:
        Texto extraído de la imagen
    """
    try:
        # Abrir la imagen
        image = Image.open(image_path)
        
        # Extraer texto usando OCR
        text = pytesseract.image_to_string(image, lang='spa+eng')
        
        logger.info(f"Texto extraído de imagen {image_path}: {len(text)} caracteres")
        return text.strip()
        
    except Exception as e:
        logger.error(f"Error al procesar imagen {image_path}: {str(e)}")
        return ""

def extract_text_from_pdf_with_ocr(pdf_path: str) -> str:
    """
    Extrae texto de un PDF usando OCR (para PDFs escaneados)
    
    Args:
        pdf_path: Ruta al archivo PDF
        
    Returns:
        Texto extraído del PDF
    """
    try:
        # Convertir PDF a imágenes
        images = pdf2image.convert_from_path(pdf_path)
        
        all_text = []
        
        for i, image in enumerate(images):
            logger.info(f"Procesando página {i+1} del PDF {pdf_path}")
            
            # Extraer texto de la imagen usando OCR
            text = pytesseract.image_to_string(image, lang='spa+eng')
            all_text.append(text.strip())
        
        # Unir todo el texto
        full_text = "\n\n".join(all_text)
        
        logger.info(f"Texto extraído de PDF {pdf_path}: {len(full_text)} caracteres")
        return full_text
        
    except Exception as e:
        logger.error(f"Error al procesar PDF {pdf_path}: {str(e)}")
        return ""

def needs_ocr(file_path: str) -> bool:
    """
    Determina si un archivo necesita OCR basándose en su extensión
    
    Args:
        file_path: Ruta al archivo
        
    Returns:
        True si el archivo necesita OCR, False en caso contrario
    """
    # Extensiones que típicamente necesitan OCR
    ocr_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    
    # Obtener la extensión del archivo
    _, ext = os.path.splitext(file_path.lower())
    
    return ext in ocr_extensions

def extract_text_with_ocr_if_needed(file_path: str) -> str:
    """
    Extrae texto de un archivo, usando OCR si es necesario
    
    Args:
        file_path: Ruta al archivo
        
    Returns:
        Texto extraído del archivo
    """
    try:
        # Determinar si necesita OCR
        if needs_ocr(file_path):
            logger.info(f"Archivo {file_path} requiere OCR")
            return extract_text_from_image(file_path)
        
        # Para PDFs, intentar primero extracción normal, luego OCR si falla
        if file_path.lower().endswith('.pdf'):
            try:
                # Aquí podrías intentar extracción normal primero
                # Por ahora, asumimos que si es PDF y no se puede extraer texto normal, necesita OCR
                logger.info(f"Procesando PDF {file_path} con OCR")
                return extract_text_from_pdf_with_ocr(file_path)
            except Exception as e:
                logger.warning(f"Error en extracción normal de PDF {file_path}: {str(e)}")
                logger.info(f"Intentando OCR para PDF {file_path}")
                return extract_text_from_pdf_with_ocr(file_path)
        
        # Para otros archivos, no aplicamos OCR
        logger.info(f"Archivo {file_path} no requiere OCR")
        return ""
        
    except Exception as e:
        logger.error(f"Error al procesar archivo {file_path}: {str(e)}")
        return "" 