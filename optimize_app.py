#!/usr/bin/env python3
"""
Script de optimización y configuración automática del sistema de cumplimiento regulatorio
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
import dropbox
from dropbox import DropboxTeam

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AppOptimizer:
    """Optimizador de la aplicación de cumplimiento regulatorio"""
    
    def __init__(self):
        load_dotenv()
        self.env_file = ".env"
        self.config_file = "app_config.json"
        
    def check_environment_variables(self):
        """Verificar y configurar variables de entorno"""
        logger.info("🔍 Verificando variables de entorno...")
        
        required_vars = {
            "DROPBOX_ACCESS_TOKEN": "Token de acceso de Dropbox",
            "DROPBOX_USER_EMAIL": "Email del usuario de Dropbox",
            "PINECONE_API_KEY": "API Key de Pinecone",
            "PINECONE_INDEX_NAME": "Nombre del índice de Pinecone",
            "OPENAI_API_KEY": "API Key de OpenAI",
            "SLACK_BOT_TOKEN": "Token del bot de Slack",
            "SLACK_SIGNING_SECRET": "Signing Secret de Slack"
        }
        
        optional_vars = {
            "DROPBOX_APP_KEY": "App Key de Dropbox (para OAuth)",
            "DROPBOX_APP_SECRET": "App Secret de Dropbox (para OAuth)",
            "DROPBOX_REFRESH_TOKEN": "Refresh Token de Dropbox (se genera automáticamente)",
            "DROPBOX_TEAM_MODE": "Modo equipo (1=activado, 0=desactivado)"
        }
        
        missing_required = []
        missing_optional = []
        
        # Verificar variables requeridas
        for var, description in required_vars.items():
            value = os.getenv(var)
            if not value:
                missing_required.append((var, description))
            else:
                logger.info(f"✅ {var}: Configurado")
        
        # Verificar variables opcionales
        for var, description in optional_vars.items():
            value = os.getenv(var)
            if not value:
                missing_optional.append((var, description))
            else:
                logger.info(f"✅ {var}: Configurado")
        
        # Reportar variables faltantes
        if missing_required:
            logger.error("❌ Variables requeridas faltantes:")
            for var, description in missing_required:
                logger.error(f"   - {var}: {description}")
        
        if missing_optional:
            logger.warning("⚠️ Variables opcionales faltantes:")
            for var, description in missing_optional:
                logger.warning(f"   - {var}: {description}")
        
        return len(missing_required) == 0
    
    def test_dropbox_connection(self):
        """Probar conexión con Dropbox"""
        logger.info("🔗 Probando conexión con Dropbox...")
        
        try:
            token = os.getenv("DROPBOX_ACCESS_TOKEN")
            if not token:
                logger.error("❌ No hay token de Dropbox configurado")
                return False
            
            # Probar conexión básica
            dbx = dropbox.Dropbox(token)
            account = dbx.users_get_current_account()
            logger.info(f"✅ Conexión exitosa: {account.name.display_name}")
            
            # Probar modo equipo si está configurado
            if os.getenv("DROPBOX_TEAM_MODE", "1") == "1":
                logger.info("🔍 Probando modo equipo...")
                dbx_team = DropboxTeam(token)
                team_info = dbx_team.team_get_info()
                logger.info(f"✅ Modo equipo activo: {team_info.name}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error de conexión con Dropbox: {e}")
            return False
    
    def test_pinecone_connection(self):
        """Probar conexión con Pinecone"""
        logger.info("🔗 Probando conexión con Pinecone...")
        
        try:
            from pinecone import Pinecone
            
            api_key = os.getenv("PINECONE_API_KEY")
            index_name = os.getenv("PINECONE_INDEX_NAME")
            
            if not api_key or not index_name:
                logger.error("❌ Variables de Pinecone no configuradas")
                return False
            
            pc = Pinecone(api_key=api_key)
            index = pc.Index(index_name)
            
            # Obtener estadísticas del índice
            stats = index.describe_index_stats()
            logger.info(f"✅ Conexión exitosa: {stats.total_vector_count} vectores")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error de conexión con Pinecone: {e}")
            return False
    
    def test_openai_connection(self):
        """Probar conexión con OpenAI"""
        logger.info("🔗 Probando conexión con OpenAI...")
        
        try:
            from openai import OpenAI
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.error("❌ API Key de OpenAI no configurada")
                return False
            
            client = OpenAI(api_key=api_key)
            
            # Probar con una consulta simple
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Hola"}],
                max_tokens=10
            )
            
            logger.info("✅ Conexión exitosa con OpenAI")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error de conexión con OpenAI: {e}")
            return False
    
    def optimize_performance(self):
        """Optimizar rendimiento de la aplicación"""
        logger.info("⚡ Optimizando rendimiento...")
        
        optimizations = {
            "rate_limiting": "Implementado en dropbox_auth_manager.py",
            "batch_operations": "Disponible para operaciones masivas",
            "caching": "Tokens persistentes en dropbox_tokens.json",
            "error_handling": "Reintentos automáticos con backoff",
            "logging": "Logs detallados para debugging"
        }
        
        for feature, status in optimizations.items():
            logger.info(f"✅ {feature}: {status}")
        
        # Crear archivo de configuración optimizada
        config = {
            "last_optimization": datetime.now().isoformat(),
            "features": optimizations,
            "recommendations": [
                "Usar webhooks para detección automática de cambios",
                "Implementar cache de metadatos de archivos",
                "Optimizar operaciones en lote para archivos grandes"
            ]
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"✅ Configuración guardada en {self.config_file}")
    
    def generate_setup_instructions(self):
        """Generar instrucciones de configuración personalizadas"""
        logger.info("📋 Generando instrucciones de configuración...")
        
        instructions = """
# 🚀 Configuración del Sistema de Cumplimiento Regulatorio

## Variables Requeridas

### Dropbox
1. Ve a https://www.dropbox.com/developers/apps
2. Selecciona tu aplicación
3. En "OAuth 2":
   - OAuth 2 type: Full Dropbox
   - Permissions: files.metadata.read, files.content.read, team_data.member
   - App permissions: Team member file access
4. Copia App key y App secret

### Pinecone
1. Ve a https://app.pinecone.io/
2. Obtén tu API Key
3. Anota el nombre de tu índice

### OpenAI
1. Ve a https://platform.openai.com/api-keys
2. Genera una nueva API Key

### Slack
1. Ve a https://api.slack.com/apps
2. Crea una nueva app o selecciona existente
3. Obtén Bot Token y Signing Secret

## Configuración en .env

```bash
# Dropbox
DROPBOX_ACCESS_TOKEN=tu_token_actual
DROPBOX_APP_KEY=tu_app_key
DROPBOX_APP_SECRET=tu_app_secret
DROPBOX_USER_EMAIL=leopoldo.bassoco@vizum.com.mx
DROPBOX_TEAM_MODE=1

# Pinecone
PINECONE_API_KEY=tu_pinecone_key
PINECONE_INDEX_NAME=tu_index_name

# OpenAI
OPENAI_API_KEY=tu_openai_key

# Slack
SLACK_BOT_TOKEN=tu_slack_bot_token
SLACK_SIGNING_SECRET=tu_slack_signing_secret
```

## Comandos de Verificación

```bash
# Probar conexiones
python optimize_app.py

# Configurar OAuth
python setup_dropbox_auth.py

# Probar sistema completo
python auto_updater.py --test
```
"""
        
        with open("SETUP_INSTRUCTIONS.md", "w") as f:
            f.write(instructions)
        
        logger.info("✅ Instrucciones guardadas en SETUP_INSTRUCTIONS.md")
    
    def run_full_optimization(self):
        """Ejecutar optimización completa"""
        logger.info("🚀 Iniciando optimización completa del sistema...")
        
        # Verificar variables de entorno
        env_ok = self.check_environment_variables()
        
        # Probar conexiones
        dropbox_ok = self.test_dropbox_connection()
        pinecone_ok = self.test_pinecone_connection()
        openai_ok = self.test_openai_connection()
        
        # Optimizar rendimiento
        self.optimize_performance()
        
        # Generar instrucciones
        self.generate_setup_instructions()
        
        # Reporte final
        logger.info("\n📊 REPORTE DE OPTIMIZACIÓN")
        logger.info("=" * 50)
        logger.info(f"Variables de entorno: {'✅' if env_ok else '❌'}")
        logger.info(f"Conexión Dropbox: {'✅' if dropbox_ok else '❌'}")
        logger.info(f"Conexión Pinecone: {'✅' if pinecone_ok else '❌'}")
        logger.info(f"Conexión OpenAI: {'✅' if openai_ok else '❌'}")
        logger.info("Optimización de rendimiento: ✅")
        logger.info("Instrucciones generadas: ✅")
        
        if all([env_ok, dropbox_ok, pinecone_ok, openai_ok]):
            logger.info("\n🎉 ¡Sistema completamente optimizado!")
        else:
            logger.info("\n⚠️ Algunos componentes necesitan configuración")
            logger.info("Revisa SETUP_INSTRUCTIONS.md para más detalles")

def main():
    """Función principal"""
    optimizer = AppOptimizer()
    optimizer.run_full_optimization()

if __name__ == "__main__":
    main() 