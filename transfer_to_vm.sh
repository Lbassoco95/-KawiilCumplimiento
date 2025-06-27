#!/bin/bash

# Script para transferir archivos a la VM de Google Cloud
# Uso: ./transfer_to_vm.sh [IP_DE_LA_VM]

if [ $# -eq 0 ]; then
    echo "❌ Error: Debes proporcionar la IP de la VM"
    echo "Uso: ./transfer_to_vm.sh [IP_DE_LA_VM]"
    echo "Ejemplo: ./transfer_to_vm.sh 34.123.45.67"
    exit 1
fi

VM_IP=$1
USER="leo_bassoco"
REMOTE_DIR="/home/leo_bassoco/KawiilVizumCumplimiento"

echo "🚀 Transfiriendo archivos a la VM..."
echo "IP: $VM_IP"
echo "Usuario: $USER"
echo "Directorio remoto: $REMOTE_DIR"
echo ""

# Archivos a transferir
FILES=(
    "auto_updater.py"
    "setup_cron.sh"
    "requirements.txt"
    "dropbox_processor.py"
    "CONFIGURACION_AUTO_UPDATE.md"
    "RESUMEN_CAMBIOS.md"
)

# Transferir cada archivo
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "📤 Transfiriendo $file..."
        scp "$file" "$USER@$VM_IP:$REMOTE_DIR/"
        if [ $? -eq 0 ]; then
            echo "✅ $file transferido exitosamente"
        else
            echo "❌ Error transfiriendo $file"
        fi
    else
        echo "⚠️ Archivo $file no encontrado"
    fi
done

echo ""
echo "🎉 Transferencia completada!"
echo ""
echo "📝 Próximos pasos en la VM:"
echo "1. Conectarse a la VM: ssh $USER@$VM_IP"
echo "2. Navegar al directorio: cd $REMOTE_DIR"
echo "3. Instalar dependencia: pip install schedule==1.2.0"
echo "4. Probar el sistema: python auto_updater.py --test"
echo "5. Configurar cron: ./setup_cron.sh" 