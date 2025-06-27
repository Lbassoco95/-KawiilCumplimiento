#!/usr/bin/env python3
"""
Ejemplo de uso del extractor de Word (.docx)
"""

from extractor.extractor_word import extract_text_from_word

def main():
    # Ruta al archivo .docx que quieres procesar
    # Cambia esta ruta por la de tu archivo .docx
    ruta_docx = "/Users/leopoldobassoconova/Downloads/ejemplo.docx"
    
    try:
        # Extraer el texto del archivo .docx
        texto = extract_text_from_word(ruta_docx)
        
        # Imprimir el resultado
        print("=== TEXTO EXTRAÍDO DEL ARCHIVO .DOCX ===")
        print(texto)
        print("=== FIN DEL TEXTO ===")
        
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ruta_docx}")
        print("Por favor, cambia la ruta en el script por la de tu archivo .docx")
    except Exception as e:
        print(f"Error al procesar el archivo .docx: {e}")

if __name__ == "__main__":
    main() 