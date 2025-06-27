#!/usr/bin/env python3
"""
Ejemplo de uso del extractor de PowerPoint (.pptx)
"""

from extractor.extractor_pptx import extract_text_from_pptx

def main():
    # Ruta al archivo .pptx que quieres procesar
    # Cambia esta ruta por la de tu archivo .pptx
    ruta_pptx = "/Users/leopoldobassoconova/Downloads/ejemplo.pptx"
    
    try:
        # Extraer el texto del archivo .pptx
        texto = extract_text_from_pptx(ruta_pptx)
        
        # Imprimir el resultado
        print("=== TEXTO EXTRAÍDO DEL ARCHIVO .PPTX ===")
        print(texto)
        print("=== FIN DEL TEXTO ===")
        
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ruta_pptx}")
        print("Por favor, cambia la ruta en el script por la de tu archivo .pptx")
    except Exception as e:
        print(f"Error al procesar el archivo PowerPoint: {e}")

if __name__ == "__main__":
    main() 