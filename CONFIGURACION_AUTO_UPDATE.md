# Configuración de Actualización Automática de Pinecone

## Resumen

Se ha implementado un sistema de actualización automática que:

1. **Monitorea la carpeta de Dropbox**: `/IA/PRUEBAS/Auditorías Vizum CNBV y anuales`
2. **Se ejecuta automáticamente**: Cada viernes a las 00:01
3. **Procesa archivos nuevos**: PDF, Word, Excel, PowerPoint, imágenes con OCR
4. **Actualiza Pinecone**: Sube los chunks procesados a la base de datos
5. **Genera reportes**: Logs detallados de cada actualización

## Archivos Creados

### 1. `auto_updater.py`
- Sistema principal de actualización automática
- Procesa archivos de Dropbox y los sube a Pinecone
- Incluye OCR para imágenes y PDFs escaneados
- Genera logs detallados

### 2. `setup_cron.sh`
- Script para configurar el cron job automático
- Configura la ejecución cada viernes a las 00:01
- Maneja la activación del entorno virtual

### 3. `requirements.txt` (actualizado)
- Agregada dependencia `schedule==1.2.0` para programación de tareas

## Instalación y Configuración

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

## Funcionamiento

### Programación
- **Frecuencia**: Cada viernes a las 00:01
- **Duración**: Variable según cantidad de archivos
- **Logs**: Se guardan en `auto_updater.log`

### Proceso de Actualización
1. **Conexión**: Verifica conexión con Dropbox y Pinecone
2. **Escaneo**: Lista todos los archivos en la carpeta configurada
3. **Procesamiento**: Para cada archivo compatible:
   - Descarga el archivo
   - Extrae texto (con OCR si es necesario)
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

## Monitoreo y Logs

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

## Configuración Avanzada

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

### Agregar Notificaciones
Puedes agregar notificaciones por email o Slack cuando hay errores:
```python
def send_notification(message):
    # Implementar notificación por email/Slack
    pass

# En la función weekly_update()
except Exception as e:
    logger.error(f"❌ Error en actualización semanal: {e}")
    send_notification(f"Error en actualización automática: {e}")
```

## Solución de Problemas

### Error de Conexión con Dropbox
```bash
# Verificar token
echo $DROPBOX_ACCESS_TOKEN

# Probar conexión manual
python -c "import dropbox; dbx = dropbox.Dropbox('$DROPBOX_ACCESS_TOKEN'); print(dbx.users_get_current_account())"
```

### Error de Conexión con Pinecone
```bash
# Verificar API key
echo $PINECONE_API_KEY

# Probar conexión manual
python -c "from pinecone import Pinecone; pc = Pinecone(api_key='$PINECONE_API_KEY'); print(pc.list_indexes())"
```

### Cron Job No Se Ejecuta
```bash
# Verificar que el cron job esté configurado
crontab -l

# Verificar logs del sistema
sudo tail -f /var/log/cron

# Probar ejecución manual
cd /ruta/al/proyecto && source venv/bin/activate && python auto_updater.py
```

### Archivos No Se Procesan
```bash
# Verificar permisos de la carpeta
ls -la /tmp/

# Verificar espacio en disco
df -h

# Verificar logs específicos
grep "ERROR" auto_updater.log
```

## Mantenimiento

### Limpieza de Logs
```bash
# Limpiar logs antiguos (más de 30 días)
find . -name "auto_updater*.log" -mtime +30 -delete
find . -name "update_report_*.txt" -mtime +30 -delete
```

### Verificación Periódica
- Revisar logs semanalmente
- Verificar que las actualizaciones se ejecuten correctamente
- Monitorear espacio en disco
- Verificar conectividad con servicios externos

## Seguridad

### Tokens y Credenciales
- Los tokens se almacenan en el archivo `.env`
- El archivo `.env` está en `.gitignore`
- Los logs no contienen información sensible
- Los archivos temporales se eliminan automáticamente

### Permisos
- El script requiere permisos de lectura en Dropbox
- El script requiere permisos de escritura en Pinecone
- El cron job se ejecuta con los permisos del usuario

## Contacto y Soporte

Para problemas o preguntas sobre la configuración:
1. Revisar los logs primero
2. Verificar la configuración de variables de entorno
3. Probar ejecución manual
4. Consultar la documentación de Dropbox y Pinecone 