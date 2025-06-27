# Este archivo hace que extractor sea un paquete Python 
from .extractor_pdf import extract_text_from_pdf
from .extractor_word import extract_text_from_word
from .extractor_excel import extract_text_from_excel
from .extractor_csv import extract_text_from_csv
from .extractor_pptx import extract_text_from_pptx
from .extractor_ocr import (
    extract_text_from_image,
    extract_text_from_pdf_with_ocr,
    needs_ocr,
    extract_text_with_ocr_if_needed
)
from .text_chunker import chunk_text
from .pinecone_uploader import upload_chunks_to_pinecone, query_pinecone

__all__ = [
    'extract_text_from_pdf',
    'extract_text_from_word', 
    'extract_text_from_excel',
    'extract_text_from_csv',
    'extract_text_from_pptx',
    'extract_text_from_image',
    'extract_text_from_pdf_with_ocr',
    'needs_ocr',
    'extract_text_with_ocr_if_needed',
    'chunk_text',
    'upload_chunks_to_pinecone',
    'query_pinecone'
] 