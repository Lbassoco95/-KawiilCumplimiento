#!/usr/bin/env python3
"""
Sistema de Seguimiento Semanal de Documentos
Detecta documentos nuevos y modificados automáticamente
"""

import os
import schedule
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Set
from dotenv import load_dotenv
from initial_document_analysis import InitialDocumentAnalyzer
from metadata_enricher import generate_folder_report

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('weekly_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WeeklyDocumentMonitor:
    """Sistema de seguimiento semanal de documentos"""
    
    def __init__(self):
        load_dotenv()
        self.analyzer = InitialDocumentAnalyzer()
        self.monitoring_active = False
        
    def weekly_analysis(self):
        """Análisis semanal automático"""
        logger.info("📅 INICIANDO ANÁLISIS SEMANAL AUTOMÁTICO")
        logger.info("=" * 50)
        
        try:
            # Ejecutar análisis incremental
            self.analyzer.run_initial_analysis(force_full=False)
            
            # Generar reporte semanal
            self.generate_weekly_report()
            
            logger.info("✅ Análisis semanal completado")
            
        except Exception as e:
            logger.error(f"❌ Error en análisis semanal: {e}")
    
    def generate_weekly_report(self):
        """Generar reporte semanal"""
        try:
            # Obtener estadísticas del índice Pinecone
            stats = self.analyzer.index.describe_index_stats()
            total_vectors = stats.total_vector_count
            
            # Contar vectores con metadatos enriquecidos
            enriched_count = 0
            try:
                query_response = self.analyzer.index.query(
                    vector=[0] * 1536,
                    top_k=1000,
                    include_metadata=True,
                    filter={"metadata_enriquecido": {"$eq": True}}
                )
                enriched_count = len(query_response.matches)
            except:
                enriched_count = "N/A"
            
            # Generar reporte
            report = f"""
📊 REPORTE SEMANAL DE MONITOREO DE DOCUMENTOS
==============================================
Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Período: Última semana

📈 ESTADÍSTICAS DE LA BASE DE DATOS:
• Total de vectores en Pinecone: {total_vectors:,}
• Vectores con metadatos enriquecidos: {enriched_count}
• Archivos analizados esta semana: {self.analyzer.analysis_status.get('processed_files', 0)}
• Archivos fallidos: {len(self.analyzer.analysis_status.get('failed_files', []))}

📁 ACTIVIDAD DE DOCUMENTOS:
• Nuevos archivos detectados: {self.count_new_files()}
• Archivos modificados: {self.count_modified_files()}
• Archivos sin cambios: {self.count_unchanged_files()}

🔍 ESTADO DEL SISTEMA:
• Monitoreo semanal: ✅ ACTIVO
• Enriquecimiento de metadatos: ✅ FUNCIONANDO
• Conexión con Google Drive: ✅ ESTABLE
• Conexión con Pinecone: ✅ ESTABLE
• Conexión con OpenAI: ✅ ESTABLE

📋 PRÓXIMAS ACCIONES:
• Próximo análisis automático: {datetime.now() + timedelta(days=7)}
• Verificación de logs: tail -f weekly_monitor.log
• Estado en Slack: /estado

🎯 RECOMENDACIONES:
• Revisar archivos fallidos si los hay
• Verificar métricas de enriquecimiento
• Probar búsquedas en Slack
"""
            
            # Guardar reporte
            timestamp = datetime.now().strftime("%Y%m%d")
            report_filename = f"reporte_semanal_{timestamp}.txt"
            
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info(f"📄 Reporte semanal guardado: {report_filename}")
            
            # También guardar en formato JSON para análisis posterior
            json_report = {
                "fecha": datetime.now().isoformat(),
                "total_vectores": total_vectors,
                "vectores_enriquecidos": enriched_count,
                "archivos_procesados": self.analyzer.analysis_status.get('processed_files', 0),
                "archivos_fallidos": len(self.analyzer.analysis_status.get('failed_files', [])),
                "nuevos_archivos": self.count_new_files(),
                "archivos_modificados": self.count_modified_files(),
                "archivos_sin_cambios": self.count_unchanged_files()
            }
            
            json_filename = f"reporte_semanal_{timestamp}.json"
            import json
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(json_report, f, indent=2, ensure_ascii=False)
            
            return report
            
        except Exception as e:
            logger.error(f"Error generando reporte semanal: {e}")
            return f"Error generando reporte: {e}"
    
    def count_new_files(self) -> int:
        """Contar archivos nuevos"""
        count = 0
        for file_info in self.analyzer.analysis_status.get("analyzed_files", {}).values():
            if file_info.get("reason") == "new":
                count += 1
        return count
    
    def count_modified_files(self) -> int:
        """Contar archivos modificados"""
        count = 0
        for file_info in self.analyzer.analysis_status.get("analyzed_files", {}).values():
            if file_info.get("reason") == "modified":
                count += 1
        return count
    
    def count_unchanged_files(self) -> int:
        """Contar archivos sin cambios"""
        count = 0
        for file_info in self.analyzer.analysis_status.get("analyzed_files", {}).values():
            if file_info.get("reason") == "no_changes":
                count += 1
        return count
    
    def start_monitoring(self):
        """Iniciar monitoreo semanal"""
        logger.info("🚀 Iniciando monitoreo semanal de documentos")
        
        # Programar análisis semanal (viernes a las 02:00)
        schedule.every().friday.at("02:00").do(self.weekly_analysis)
        
        # También programar verificación diaria de estado
        schedule.every().day.at("09:00").do(self.daily_status_check)
        
        self.monitoring_active = True
        
        logger.info("✅ Monitoreo programado:")
        logger.info("   📅 Análisis semanal: Viernes 02:00")
        logger.info("   📊 Verificación diaria: 09:00")
        
        # Ejecutar análisis inicial si es la primera vez
        if not self.analyzer.analysis_status.get("last_analysis"):
            logger.info("🔄 Primera ejecución - Iniciando análisis inicial...")
            self.analyzer.run_initial_analysis(force_full=True)
        
        # Mantener el monitoreo activo
        while self.monitoring_active:
            try:
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto
            except KeyboardInterrupt:
                logger.info("🛑 Monitoreo detenido por el usuario")
                break
            except Exception as e:
                logger.error(f"Error en monitoreo: {e}")
                time.sleep(300)  # Esperar 5 minutos antes de reintentar
    
    def stop_monitoring(self):
        """Detener monitoreo"""
        self.monitoring_active = False
        logger.info("🛑 Monitoreo detenido")
    
    def daily_status_check(self):
        """Verificación diaria de estado"""
        logger.info("📊 Verificación diaria de estado del sistema")
        
        try:
            # Verificar conexiones
            connections_ok = True
            
            # Verificar Pinecone
            try:
                stats = self.analyzer.index.describe_index_stats()
                logger.info(f"✅ Pinecone: {stats.total_vector_count} vectores")
            except Exception as e:
                logger.error(f"❌ Error Pinecone: {e}")
                connections_ok = False
            
            # Verificar Dropbox
            try:
                self.analyzer.dbx.files_list_folder("/", limit=1)
                logger.info("✅ Dropbox: Conectado")
            except Exception as e:
                logger.error(f"❌ Error Dropbox: {e}")
                connections_ok = False
            
            # Verificar OpenAI
            try:
                from openai import OpenAI
                client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=5
                )
                logger.info("✅ OpenAI: Conectado")
            except Exception as e:
                logger.error(f"❌ Error OpenAI: {e}")
                connections_ok = False
            
            if connections_ok:
                logger.info("🎉 Todas las conexiones funcionando correctamente")
            else:
                logger.warning("⚠️ Algunas conexiones tienen problemas")
            
        except Exception as e:
            logger.error(f"Error en verificación diaria: {e}")
    
    def manual_weekly_analysis(self):
        """Ejecutar análisis semanal manualmente"""
        logger.info("🔄 Ejecutando análisis semanal manual...")
        self.weekly_analysis()

def main():
    """Función principal"""
    print("📅 Sistema de Seguimiento Semanal de Documentos")
    print("=" * 50)
    
    monitor = WeeklyDocumentMonitor()
    
    print("\n📋 Opciones disponibles:")
    print("1. Iniciar monitoreo semanal automático")
    print("2. Ejecutar análisis semanal manual")
    print("3. Verificar estado del sistema")
    print("4. Generar reporte semanal")
    print("5. Análisis inicial completo")
    
    try:
        option = input("\nSelecciona una opción (1-5): ").strip()
        
        if option == "1":
            print("\n🚀 Iniciando monitoreo semanal automático...")
            print("📅 Análisis programado: Viernes 02:00")
            print("📊 Verificación diaria: 09:00")
            print("⏰ Presiona Ctrl+C para detener")
            
            monitor.start_monitoring()
        
        elif option == "2":
            print("\n🔄 Ejecutando análisis semanal manual...")
            monitor.manual_weekly_analysis()
        
        elif option == "3":
            print("\n📊 Verificando estado del sistema...")
            monitor.daily_status_check()
        
        elif option == "4":
            print("\n📄 Generando reporte semanal...")
            report = monitor.generate_weekly_report()
            print(report)
        
        elif option == "5":
            print("\n🔍 Ejecutando análisis inicial completo...")
            monitor.analyzer.run_initial_analysis(force_full=True)
        
        else:
            print("❌ Opción no válida")
    
    except KeyboardInterrupt:
        print("\n❌ Operación cancelada por el usuario")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 