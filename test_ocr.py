#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento del OCR
"""

import os
import sys
from dotenv import load_dotenv

# Agregar el directorio actual al path para importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extractor.extractor_ocr import (
    extract_text_from_image,
    extract_text_from_pdf_with_ocr,
    needs_ocr,
    extract_text_with_ocr_if_needed
)

def test_ocr_functions():
    """Prueba las funciones de OCR"""
    
    print("🧪 Probando funciones de OCR...")
    
    # Prueba 1: Verificar detección de archivos que necesitan OCR
    print("\n1. Probando detección de archivos que necesitan OCR:")
    
    test_files = [
        "documento.pdf",
        "imagen.jpg", 
        "foto.png",
        "archivo.docx",
        "datos.xlsx"
    ]
    
    for file in test_files:
        needs = needs_ocr(file)
        print(f"   {file}: {'🔍 Necesita OCR' if needs else '✅ No necesita OCR'}")
    
    # Prueba 2: Verificar que las funciones se pueden importar
    print("\n2. Verificando importaciones:")
    try:
        import pytesseract
        print("   ✅ pytesseract importado correctamente")
    except ImportError as e:
        print(f"   ❌ Error importando pytesseract: {e}")
    
    try:
        from PIL import Image
        print("   ✅ PIL importado correctamente")
    except ImportError as e:
        print(f"   ❌ Error importando PIL: {e}")
    
    try:
        import pdf2image
        print("   ✅ pdf2image importado correctamente")
    except ImportError as e:
        print(f"   ❌ Error importando pdf2image: {e}")
    
    # Prueba 3: Verificar que Tesseract está disponible
    print("\n3. Verificando instalación de Tesseract:")
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"   ✅ Tesseract versión: {version}")
    except Exception as e:
        print(f"   ❌ Error con Tesseract: {e}")
        print("   💡 Asegúrate de tener Tesseract instalado: brew install tesseract")
    
    print("\n✅ Pruebas de OCR completadas!")

if __name__ == "__main__":
    load_dotenv()
    test_ocr_functions() 