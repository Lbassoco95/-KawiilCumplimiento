#!/usr/bin/env python3
"""
Ejemplo de uso del extractor de CSV (.csv)
"""

from extractor.extractor_csv import extract_text_from_csv

def main():
    # Ruta al archivo .csv que quieres procesar
    # Cambia esta ruta por la de tu archivo .csv
    ruta_csv = "/Users/leopoldobassoconova/Downloads/ejemplo.csv"
    
    try:
        # Extraer el texto del archivo .csv
        texto = extract_text_from_csv(ruta_csv)
        
        # Imprimir el resultado
        print("=== TEXTO EXTRAÍDO DEL ARCHIVO .CSV ===")
        print(texto)
        print("=== FIN DEL TEXTO ===")
        
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ruta_csv}")
        print("Por favor, cambia la ruta en el script por la de tu archivo .csv")
    except Exception as e:
        print(f"Error al procesar el archivo .csv: {e}")

if __name__ == "__main__":
    main() 