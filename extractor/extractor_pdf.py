import fitz  # type: ignore  # PyMuPDF
import re
from typing import List

def extract_text_from_pdf(path: str) -> str:
    """
    Extrae el texto de un archivo PDF, eliminando encabezados y pies de página repetitivos.
    Args:
        path (str): Ruta al archivo PDF.
    Returns:
        str: Texto extraído y limpio.
    """
    doc = fitz.open(path)
    pages_text = []
    header_candidates = {}
    footer_candidates = {}
    
    # Extraer texto de cada página y recolectar posibles encabezados/pies
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        lines = text.splitlines()
        if not lines:
            continue
        # Candidatos a encabezado y pie (primeras y últimas líneas)
        header = lines[0].strip()
        footer = lines[-1].strip()
        header_candidates[header] = header_candidates.get(header, 0) + 1
        footer_candidates[footer] = footer_candidates.get(footer, 0) + 1
        pages_text.append(lines)

    # Determinar encabezado y pie más repetidos
    header = max(header_candidates, key=lambda k: header_candidates[k]) if header_candidates else None
    footer = max(footer_candidates, key=lambda k: footer_candidates[k]) if footer_candidates else None

    # Limpiar encabezados y pies de página
    cleaned_pages = []
    for lines in pages_text:
        if header and lines and lines[0].strip() == header:
            lines = lines[1:]
        if footer and lines and lines and lines[-1].strip() == footer:
            lines = lines[:-1]
        cleaned_pages.append("\n".join(lines))

    # Unir todo el texto
    full_text = "\n".join(cleaned_pages)
    # Limpieza adicional: eliminar múltiples saltos de línea
    full_text = re.sub(r'\n{2,}', '\n\n', full_text)
    return full_text 