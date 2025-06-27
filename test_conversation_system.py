#!/usr/bin/env python3
"""
Script de prueba para verificar el sistema de conversaciones y personalidad
"""

import os
import sys
import time
from dotenv import load_dotenv

# Agregar el directorio actual al path para importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from conversation_manager import ConversationManager
from personality_manager import PersonalityManager

def test_conversation_system():
    """Prueba el sistema de conversaciones y personalidad"""
    
    print("🧪 Probando sistema de conversaciones y personalidad...")
    
    # Inicializar gestores
    conversation_manager = ConversationManager(auto_close_minutes=1)  # 1 minuto para pruebas
    personality_manager = PersonalityManager()
    
    # Prueba 1: Personalidad
    print("\n1. Probando gestor de personalidad:")
    print(f"   Nombre: {personality_manager.name}")
    print(f"   Rol: {personality_manager.role}")
    print(f"   Empresa: {personality_manager.company}")
    
    greeting = personality_manager.get_greeting()
    print(f"   Saludo: {greeting}")
    
    farewell = personality_manager.get_farewell()
    print(f"   Despedida: {farewell}")
    
    # Prueba 2: Crear conversación
    print("\n2. Probando gestor de conversaciones:")
    
    thread_ts = "test_thread_123"
    channel_id = "test_channel"
    user_id = "test_user"
    
    # Crear conversación
    conversation = conversation_manager.get_or_create_conversation(thread_ts, channel_id, user_id)
    print(f"   Conversación creada: {conversation.conversation_id}")
    print(f"   Activa: {conversation.is_active}")
    
    # Prueba 3: Agregar mensajes
    print("\n3. Probando mensajes:")
    
    # Mensaje del usuario
    conversation_manager.add_message(thread_ts, user_id, "¿Cuáles son los requisitos de cumplimiento?", "user")
    print("   ✅ Mensaje de usuario agregado")
    
    # Mensaje del bot
    conversation_manager.add_message(thread_ts, user_id, "Los requisitos incluyen...", "assistant")
    print("   ✅ Mensaje del bot agregado")
    
    # Prueba 4: Obtener contexto
    print("\n4. Probando contexto de conversación:")
    context = conversation_manager.get_conversation_context(thread_ts)
    print(f"   Contexto: {context[:100]}...")
    
    # Prueba 5: Actualizar resumen
    print("\n5. Probando actualización de resumen:")
    conversation_manager.update_context_summary(thread_ts, "Conversación sobre requisitos de cumplimiento regulatorio")
    print("   ✅ Resumen actualizado")
    
    # Prueba 6: Estadísticas
    print("\n6. Probando estadísticas:")
    stats = conversation_manager.get_conversation_stats()
    print(f"   Conversaciones activas: {stats['active_conversations']}")
    print(f"   Total de conversaciones: {stats['total_conversations']}")
    
    # Prueba 7: Prompt mejorado
    print("\n7. Probando prompt mejorado:")
    prompts = personality_manager.get_enhanced_prompt(
        user_question="¿Qué documentos necesito para una auditoría?",
        conversation_context="Conversación previa sobre cumplimiento",
        pinecone_context="Información de documentos regulatorios"
    )
    print(f"   System prompt: {prompts['system'][:100]}...")
    print(f"   User prompt: {prompts['user'][:100]}...")
    
    # Prueba 8: Cerrar conversación
    print("\n8. Probando cierre de conversación:")
    conversation_manager.close_conversation(thread_ts)
    print("   ✅ Conversación cerrada")
    
    # Verificar que se cerró
    updated_stats = conversation_manager.get_conversation_stats()
    print(f"   Conversaciones activas después del cierre: {updated_stats['active_conversations']}")
    
    # Guardar conversaciones
    conversation_manager.save_conversations()
    print("   ✅ Conversaciones guardadas")
    
    print("\n✅ Todas las pruebas del sistema de conversaciones completadas!")

def test_personality_responses():
    """Prueba las respuestas de personalidad"""
    
    print("\n🎭 Probando respuestas de personalidad:")
    
    personality_manager = PersonalityManager()
    
    # Probar diferentes tipos de respuestas
    responses = [
        ("Saludo", personality_manager.get_greeting()),
        ("Despedida", personality_manager.get_farewell()),
        ("Confirmación", personality_manager.get_confirmation()),
        ("Procesamiento", personality_manager.get_processing_message()),
        ("Clarificación", personality_manager.get_clarification("el tipo de auditoría")),
        ("Intro regulatoria", personality_manager.get_regulatory_intro()),
        ("Mensaje de archivo", personality_manager.get_file_processing_message("documento.pdf")),
        ("Mensaje de error", personality_manager.get_error_message("Error de conexión"))
    ]
    
    for response_type, response in responses:
        print(f"   {response_type}: {response[:80]}...")
    
    print("✅ Pruebas de personalidad completadas!")

if __name__ == "__main__":
    load_dotenv()
    test_conversation_system()
    test_personality_responses() 