from docx import Document  # type: ignore
import re
from typing import List

def extract_text_from_word(path: str) -> str:
    """
    Extrae el texto de un archivo .docx, eliminando saltos de línea innecesarios.
    Args:
        path (str): Ruta al archivo .docx.
    Returns:
        str: Texto extraído y limpio.
    """
    doc = Document(path)
    paragraphs = []
    
    # Extraer texto de cada párrafo
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if text:  # Solo agregar párrafos que no estén vacíos
            paragraphs.append(text)
    
    # Unir todos los párrafos
    full_text = "\n".join(paragraphs)
    
    # Limpiar saltos de línea innecesarios
    # Reemplazar múltiples saltos de línea con uno solo
    full_text = re.sub(r'\n{2,}', '\n\n', full_text)
    
    # Eliminar espacios en blanco al inicio y final
    full_text = full_text.strip()
    
    return full_text 