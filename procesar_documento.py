#!/usr/bin/env python3
"""
Script para procesar documentos y subirlos a Pinecone
"""

from extractor.extractor_pdf import extract_text_from_pdf
from extractor.text_chunker import chunk_text
from extractor.pinecone_uploader import upload_chunks_to_pinecone

def main():
    # Ruta al archivo PDF
    ruta_pdf = "/Users/leopoldobassoconova/Downloads/Designación de persona responsable.pdf"
    
    try:
        # Extraer texto del PDF
        print("📄 Extrayendo texto del PDF...")
        texto = extract_text_from_pdf(ruta_pdf)
        print(f"✅ Texto extraído: {len(texto)} caracteres")
        
        if len(texto) == 0:
            print("❌ No se pudo extraer texto del PDF. Puede estar escaneado o protegido.")
            return
        
        # Dividir en chunks
        print("✂️ Dividiendo texto en chunks...")
        chunks = chunk_text(texto)
        print(f"✅ Texto dividido en {len(chunks)} chunks")
        
        # Preparar metadatos
        metadata = {
            "cliente": "Vizum",
            "archivo": "designacion_responsable.pdf",
            "tipo": "PDF",
            "fecha": "2025-06-25"
        }
        
        # Subir a Pinecone
        print("🚀 Subiendo chunks a Pinecone...")
        success = upload_chunks_to_pinecone(chunks, metadata)
        
        if success:
            print("🎉 Proceso completado exitosamente!")
        else:
            print("❌ Error en el proceso")
            
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo: {ruta_pdf}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main() 