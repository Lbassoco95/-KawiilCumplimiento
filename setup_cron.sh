#!/bin/bash

# Script para configurar la actualización automática de Pinecone
# Ejecuta cada viernes a las 00:01

echo "🤖 Configurando actualización automática de Pinecone..."

# Obtener la ruta actual del proyecto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📁 Directorio del proyecto: $PROJECT_DIR"

# Crear el comando para el cron job
CRON_COMMAND="0 1 * * 5 cd $PROJECT_DIR && source venv/bin/activate && python auto_updater.py >> auto_updater_cron.log 2>&1"

echo "⏰ Comando del cron job:"
echo "$CRON_COMMAND"
echo ""

# Verificar si ya existe el cron job
if crontab -l 2>/dev/null | grep -q "auto_updater.py"; then
    echo "⚠️  Ya existe un cron job para auto_updater.py"
    echo "¿Deseas reemplazarlo? (y/n)"
    read -r response
    if [[ "$response" != "y" ]]; then
        echo "❌ Configuración cancelada"
        exit 1
    fi
fi

# Crear archivo temporal con el nuevo cron job
TEMP_CRON=$(mktemp)

# Obtener cron jobs existentes (excluyendo auto_updater.py)
crontab -l 2>/dev/null | grep -v "auto_updater.py" > "$TEMP_CRON"

# Agregar el nuevo cron job
echo "$CRON_COMMAND" >> "$TEMP_CRON"

# Instalar el nuevo cron job
crontab "$TEMP_CRON"

# Limpiar archivo temporal
rm "$TEMP_CRON"

echo "✅ Cron job configurado exitosamente"
echo ""
echo "📋 Cron jobs actuales:"
crontab -l
echo ""
echo "📝 Para verificar que funciona:"
echo "1. Ejecuta: python auto_updater.py --test"
echo "2. Revisa los logs: tail -f auto_updater.log"
echo "3. El próximo viernes a las 00:01 se ejecutará automáticamente" 