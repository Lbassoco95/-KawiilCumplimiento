import os
from extractor.extractor_pdf import extract_text_from_pdf
from extractor.extractor_word import extract_text_from_word
from extractor.extractor_excel import extract_text_from_excel
from extractor.extractor_csv import extract_text_from_csv
from extractor.extractor_pptx import extract_text_from_pptx

def extract_text_from_file(file_path):
    """
    Extrae texto de un archivo basándose en su extensión.
    Args:
        file_path (str): Ruta al archivo.
    Returns:
        str: Texto extraído del archivo.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"El archivo {file_path} no existe")
    
    file_extension = os.path.splitext(file_path)[1].lower()
    
    try:
        if file_extension == '.pdf':
            return extract_text_from_pdf(file_path)
        elif file_extension == '.docx':
            return extract_text_from_word(file_path)
        elif file_extension == '.xlsx':
            return extract_text_from_excel(file_path)
        elif file_extension == '.csv':
            return extract_text_from_csv(file_path)
        elif file_extension == '.pptx':
            return extract_text_from_pptx(file_path)
        elif file_extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise ValueError(f"Tipo de archivo no soportado: {file_extension}")
    except Exception as e:
        raise Exception(f"Error al extraer texto de {file_path}: {str(e)}") 