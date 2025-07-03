#!/usr/bin/env python3
"""
Script para configurar múltiples carpetas de análisis en el sistema
Permite analizar todas las carpetas relevantes de VIZUM TECHNOLOGIES
"""

import os
from pathlib import Path

def update_auto_updater_config():
    """Actualizar configuración de auto_updater.py para múltiples carpetas"""
    
    auto_updater_file = Path('auto_updater.py')
    
    if not auto_updater_file.exists():
        print("❌ No se encontró auto_updater.py")
        return False
    
    # Leer contenido actual
    with open(auto_updater_file, 'r') as f:
        content = f.read()
    
    # Definir múltiples carpetas para análisis
    new_folder_config = '''# Configuración de carpetas múltiples
FOLDER_PATHS = [
    "/Leopoldo Bassoco Nova/IA/PRUEBAS/VIZUM TECHNOLOGIES",
    "/IA/PRUEBAS/Auditorías Vizum CNBV y anuales",
    "/Leopoldo Bassoco Nova/IA/PRUEBAS/VIZUM TECHNOLOGIES/Auditorías",
    "/Leopoldo Bassoco Nova/IA/PRUEBAS/VIZUM TECHNOLOGIES/Regulaciones",
    "/Leopoldo Bassoco Nova/IA/PRUEBAS/VIZUM TECHNOLOGIES/Compliance",
    "/Leopoldo Bassoco Nova/IA/PRUEBAS/VIZUM TECHNOLOGIES/Documentos",
    "/Leopoldo Bassoco Nova/IA/PRUEBAS/VIZUM TECHNOLOGIES/Reportes",
    "/Leopoldo Bassoco Nova/IA/PRUEBAS/VIZUM TECHNOLOGIES/Manuales",
    "/Leopoldo Bassoco Nova/IA/PRUEBAS/VIZUM TECHNOLOGIES/Políticas",
    "/Leopoldo Bassoco Nova/IA/PRUEBAS/VIZUM TECHNOLOGIES/Procedimientos"
]

# Carpeta principal para compatibilidad
FOLDER_PATH = "/Leopoldo Bassoco Nova/IA/PRUEBAS/VIZUM TECHNOLOGIES"'''
    
    # Reemplazar la configuración de carpeta única
    lines = content.split('\n')
    updated_lines = []
    folder_config_found = False
    
    for line in lines:
        if line.strip().startswith('FOLDER_PATH = '):
            if not folder_config_found:
                # Insertar nueva configuración
                updated_lines.extend(new_folder_config.split('\n'))
                folder_config_found = True
        else:
            updated_lines.append(line)
    
    # Si no se encontró la configuración, agregarla después de las importaciones
    if not folder_config_found:
        new_lines = []
        for i, line in enumerate(lines):
            new_lines.append(line)
            if 'load_dotenv()' in line:
                # Agregar después de load_dotenv()
                new_lines.extend([''] + new_folder_config.split('\n'))
        updated_lines = new_lines
    
    # Escribir archivo actualizado
    with open(auto_updater_file, 'w') as f:
        f.write('\n'.join(updated_lines))
    
    return True

def update_scan_function():
    """Actualizar función de escaneo para múltiples carpetas"""
    
    auto_updater_file = Path('auto_updater.py')
    
    if not auto_updater_file.exists():
        return False
    
    # Leer contenido actual
    with open(auto_updater_file, 'r') as f:
        content = f.read()
    
    # Nueva función de escaneo múltiple
    new_scan_function = '''def scan_for_new_files():
    """Escanear múltiples carpetas de Dropbox en busca de archivos nuevos"""
    logger.info("🔍 Iniciando escaneo de archivos en múltiples carpetas de Dropbox...")
    
    try:
        # Obtener cliente de Dropbox válido
        dbx = get_dropbox_client()
        
        total_files = 0
        processed_files = 0
        
        # Escanear cada carpeta configurada
        for folder_path in FOLDER_PATHS:
            try:
                logger.info(f"📁 Escaneando carpeta: {folder_path}")
                
                # Obtener lista de archivos en la carpeta
                result = dbx.files_list_folder(folder_path, recursive=True)
                
                for entry in result.entries:
                    if isinstance(entry, dropbox.files.FileMetadata) and is_supported_file(entry.path_lower):
                        total_files += 1
                        logger.info(f"📄 Procesando archivo: {entry.path_lower}")
                        if process_file(entry.path_lower):
                            processed_files += 1
                            
            except dropbox.exceptions.ApiError as e:
                if e.error.is_path():
                    logger.warning(f"⚠️ Carpeta no encontrada: {folder_path}")
                else:
                    logger.error(f"❌ Error accediendo a {folder_path}: {e}")
            except Exception as e:
                logger.error(f"❌ Error escaneando {folder_path}: {e}")
        
        logger.info(f"📊 Resumen del escaneo múltiple:")
        logger.info(f"   - Carpetas escaneadas: {len(FOLDER_PATHS)}")
        logger.info(f"   - Total de archivos encontrados: {total_files}")
        logger.info(f"   - Archivos procesados exitosamente: {processed_files}")
        
        return processed_files
        
    except Exception as e:
        logger.error(f"❌ Error en escaneo múltiple: {e}")
        return 0'''
    
    # Reemplazar función existente
    lines = content.split('\n')
    updated_lines = []
    in_scan_function = False
    function_replaced = False
    
    for line in lines:
        if 'def scan_for_new_files():' in line:
            in_scan_function = True
            function_replaced = True
            # Agregar nueva función
            updated_lines.extend(new_scan_function.split('\n'))
            continue
        
        if in_scan_function:
            if line.strip().startswith('def ') and not line.strip().startswith('def scan_for_new_files'):
                in_scan_function = False
                updated_lines.append(line)
            elif not line.strip().startswith('def '):
                continue  # Saltar líneas dentro de la función antigua
            else:
                in_scan_function = False
                updated_lines.append(line)
        else:
            updated_lines.append(line)
    
    # Si no se encontró la función, agregarla al final
    if not function_replaced:
        updated_lines.extend(['', new_scan_function])
    
    # Escribir archivo actualizado
    with open(auto_updater_file, 'w') as f:
        f.write('\n'.join(updated_lines))
    
    return True

def create_folder_analysis_report():
    """Crear reporte de análisis de carpetas"""
    
    report_content = '''# 📁 CONFIGURACIÓN DE CARPETAS MÚLTIPLES

## 🎯 Carpetas Configuradas para Análisis

### 1. 📂 Carpeta Principal
- **Ruta:** `/Leopoldo Bassoco Nova/IA/PRUEBAS/VIZUM TECHNOLOGIES`
- **Contenido:** Documentos generales de VIZUM TECHNOLOGIES

### 2. 📂 Auditorías CNBV
- **Ruta:** `/IA/PRUEBAS/Auditorías Vizum CNBV y anuales`
- **Contenido:** Auditorías específicas de CNBV y anuales

### 3. 📂 Subcarpetas de VIZUM TECHNOLOGIES
- **Auditorías:** `/Leopoldo Bassoco Nova/IA/PRUEBAS/VIZUM TECHNOLOGIES/Auditorías`
- **Regulaciones:** `/Leopoldo Bassoco Nova/IA/PRUEBAS/VIZUM TECHNOLOGIES/Regulaciones`
- **Compliance:** `/Leopoldo Bassoco Nova/IA/PRUEBAS/VIZUM TECHNOLOGIES/Compliance`
- **Documentos:** `/Leopoldo Bassoco Nova/IA/PRUEBAS/VIZUM TECHNOLOGIES/Documentos`
- **Reportes:** `/Leopoldo Bassoco Nova/IA/PRUEBAS/VIZUM TECHNOLOGIES/Reportes`
- **Manuales:** `/Leopoldo Bassoco Nova/IA/PRUEBAS/VIZUM TECHNOLOGIES/Manuales`
- **Políticas:** `/Leopoldo Bassoco Nova/IA/PRUEBAS/VIZUM TECHNOLOGIES/Políticas`
- **Procedimientos:** `/Leopoldo Bassoco Nova/IA/PRUEBAS/VIZUM TECHNOLOGIES/Procedimientos`

## 🔄 Funcionalidades

### ✅ Escaneo Múltiple
- Análisis automático de todas las carpetas configuradas
- Detección de archivos nuevos y modificados
- Procesamiento recursivo de subcarpetas

### ✅ Metadatos Enriquecidos
- Análisis de tipo de documento por carpeta
- Categorización automática por contexto
- Enriquecimiento con IA para mejor búsqueda

### ✅ Búsqueda Semántica
- Búsqueda en todos los documentos de todas las carpetas
- Filtrado por tipo de documento y categoría
- Respuestas contextuales mejoradas

## 🚀 Próximos Pasos

1. **Configurar credenciales de Dropbox** (si no están configuradas)
2. **Ejecutar análisis inicial completo**
3. **Configurar actualización automática**
4. **Probar búsquedas en Slack**

## 📊 Métricas Esperadas

- **Carpetas monitoreadas:** 10
- **Tipos de documentos:** PDF, Word, Excel, PowerPoint, imágenes
- **Procesamiento:** OCR automático cuando sea necesario
- **Actualización:** Semanal automática
'''
    
    with open('CONFIGURACION_CARPETAS_MULTIPLES.md', 'w') as f:
        f.write(report_content)
    
    return True

def main():
    print("🔧 CONFIGURANDO ANÁLISIS DE MÚLTIPLES CARPETAS")
    print("=" * 50)
    
    print("📁 Actualizando configuración de carpetas...")
    if update_auto_updater_config():
        print("✅ Configuración de carpetas actualizada")
    else:
        print("❌ Error actualizando configuración")
        return
    
    print("🔄 Actualizando función de escaneo...")
    if update_scan_function():
        print("✅ Función de escaneo actualizada")
    else:
        print("❌ Error actualizando función de escaneo")
        return
    
    print("📄 Creando reporte de configuración...")
    if create_folder_analysis_report():
        print("✅ Reporte de configuración creado")
    else:
        print("❌ Error creando reporte")
        return
    
    print()
    print("🎉 CONFIGURACIÓN COMPLETADA")
    print("=" * 30)
    print("✅ Sistema configurado para analizar múltiples carpetas")
    print("✅ Escaneo recursivo habilitado")
    print("✅ Metadatos enriquecidos activados")
    print()
    print("🚀 Próximos pasos:")
    print("1. Configurar credenciales de Dropbox (si es necesario)")
    print("2. Ejecutar: python setup_complete_system.py")
    print("3. Ejecutar: python auto_updater.py")
    print("4. Probar búsquedas en Slack")

if __name__ == "__main__":
    main() 