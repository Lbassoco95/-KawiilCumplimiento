#!/usr/bin/env python3
"""
Gestor de Google Drive para el Sistema de Cumplimiento
Maneja la autenticación y operaciones con Google Drive
"""

import os
import logging
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import tempfile

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('google_drive.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GoogleDriveManager:
    """Gestor principal de Google Drive"""
    
    def __init__(self, credentials_path: str = "vizum-cumplimiento-d74f8d99f1ac.json"):
        """
        Inicializar el gestor de Google Drive
        
        Args:
            credentials_path: Ruta al archivo de credenciales JSON del usuario de servicio
        """
        self.credentials_path = credentials_path
        self.service = None
        self.folder_id = "1_yXImvvJNbj_hlqR67RInd9hoCLVyRfC"  # ID de la carpeta de prueba
        self.supported_extensions = {
            ".pdf", ".docx", ".txt", ".xlsx", ".csv", ".pptx", 
            ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"
        }
        
        # Inicializar el servicio
        self._initialize_service()
    
    def _initialize_service(self):
        """Inicializar el servicio de Google Drive"""
        try:
            # Cargar credenciales del usuario de servicio
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            
            # Construir el servicio
            self.service = build('drive', 'v3', credentials=credentials)
            logger.info("✅ Servicio de Google Drive inicializado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando servicio de Google Drive: {e}")
            raise
    
    def list_files_in_folder(self, folder_id: Optional[str] = None) -> List[Dict]:
        """
        Listar todos los archivos en una carpeta y subcarpetas (búsqueda recursiva)
        Args:
            folder_id: ID de la carpeta (usa la carpeta por defecto si no se especifica)
        Returns:
            Lista de diccionarios con información de los archivos
        """
        if folder_id is None:
            folder_id = self.folder_id
        logger.info(f"🔍 Listando archivos recursivamente en carpeta: {folder_id}")
        files = []
        folders_to_search = [folder_id]
        try:
            while folders_to_search:
                current_folder = folders_to_search.pop()
                query = f"'{current_folder}' in parents and trashed=false"
                page_token = None
                while True:
                    response = self.service.files().list(
                        q=query,
                        spaces='drive',
                        fields='nextPageToken, files(id, name, mimeType, size, modifiedTime, parents)',
                        pageToken=page_token
                    ).execute()
                    for file in response.get('files', []):
                        file_name = file.get('name', '')
                        mime_type = file.get('mimeType', '')
                        if mime_type == 'application/vnd.google-apps.folder':
                            # Es una subcarpeta, agregar a la lista para buscar recursivamente
                            folders_to_search.append(file['id'])
                        elif any(file_name.lower().endswith(ext) for ext in self.supported_extensions):
                            file_info = {
                                "id": file.get('id'),
                                "name": file_name,
                                "mime_type": mime_type,
                                "size": int(file.get('size', 0)),
                                "modified_time": file.get('modifiedTime'),
                                "parents": file.get('parents', []),
                                "path": f"/{file_name}"  # Path simplificado
                            }
                            files.append(file_info)
                    page_token = response.get('nextPageToken', None)
                    if page_token is None:
                        break
            logger.info(f"📊 Total de archivos encontrados (recursivo): {len(files)}")
            return files
        except Exception as e:
            logger.error(f"❌ Error listando archivos recursivamente: {e}")
            return []
    
    def download_file(self, file_id: str, file_name: str) -> Optional[str]:
        """
        Descargar un archivo de Google Drive
        
        Args:
            file_id: ID del archivo en Google Drive
            file_name: Nombre del archivo
            
        Returns:
            Ruta temporal del archivo descargado o None si hay error
        """
        try:
            logger.info(f"⬇️ Descargando: {file_name}")
            
            # Crear archivo temporal
            file_extension = os.path.splitext(file_name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                tmp_file_path = tmp_file.name
            
            # Descargar archivo
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                if status:
                    logger.info(f"📥 Descargando {file_name}: {int(status.progress() * 100)}%")
            
            # Guardar archivo
            with open(tmp_file_path, 'wb') as f:
                f.write(fh.getvalue())
            
            logger.info(f"✅ Archivo descargado: {tmp_file_path}")
            return tmp_file_path
            
        except Exception as e:
            logger.error(f"❌ Error descargando {file_name}: {e}")
            return None
    
    def get_file_metadata(self, file_id: str) -> Optional[Dict]:
        """
        Obtener metadatos de un archivo
        
        Args:
            file_id: ID del archivo
            
        Returns:
            Diccionario con metadatos del archivo
        """
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='id,name,mimeType,size,modifiedTime,createdTime,parents'
            ).execute()
            
            return {
                "id": file.get('id'),
                "name": file.get('name'),
                "mime_type": file.get('mimeType'),
                "size": int(file.get('size', 0)),
                "modified_time": file.get('modifiedTime'),
                "created_time": file.get('createdTime'),
                "parents": file.get('parents', [])
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo metadatos: {e}")
            return None
    
    def get_file_hash(self, file_id: str) -> str:
        """
        Obtener hash del archivo para detectar cambios
        Usa modified_time y size como indicador de cambios
        
        Args:
            file_id: ID del archivo
            
        Returns:
            String hash del archivo
        """
        metadata = self.get_file_metadata(file_id)
        if metadata:
            return f"{metadata['modified_time']}_{metadata['size']}"
        return ""
    
    def is_file_modified(self, file_id: str, previous_hash: str) -> bool:
        """
        Verificar si el archivo ha sido modificado
        
        Args:
            file_id: ID del archivo
            previous_hash: Hash anterior del archivo
            
        Returns:
            True si el archivo ha sido modificado
        """
        current_hash = self.get_file_hash(file_id)
        return current_hash != previous_hash
    
    def list_folders(self) -> List[Dict]:
        """
        Listar todas las carpetas accesibles
        
        Returns:
            Lista de carpetas con sus IDs y nombres
        """
        try:
            response = self.service.files().list(
                q="mimeType='application/vnd.google-apps.folder' and trashed=false",
                spaces='drive',
                fields='files(id, name, parents)'
            ).execute()
            
            folders = []
            for folder in response.get('files', []):
                folders.append({
                    "id": folder.get('id'),
                    "name": folder.get('name'),
                    "parents": folder.get('parents', [])
                })
            
            return folders
            
        except Exception as e:
            logger.error(f"❌ Error listando carpetas: {e}")
            return []
    
    def test_connection(self) -> bool:
        """
        Probar la conexión con Google Drive
        
        Returns:
            True si la conexión es exitosa
        """
        try:
            # Intentar listar archivos en la carpeta de prueba
            files = self.list_files_in_folder()
            logger.info(f"✅ Conexión exitosa. Archivos en carpeta: {len(files)}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en conexión: {e}")
            return False

def get_google_drive_client() -> GoogleDriveManager:
    """
    Función helper para obtener el cliente de Google Drive
    
    Returns:
        Instancia de GoogleDriveManager
    """
    return GoogleDriveManager()

if __name__ == "__main__":
    # Prueba del gestor
    try:
        manager = GoogleDriveManager()
        
        if manager.test_connection():
            print("✅ Conexión con Google Drive exitosa")
            
            # Listar archivos
            files = manager.list_files_in_folder()
            print(f"📁 Archivos encontrados: {len(files)}")
            
            for file in files[:5]:  # Mostrar solo los primeros 5
                print(f"  - {file['name']} ({file['size']} bytes)")
                
        else:
            print("❌ Error en la conexión con Google Drive")
            
    except Exception as e:
        print(f"❌ Error: {e}") 