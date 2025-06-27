#!/bin/bash

# Script con comandos para configurar la VM
# Ejecutar estos comandos en la VM de Google Cloud

echo "🤖 CONFIGURACIÓN DE ACTUALIZACIÓN AUTOMÁTICA EN VM"
echo "=================================================="
echo ""

# 1. Verificar que estamos en el directorio correcto
echo "1️⃣ Verificando directorio..."
pwd
ls -la auto_updater.py setup_cron.sh 2>/dev/null || echo "❌ Archivos no encontrados"

echo ""
echo "2️⃣ Instalando dependencia schedule..."
source venv/bin/activate
pip install schedule==1.2.0

echo ""
echo "3️⃣ Verificando variables de entorno..."
if [ -f ".env" ]; then
    echo "✅ Archivo .env encontrado"
    grep -E "(DROPBOX|PINECONE)" .env | head -3
else
    echo "❌ Archivo .env no encontrado"
fi

echo ""
echo "4️⃣ Probando conexión con Dropbox..."
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
import dropbox
try:
    dbx = dropbox.Dropbox(os.getenv('DROPBOX_ACCESS_TOKEN'))
    account = dbx.users_get_current_account()
    print(f'✅ Conectado a Dropbox como: {account.name.display_name}')
except Exception as e:
    print(f'❌ Error conectando a Dropbox: {e}')
"

echo ""
echo "5️⃣ Probando conexión con Pinecone..."
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
from pinecone import Pinecone
try:
    pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
    index_name = os.getenv('PINECONE_INDEX_NAME')
    indexes = pc.list_indexes()
    if index_name in [idx.name for idx in indexes]:
        print(f'✅ Índice Pinecone encontrado: {index_name}')
    else:
        print(f'❌ Índice no encontrado: {index_name}')
except Exception as e:
    print(f'❌ Error conectando a Pinecone: {e}')
"

echo ""
echo "6️⃣ Probando auto_updater..."
if [ -f "auto_updater.py" ]; then
    echo "✅ Archivo auto_updater.py encontrado"
    echo "Para probar: python auto_updater.py --test"
else
    echo "❌ Archivo auto_updater.py no encontrado"
fi

echo ""
echo "7️⃣ Configurando cron job..."
if [ -f "setup_cron.sh" ]; then
    echo "✅ Archivo setup_cron.sh encontrado"
    echo "Para configurar: ./setup_cron.sh"
else
    echo "❌ Archivo setup_cron.sh no encontrado"
fi

echo ""
echo "📋 RESUMEN DE COMANDOS A EJECUTAR:"
echo "=================================="
echo "1. pip install schedule==1.2.0"
echo "2. python auto_updater.py --test"
echo "3. ./setup_cron.sh"
echo "4. crontab -l (para verificar)"
echo "5. tail -f auto_updater.log (para monitorear)" 