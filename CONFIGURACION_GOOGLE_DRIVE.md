# Configuración de Google Drive

## Migración Completada

✅ **Dropbox eliminado** - Todos los archivos relacionados con Dropbox han sido eliminados
✅ **Google Drive integrado** - Nuevo sistema usando Google Drive API
✅ **Archivos actualizados** - Sistema principal modificado para usar Google Drive

## Configuración Actual

- **Archivo de credenciales**: `vizum-cumplimiento-d74f8d99f1ac.json`
- **Email del usuario de servicio**: `cumplimiento-drive@vizum-cumplimiento.iam.gserviceaccount.com`
- **ID de carpeta de prueba**: `1_yXImvvJNbj_hlqR67RInd9hoCLVyRfC`

## Próximos Pasos

1. **Instalar dependencias**: `pip install -r requirements.txt`
2. **Probar integración**: `python test_google_drive.py`
3. **Análisis inicial**: `python initial_document_analysis.py`
4. **Monitoreo semanal**: `python weekly_document_monitor.py`

## Archivos Nuevos

- `google_drive_manager.py` - Gestor de Google Drive
- `test_google_drive.py` - Script de prueba
- `CONFIGURACION_GOOGLE_DRIVE.md` - Esta documentación

## Verificación

Para verificar que todo funciona:
```bash
python test_google_drive.py
```

El sistema está listo para usar Google Drive en lugar de Dropbox. 