# Resumen de Cambios - Configuración de Dropbox y Actualización Automática

## 🎯 Objetivos Cumplidos

### 1. ✅ Configuración de Carpeta de Dropbox
- **Carpeta configurada**: `/IA/PRUEBAS/Auditorías Vizum CNBV y anuales`
- **Token existente**: Se mantiene el mismo token de Dropbox
- **Compatibilidad**: Funciona con la nueva ubicación de archivos

### 2. ✅ Sistema de Actualización Automática
- **Frecuencia**: Cada viernes a las 00:01
- **Procesamiento**: Archivos PDF, Word, Excel, PowerPoint, imágenes con OCR
- **Base de datos**: Actualización automática de Pinecone
- **Logs**: Sistema completo de logging y reportes

## 📁 Archivos Creados/Modificados

### Archivos Nuevos
1. **`auto_updater.py`**
   - Sistema principal de actualización automática
   - Procesa archivos de Dropbox y los sube a Pinecone
   - Incluye OCR para imágenes y PDFs escaneados
   - Genera logs detallados y reportes

2. **`setup_cron.sh`**
   - Script para configurar el cron job automático
   - Configura la ejecución cada viernes a las 00:01
   - Maneja la activación del entorno virtual

3. **`CONFIGURACION_AUTO_UPDATE.md`**
   - Documentación completa del sistema
   - Instrucciones de instalación y configuración
   - Guía de solución de problemas

### Archivos Modificados
1. **`requirements.txt`**
   - Agregada dependencia `schedule==1.2.0`

2. **`dropbox_processor.py`**
   - Configuración actualizada para la nueva carpeta
   - Mejoras en el manejo de variables de entorno

## 🚀 Instalación y Configuración

### Paso 1: Instalar Dependencias
```bash
# Activar entorno virtual
source venv/bin/activate

# Instalar nueva dependencia
pip install schedule==1.2.0
```

### Paso 2: Verificar Configuración
Asegúrate de que las siguientes variables estén en tu archivo `.env`:
```bash
DROPBOX_ACCESS_TOKEN=tu_token_de_dropbox
PINECONE_API_KEY=tu_api_key_de_pinecone
PINECONE_INDEX_NAME=tu_nombre_de_indice
```

### Paso 3: Probar el Sistema
```bash
# Ejecutar prueba manual
python auto_updater.py --test

# Ver logs en tiempo real
tail -f auto_updater.log
```

### Paso 4: Configurar Cron Job Automático
```bash
# Ejecutar script de configuración
./setup_cron.sh

# Verificar que se configuró correctamente
crontab -l
```

## ⏰ Funcionamiento del Sistema

### Programación Automática
- **Día**: Cada viernes
- **Hora**: 00:01 (madrugada)
- **Duración**: Variable según cantidad de archivos
- **Logs**: Se guardan en `auto_updater.log`

### Proceso de Actualización
1. **Verificación**: Conexión con Dropbox y Pinecone
2. **Escaneo**: Lista todos los archivos en la carpeta configurada
3. **Procesamiento**: Para cada archivo compatible:
   - Descarga el archivo
   - Extraer texto (con OCR si es necesario)
   - Divide en chunks
   - Genera embeddings
   - Sube a Pinecone
4. **Limpieza**: Elimina archivos temporales
5. **Reporte**: Genera reporte de la actualización

### Tipos de Archivos Soportados
- **PDF**: Texto y OCR para escaneados
- **Word**: Documentos .docx
- **Excel**: Hojas de cálculo .xlsx
- **PowerPoint**: Presentaciones .pptx
- **CSV**: Archivos de datos
- **Imágenes**: JPG, PNG, BMP, TIFF (con OCR)

## 📊 Monitoreo y Logs

### Archivos de Log
- `auto_updater.log`: Log principal con detalles de cada ejecución
- `auto_updater_cron.log`: Log específico del cron job
- `update_report_YYYYMMDD.txt`: Reporte diario de actualización

### Comandos Útiles
```bash
# Ver logs en tiempo real
tail -f auto_updater.log

# Ver últimas 50 líneas
tail -50 auto_updater.log

# Buscar errores
grep "ERROR" auto_updater.log

# Ver reportes de actualización
ls -la update_report_*.txt
```

## 🔧 Configuración Avanzada

### Cambiar Frecuencia de Actualización
Para cambiar la frecuencia, edita `auto_updater.py`:
```python
# Actualización diaria a las 02:00
schedule.every().day.at("02:00").do(weekly_update)

# Actualización cada 12 horas
schedule.every(12).hours.do(weekly_update)

# Actualización cada lunes y jueves
schedule.every().monday.at("00:01").do(weekly_update)
schedule.every().thursday.at("00:01").do(weekly_update)
```

### Cambiar Carpeta de Dropbox
Edita la variable `FOLDER_PATH` en `auto_updater.py`:
```python
FOLDER_PATH = "/tu/nueva/ruta/de/carpeta"
```

## 🛡️ Seguridad y Mantenimiento

### Seguridad
- Los tokens se almacenan en el archivo `.env`
- El archivo `.env` está en `.gitignore`
- Los logs no contienen información sensible
- Los archivos temporales se eliminan automáticamente

### Mantenimiento
```bash
# Limpiar logs antiguos (más de 30 días)
find . -name "auto_updater*.log" -mtime +30 -delete
find . -name "update_report_*.txt" -mtime +30 -delete
```

## 🎉 Beneficios Implementados

### Para el Usuario
- **Automatización completa**: No requiere intervención manual
- **Actualización regular**: Base de datos siempre actualizada
- **Monitoreo**: Logs detallados para seguimiento
- **Flexibilidad**: Fácil cambio de configuración

### Para el Sistema
- **Eficiencia**: Procesamiento optimizado de archivos
- **Confiabilidad**: Manejo robusto de errores
- **Escalabilidad**: Fácil agregar nuevos tipos de archivos
- **Mantenibilidad**: Código bien documentado y estructurado

## 📞 Soporte

Para problemas o preguntas:
1. Revisar los logs primero: `tail -f auto_updater.log`
2. Verificar la configuración de variables de entorno
3. Probar ejecución manual: `python auto_updater.py --test`
4. Consultar la documentación en `CONFIGURACION_AUTO_UPDATE.md`

## ✅ Estado del Proyecto

- **Configuración de Dropbox**: ✅ Completada
- **Sistema de actualización automática**: ✅ Implementado
- **Documentación**: ✅ Completa
- **Scripts de configuración**: ✅ Listos
- **Pruebas**: ✅ Disponibles

El sistema está listo para funcionar automáticamente cada viernes a las 00:01, procesando todos los archivos nuevos en la carpeta de Dropbox y actualizando la base de datos de Pinecone. 