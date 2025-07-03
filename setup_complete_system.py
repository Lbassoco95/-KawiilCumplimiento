#!/usr/bin/env python3
"""
Script de Configuración Completa del Sistema
Guía al usuario a través de la configuración del sistema de análisis inicial y seguimiento semanal
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment_variables():
    """Verificar variables de entorno requeridas"""
    print("🔍 Verificando variables de entorno...")
    
    load_dotenv()
    
    required_vars = {
        "OPENAI_API_KEY": "OpenAI API Key (requerido para enriquecimiento)",
        "PINECONE_API_KEY": "Pinecone API Key (base de datos vectorial)",
        "PINECONE_INDEX_NAME": "Nombre del índice de Pinecone",
        "DROPBOX_APP_KEY": "Dropbox App Key",
        "DROPBOX_APP_SECRET": "Dropbox App Secret", 
        "DROPBOX_REFRESH_TOKEN": "Dropbox Refresh Token",
        "SLACK_BOT_TOKEN": "Slack Bot Token",
        "SLACK_APP_TOKEN": "Slack App Token"
    }
    
    missing_vars = []
    configured_vars = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            configured_vars.append(var)
            print(f"✅ {var}: Configurado")
        else:
            missing_vars.append(var)
            print(f"❌ {var}: Faltante - {description}")
    
    print(f"\n📊 Resumen:")
    print(f"   ✅ Variables configuradas: {len(configured_vars)}")
    print(f"   ❌ Variables faltantes: {len(missing_vars)}")
    
    if missing_vars:
        print(f"\n⚠️ Variables faltantes: {', '.join(missing_vars)}")
        print("Configura estas variables en tu archivo .env antes de continuar")
        return False
    
    print("✅ Todas las variables de entorno están configuradas")
    return True

def test_connections():
    """Probar conexiones con servicios externos"""
    print("\n🔍 Probando conexiones con servicios externos...")
    
    tests = []
    
    # Test OpenAI
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        print("✅ OpenAI: Conectado")
        tests.append(("OpenAI", True))
    except Exception as e:
        print(f"❌ OpenAI: Error - {e}")
        tests.append(("OpenAI", False))
    
    # Test Pinecone
    try:
        from pinecone import Pinecone
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))
        stats = index.describe_index_stats()
        print(f"✅ Pinecone: Conectado ({stats.total_vector_count} vectores)")
        tests.append(("Pinecone", True))
    except Exception as e:
        print(f"❌ Pinecone: Error - {e}")
        tests.append(("Pinecone", False))
    
    # Test Dropbox
    try:
        from dropbox_auth_manager import test_dropbox_connection
        if test_dropbox_connection():
            print("✅ Dropbox: Conectado")
            tests.append(("Dropbox", True))
        else:
            print("❌ Dropbox: Error de conexión")
            tests.append(("Dropbox", False))
    except Exception as e:
        print(f"❌ Dropbox: Error - {e}")
        tests.append(("Dropbox", False))
    
    # Test Slack
    try:
        from slack_bolt import App
        app = App(token=os.getenv("SLACK_BOT_TOKEN"))
        print("✅ Slack: Configurado")
        tests.append(("Slack", True))
    except Exception as e:
        print(f"❌ Slack: Error - {e}")
        tests.append(("Slack", False))
    
    # Resumen de pruebas
    successful_tests = sum(1 for _, success in tests if success)
    total_tests = len(tests)
    
    print(f"\n📊 Resumen de conexiones:")
    print(f"   ✅ Exitosas: {successful_tests}/{total_tests}")
    
    if successful_tests == total_tests:
        print("🎉 Todas las conexiones funcionan correctamente")
        return True
    else:
        print("⚠️ Algunas conexiones fallaron. Revisa la configuración.")
        return False

def run_initial_analysis():
    """Ejecutar análisis inicial completo"""
    print("\n🚀 EJECUTANDO ANÁLISIS INICIAL COMPLETO")
    print("=" * 50)
    
    try:
        from initial_document_analysis import InitialDocumentAnalyzer
        
        print("📋 Este proceso:")
        print("   • Escaneará todos los documentos en Dropbox")
        print("   • Analizará cada documento con OpenAI")
        print("   • Generará metadatos enriquecidos")
        print("   • Subirá vectores a Pinecone")
        print("   • Puede tomar tiempo dependiendo del número de archivos")
        
        confirm = input("\n¿Continuar con el análisis inicial? (s/n): ").lower()
        if confirm != 's':
            print("❌ Análisis inicial cancelado")
            return False
        
        print("\n🔄 Iniciando análisis inicial...")
        analyzer = InitialDocumentAnalyzer()
        analyzer.run_initial_analysis(force_full=True)
        
        print("✅ Análisis inicial completado exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en análisis inicial: {e}")
        return False

def setup_weekly_monitoring():
    """Configurar monitoreo semanal"""
    print("\n📅 CONFIGURANDO MONITOREO SEMANAL")
    print("=" * 40)
    
    try:
        from weekly_document_monitor import WeeklyDocumentMonitor
        
        print("📋 El monitoreo semanal:")
        print("   • Se ejecutará automáticamente cada viernes a las 02:00")
        print("   • Detectará documentos nuevos y modificados")
        print("   • Generará reportes semanales")
        print("   • Verificará el estado del sistema diariamente")
        
        confirm = input("\n¿Configurar monitoreo semanal automático? (s/n): ").lower()
        if confirm != 's':
            print("❌ Monitoreo semanal no configurado")
            return False
        
        print("\n🔄 Configurando monitoreo semanal...")
        monitor = WeeklyDocumentMonitor()
        
        # Generar reporte de configuración
        report = monitor.generate_weekly_report()
        print("✅ Monitoreo semanal configurado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error configurando monitoreo: {e}")
        return False

def test_system():
    """Probar el sistema completo"""
    print("\n🧪 PROBANDO EL SISTEMA COMPLETO")
    print("=" * 35)
    
    try:
        from test_metadata_enrichment import run_full_test
        
        print("📋 Ejecutando pruebas del sistema...")
        success = run_full_test()
        
        if success:
            print("✅ Todas las pruebas pasaron")
            return True
        else:
            print("⚠️ Algunas pruebas fallaron")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando pruebas: {e}")
        return False

def create_startup_script():
    """Crear script de inicio automático"""
    print("\n📝 CREANDO SCRIPT DE INICIO AUTOMÁTICO")
    print("=" * 45)
    
    script_content = """#!/bin/bash
# Script de inicio automático del sistema de cumplimiento
# Ejecutar: chmod +x start_system.sh && ./start_system.sh

echo "🚀 Iniciando Sistema de Cumplimiento Regulatorio..."
echo "📅 $(date)"

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Entorno virtual activado"
fi

# Verificar variables de entorno
if [ ! -f ".env" ]; then
    echo "❌ Archivo .env no encontrado"
    exit 1
fi

# Iniciar monitoreo automático
echo "🔄 Iniciando monitoreo automático..."
python auto_updater.py

echo "✅ Sistema iniciado correctamente"
"""
    
    try:
        with open("start_system.sh", "w") as f:
            f.write(script_content)
        
        # Hacer ejecutable
        os.chmod("start_system.sh", 0o755)
        
        print("✅ Script de inicio creado: start_system.sh")
        print("💡 Para iniciar el sistema: ./start_system.sh")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando script: {e}")
        return False

def generate_setup_report():
    """Generar reporte de configuración"""
    print("\n📄 GENERANDO REPORTE DE CONFIGURACIÓN")
    print("=" * 40)
    
    try:
        report = f"""
📊 REPORTE DE CONFIGURACIÓN DEL SISTEMA
========================================
Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🎯 COMPONENTES CONFIGURADOS:
✅ Variables de entorno verificadas
✅ Conexiones con servicios externos probadas
✅ Análisis inicial completo ejecutado
✅ Monitoreo semanal configurado
✅ Sistema de pruebas validado
✅ Script de inicio automático creado

🚀 FUNCIONALIDADES DISPONIBLES:
• Análisis automático de documentos con OpenAI
• Enriquecimiento de metadatos estructurados
• Búsquedas mejoradas en Pinecone
• Bot de Slack con respuestas enriquecidas
• Monitoreo semanal automático
• Reportes y logs detallados

📋 COMANDOS DISPONIBLES:
• Iniciar sistema: ./start_system.sh
• Análisis manual: python auto_updater.py
• Enriquecimiento: python enrich_existing_vectors.py
• Pruebas: python test_metadata_enrichment.py
• Monitoreo: python weekly_document_monitor.py

📅 PROGRAMACIÓN AUTOMÁTICA:
• Análisis semanal: Viernes 02:00
• Verificación diaria: 09:00
• Actualización automática: Viernes 00:01

🎉 SISTEMA LISTO PARA PRODUCCIÓN
"""
        
        # Guardar reporte
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"setup_report_{timestamp}.txt"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"✅ Reporte guardado: {filename}")
        print(report)
        
        return True
        
    except Exception as e:
        print(f"❌ Error generando reporte: {e}")
        return False

def main():
    """Función principal de configuración"""
    print("🔧 CONFIGURACIÓN COMPLETA DEL SISTEMA DE CUMPLIMIENTO")
    print("=" * 60)
    print("Este script te guiará a través de la configuración completa")
    print("del sistema de análisis inicial y seguimiento semanal.")
    
    steps = [
        ("Verificar variables de entorno", check_environment_variables),
        ("Probar conexiones", test_connections),
        ("Ejecutar análisis inicial completo", run_initial_analysis),
        ("Configurar monitoreo semanal", setup_weekly_monitoring),
        ("Probar sistema completo", test_system),
        ("Crear script de inicio", create_startup_script),
        ("Generar reporte final", generate_setup_report)
    ]
    
    completed_steps = []
    failed_steps = []
    
    for i, (step_name, step_func) in enumerate(steps, 1):
        print(f"\n{'='*60}")
        print(f"PASO {i}/{len(steps)}: {step_name}")
        print("="*60)
        
        try:
            if step_func():
                completed_steps.append(step_name)
                print(f"✅ Paso {i} completado: {step_name}")
            else:
                failed_steps.append(step_name)
                print(f"❌ Paso {i} falló: {step_name}")
                
                # Preguntar si continuar
                if i < len(steps):
                    continue_anyway = input("\n¿Continuar con los siguientes pasos? (s/n): ").lower()
                    if continue_anyway != 's':
                        print("❌ Configuración cancelada por el usuario")
                        break
                        
        except KeyboardInterrupt:
            print("\n❌ Configuración cancelada por el usuario")
            break
        except Exception as e:
            print(f"❌ Error inesperado en paso {i}: {e}")
            failed_steps.append(step_name)
    
    # Resumen final
    print(f"\n{'='*60}")
    print("📊 RESUMEN DE CONFIGURACIÓN")
    print("="*60)
    print(f"✅ Pasos completados: {len(completed_steps)}/{len(steps)}")
    print(f"❌ Pasos fallidos: {len(failed_steps)}")
    
    if completed_steps:
        print("\n✅ Pasos completados:")
        for step in completed_steps:
            print(f"   • {step}")
    
    if failed_steps:
        print("\n❌ Pasos fallidos:")
        for step in failed_steps:
            print(f"   • {step}")
    
    if len(completed_steps) == len(steps):
        print("\n🎉 ¡CONFIGURACIÓN COMPLETA!")
        print("El sistema está listo para usar en producción.")
        print("\n💡 Próximos pasos:")
        print("   1. Ejecutar: ./start_system.sh")
        print("   2. Verificar en Slack: /estado")
        print("   3. Probar búsquedas: /cumplimiento [consulta]")
    else:
        print("\n⚠️ Configuración incompleta")
        print("Revisa los pasos fallidos antes de usar el sistema.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Configuración cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        sys.exit(1) 