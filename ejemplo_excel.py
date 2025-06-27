#!/usr/bin/env python3
"""
Ejemplo de uso del extractor de Excel (.xlsx)
"""

from extractor.extractor_excel import extract_text_from_excel

def main():
    # Ruta al archivo .xlsx que quieres procesar
    # Cambia esta ruta por la de tu archivo .xlsx
    ruta_excel = "/Users/leopoldobassoconova/Downloads/ejemplo.xlsx"
    
    try:
        # Extraer el texto del archivo .xlsx
        texto = extract_text_from_excel(ruta_excel)
        
        # Imprimir el resultado
        print("=== TEXTO EXTRAÍDO DEL ARCHIVO .XLSX ===")
        print(texto)
        print("=== FIN DEL TEXTO ===")
        
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ruta_excel}")
        print("Por favor, cambia la ruta en el script por la de tu archivo .xlsx")
    except Exception as e:
        print(f"Error al procesar el archivo .xlsx: {e}")

if __name__ == "__main__":
    main() 