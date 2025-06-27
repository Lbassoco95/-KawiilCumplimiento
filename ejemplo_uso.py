#!/usr/bin/env python3
"""
Ejemplo de uso del extractor de PDF
"""

from extractor.extractor_pdf import extract_text_from_pdf

def main():
    # Ruta al archivo PDF que quieres procesar
    ruta_pdf = "/Users/leopoldobassoconova/Downloads/Designación de persona responsable.pdf"
    
    try:
        # Extraer el texto del PDF
        texto = extract_text_from_pdf(ruta_pdf)
        
        # Imprimir el resultado
        print("=== TEXTO EXTRAÍDO DEL PDF ===")
        print(texto)
        print("=== FIN DEL TEXTO ===")
        
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ruta_pdf}")
    except Exception as e:
        print(f"Error al procesar el PDF: {e}")

if __name__ == "__main__":
    main() 