import pandas as pd  # type: ignore
import os
from typing import List

def extract_text_from_excel(path: str) -> str:
    """
    Extrae el texto de un archivo .xlsx, recorriendo todas sus hojas y convirtiendo el contenido en texto.
    Args:
        path (str): Ruta al archivo .xlsx.
    Returns:
        str: Texto extraído de todas las hojas del Excel.
    """
    try:
        # Leer todas las hojas del archivo Excel
        excel_file = pd.ExcelFile(path, engine='openpyxl')
        all_text = []
        
        # Recorrer cada hoja
        for sheet_name in excel_file.sheet_names:
            try:
                # Leer la hoja actual
                df = pd.read_excel(path, sheet_name=sheet_name, header=None, na_filter=False)
                
                # Agregar el nombre de la hoja como título
                sheet_text = [f"=== HOJA: {sheet_name} ==="]
                
                # Convertir el DataFrame a texto
                for index, row in df.iterrows():
                    # Convertir cada fila a texto con tabuladores como separadores
                    row_text = "\t".join(str(cell) for cell in row)
                    if row_text.strip():  # Solo agregar filas que no estén vacías
                        sheet_text.append(row_text)
                
                # Agregar un separador entre hojas
                sheet_text.append("")  # Línea en blanco
                all_text.extend(sheet_text)
                
            except Exception as e:
                # Si hay error en una hoja específica, continuar con la siguiente
                error_msg = f"Error al procesar la hoja '{sheet_name}': {str(e)}"
                all_text.append(error_msg)
                continue
        
        # Unir todo el texto
        full_text = "\n".join(all_text)
        return full_text
        
    except Exception as e:
        return f"Error al leer el archivo Excel: {str(e)}" 