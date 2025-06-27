import pandas as pd  # type: ignore
import os
from typing import List

def extract_text_from_csv(path: str) -> str:
    """
    Extrae el texto de un archivo .csv, convirtiendo su contenido en texto legible.
    Args:
        path (str): Ruta al archivo .csv.
    Returns:
        str: Texto extraído del archivo CSV en formato tabla.
    """
    # Lista de encodings comunes a probar
    encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
    
    for encoding in encodings:
        try:
            # Intentar leer el archivo CSV con el encoding actual
            df = pd.read_csv(path, encoding=encoding, on_bad_lines='skip')
            
            # Convertir el DataFrame a texto
            rows = []
            
            # Agregar encabezados
            if not df.empty and len(df.columns) > 0:
                header = "\t".join(str(col) for col in df.columns)
                rows.append(header)
            
            # Agregar filas de datos
            for index, row in df.iterrows():
                # Convertir cada fila a texto con tabuladores como separadores
                row_text = "\t".join(str(cell) for cell in row)
                rows.append(row_text)
            
            # Unir todas las filas con saltos de línea
            full_text = "\n".join(rows)
            return full_text
            
        except UnicodeDecodeError:
            # Si hay error de codificación, continuar con el siguiente encoding
            continue
        except Exception as e:
            # Si hay otro tipo de error, intentar con el siguiente encoding
            continue
    
    # Si ningún encoding funcionó, devolver mensaje de error
    return f"Error: No se pudo leer el archivo CSV con ningún encoding disponible. Archivo: {path}" 