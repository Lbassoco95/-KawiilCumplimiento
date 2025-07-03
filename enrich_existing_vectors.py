#!/usr/bin/env python3
"""
Script para enriquecer vectores existentes en Pinecone con metadatos mejorados
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv
from metadata_enricher import enrich_existing_vectors, generate_folder_report

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Función principal"""
    load_dotenv()
    
    print("🔍 Enriquecimiento de Vectores Existentes en Pinecone")
    print("=" * 60)
    
    # Verificar variables de entorno
    required_vars = ["OPENAI_API_KEY", "PINECONE_API_KEY", "PINECONE_INDEX_NAME"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variables faltantes: {', '.join(missing_vars)}")
        print("Configura estas variables en tu archivo .env")
        return
    
    print("✅ Variables de entorno configuradas")
    
    # Mostrar opciones
    print("\n📋 Opciones disponibles:")
    print("1. Enriquecer todos los vectores existentes")
    print("2. Generar reporte de carpeta de Dropbox")
    print("3. Enriquecer vectores específicos por cliente")
    print("4. Verificar estado de enriquecimiento")
    
    try:
        option = input("\nSelecciona una opción (1-4): ").strip()
        
        if option == "1":
            print("\n🚀 Iniciando enriquecimiento de todos los vectores...")
            print("⚠️ Esto puede tomar tiempo dependiendo del número de vectores")
            
            confirm = input("¿Continuar? (s/n): ").lower()
            if confirm == 's':
                enrich_existing_vectors()
                print("✅ Enriquecimiento completado")
            else:
                print("❌ Operación cancelada")
        
        elif option == "2":
            folder_path = input("Ingresa la ruta de la carpeta en Dropbox: ").strip()
            if folder_path:
                print(f"\n📁 Generando reporte para: {folder_path}")
                report = generate_folder_report(folder_path)
                print("\n" + "=" * 50)
                print("REPORTE DE CARPETA")
                print("=" * 50)
                print(report)
                
                # Guardar reporte en archivo
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"reporte_carpeta_{timestamp}.txt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(report)
                print(f"\n✅ Reporte guardado en: {filename}")
            else:
                print("❌ Ruta de carpeta no especificada")
        
        elif option == "3":
            cliente = input("Ingresa el nombre del cliente: ").strip()
            if cliente:
                print(f"\n🔍 Enriqueciendo vectores del cliente: {cliente}")
                # Aquí podrías implementar enriquecimiento por cliente específico
                print("⚠️ Función en desarrollo")
            else:
                print("❌ Nombre de cliente no especificado")
        
        elif option == "4":
            print("\n📊 Verificando estado de enriquecimiento...")
            try:
                from pinecone import Pinecone
                pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
                index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
                
                stats = index.describe_index_stats()
                total_vectors = stats.total_vector_count
                
                print(f"Total de vectores: {total_vectors}")
                print("Estado: Verificación completada")
                
            except Exception as e:
                print(f"❌ Error verificando estado: {e}")
        
        else:
            print("❌ Opción no válida")
    
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada por el usuario")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 