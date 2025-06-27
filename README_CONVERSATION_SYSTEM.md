# Sistema de Conversaciones y Personalidad - Vizum Compliance Assistant

## 🎯 Características Principales

### 1. **Personalidad Profesional**
- **Rol**: Oficial de Cumplimiento en Vizum
- **Tono**: Profesional, respetuoso y confiable
- **Especialización**: Cumplimiento regulatorio y auditorías

### 2. **Memoria de Conversación**
- **Contexto persistente**: Recuerda conversaciones anteriores
- **Resúmenes automáticos**: Genera resúmenes de conversaciones largas
- **Continuidad**: Mantiene contexto entre mensajes

### 3. **Cierre Automático**
- **Inactividad**: Conversaciones se cierran después de 3 minutos sin actividad
- **Persistencia**: Los datos se guardan automáticamente
- **Recuperación**: Las conversaciones se pueden retomar

### 4. **Mejoras de UX/UI**
- **Saludos personalizados**: Diferentes saludos para nuevas conversaciones
- **Mensajes contextuales**: Respuestas adaptadas al contexto
- **Feedback inmediato**: Notificaciones de procesamiento
- **Manejo de errores**: Mensajes de error profesionales

## 📁 Archivos del Sistema

### Core Files
- `conversation_manager.py` - Gestor de conversaciones y memoria
- `personality_manager.py` - Personalidad y respuestas del bot
- `slack_bot.py` - Bot actualizado con nuevas funcionalidades

### Testing
- `test_conversation_system.py` - Pruebas del sistema completo
- `test_ocr.py` - Pruebas de OCR

## 🔧 Funcionalidades Detalladas

### Gestión de Conversaciones
```python
# Crear o obtener conversación
conversation = conversation_manager.get_or_create_conversation(thread_ts, channel_id, user_id)

# Agregar mensaje
conversation_manager.add_message(thread_ts, user_id, content, role)

# Obtener contexto
context = conversation_manager.get_conversation_context(thread_ts)

# Cerrar conversación
conversation_manager.close_conversation(thread_ts)
```

### Personalidad Profesional
```python
# Saludos
greeting = personality_manager.get_greeting(is_new_conversation=True)

# Respuestas contextuales
response = personality_manager.format_professional_response(content)

# Prompts mejorados
prompts = personality_manager.get_enhanced_prompt(question, context, pinecone_data)
```

## 🚀 Uso en Slack

### Comandos Disponibles
- `/conversation-stats` - Ver estadísticas de conversaciones

### Eventos Manejados
- `app_mention` - Menciones del bot
- `message` - Mensajes directos y en hilos
- `file_shared` - Archivos compartidos (con OCR)

### Flujo de Conversación
1. **Nueva conversación**: Saludo profesional + respuesta
2. **Conversación continua**: Respuesta contextual
3. **Inactividad**: Cierre automático después de 3 minutos
4. **Retoma**: Recupera contexto anterior

## 📊 Almacenamiento

### Archivos de Datos
- `conversations.json` - Conversaciones guardadas
- Estructura:
  ```json
  {
    "thread_ts": {
      "thread_ts": "...",
      "channel_id": "...",
      "user_id": "...",
      "messages": [...],
      "context_summary": "...",
      "is_active": true,
      "conversation_id": "..."
    }
  }
  ```

### Metadatos en Pinecone
- `procesado_con_ocr`: Indica si el archivo fue procesado con OCR
- `cliente`: Identificador del usuario
- `nombre_archivo`: Nombre del archivo procesado

## 🧪 Pruebas

### Ejecutar Pruebas
```bash
# Pruebas del sistema de conversaciones
python test_conversation_system.py

# Pruebas de OCR
python test_ocr.py
```

### Verificar Funcionalidades
- ✅ Gestión de conversaciones
- ✅ Personalidad profesional
- ✅ Memoria de contexto
- ✅ Cierre automático
- ✅ OCR integrado
- ✅ Respuestas contextuales

## 🔄 Flujo de Trabajo

### 1. Nueva Consulta
```
Usuario: "¿Cuáles son los requisitos de cumplimiento?"
Bot: "¡Hola! Soy tu asistente de cumplimiento en Vizum. [Respuesta profesional]"
```

### 2. Conversación Continua
```
Usuario: "¿Y para auditorías externas?"
Bot: "[Respuesta contextual considerando conversación anterior]"
```

### 3. Procesamiento de Archivos
```
Usuario: [Sube archivo]
Bot: "📄 Procesando el archivo *documento.pdf*..."
Bot: "✅ Archivo procesado y agregado a la base de conocimiento"
```

### 4. Cierre Automático
```
[Después de 3 minutos sin actividad]
Conversación marcada como inactiva
Contexto guardado para futuras consultas
```

## 🎨 Mejoras de UX

### Mensajes Profesionales
- Saludos variados y profesionales
- Confirmaciones de entendimiento
- Mensajes de procesamiento informativos
- Despedidas cordiales

### Feedback Inmediato
- Notificación inmediata de procesamiento
- Indicadores de progreso
- Mensajes de error claros y útiles

### Contexto Inteligente
- Respuestas basadas en conversación previa
- Resúmenes automáticos de conversaciones largas
- Continuidad natural entre mensajes

## 🔧 Configuración

### Variables de Entorno Requeridas
```env
SLACK_BOT_TOKEN=your_bot_token
SLACK_SIGNING_SECRET=your_signing_secret
SLACK_APP_TOKEN=your_app_token
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_environment
```

### Configuración de Cierre Automático
```python
# En conversation_manager.py
conversation_manager = ConversationManager(auto_close_minutes=3)
```

## 📈 Monitoreo

### Estadísticas Disponibles
- Conversaciones activas
- Total de conversaciones
- Archivo de almacenamiento
- Tiempo de inactividad

### Logs
- Creación de conversaciones
- Agregado de mensajes
- Cierre de conversaciones
- Errores y excepciones

## 🚀 Próximas Mejoras

### Funcionalidades Planificadas
- [ ] Análisis de sentimiento en conversaciones
- [ ] Sugerencias automáticas de preguntas
- [ ] Integración con calendario para recordatorios
- [ ] Reportes de conversaciones por usuario
- [ ] Exportación de conversaciones
- [ ] Integración con sistemas de tickets

### Optimizaciones
- [ ] Compresión de contexto para conversaciones largas
- [ ] Cache inteligente de respuestas frecuentes
- [ ] Análisis de patrones de uso
- [ ] Personalización por usuario 