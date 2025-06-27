import os
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass, asdict
from uuid import uuid4

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Message:
    """Estructura para un mensaje en la conversación"""
    id: str
    timestamp: float
    user_id: str
    content: str
    role: str  # 'user' o 'assistant'
    thread_ts: str

@dataclass
class Conversation:
    """Estructura para una conversación completa"""
    thread_ts: str
    channel_id: str
    user_id: str
    created_at: float
    last_activity: float
    messages: List[Message]
    context_summary: str
    is_active: bool
    conversation_id: str

class ConversationManager:
    """Gestor de conversaciones con memoria y cierre automático"""
    
    def __init__(self, storage_file: str = "conversations.json", auto_close_minutes: int = 3):
        self.storage_file = storage_file
        self.auto_close_minutes = auto_close_minutes
        self.conversations: Dict[str, Conversation] = {}
        self.load_conversations()
        
        # Iniciar thread para cierre automático
        self.cleanup_thread = threading.Thread(target=self._cleanup_inactive_conversations, daemon=True)
        self.cleanup_thread.start()
    
    def load_conversations(self):
        """Cargar conversaciones desde archivo"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for conv_data in data.values():
                        # Recrear objetos Message
                        messages = []
                        for msg_data in conv_data['messages']:
                            messages.append(Message(**msg_data))
                        
                        # Recrear objeto Conversation
                        conv_data['messages'] = messages
                        self.conversations[conv_data['thread_ts']] = Conversation(**conv_data)
                        
                logger.info(f"Cargadas {len(self.conversations)} conversaciones")
        except Exception as e:
            logger.error(f"Error cargando conversaciones: {e}")
    
    def save_conversations(self):
        """Guardar conversaciones en archivo"""
        try:
            data = {}
            for thread_ts, conv in self.conversations.items():
                # Convertir a diccionario serializable
                conv_dict = asdict(conv)
                data[thread_ts] = conv_dict
            
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Error guardando conversaciones: {e}")
    
    def get_or_create_conversation(self, thread_ts: str, channel_id: str, user_id: str) -> Conversation:
        """Obtener conversación existente o crear una nueva"""
        if thread_ts in self.conversations:
            conv = self.conversations[thread_ts]
            conv.last_activity = time.time()
            conv.is_active = True
            return conv
        
        # Crear nueva conversación
        conv = Conversation(
            thread_ts=thread_ts,
            channel_id=channel_id,
            user_id=user_id,
            created_at=time.time(),
            last_activity=time.time(),
            messages=[],
            context_summary="",
            is_active=True,
            conversation_id=str(uuid4())
        )
        
        self.conversations[thread_ts] = conv
        logger.info(f"Nueva conversación creada: {thread_ts}")
        return conv
    
    def add_message(self, thread_ts: str, user_id: str, content: str, role: str = "user"):
        """Agregar mensaje a la conversación"""
        if thread_ts not in self.conversations:
            logger.warning(f"Conversación no encontrada: {thread_ts}")
            return
        
        conv = self.conversations[thread_ts]
        conv.last_activity = time.time()
        conv.is_active = True
        
        message = Message(
            id=str(uuid4()),
            timestamp=time.time(),
            user_id=user_id,
            content=content,
            role=role,
            thread_ts=thread_ts
        )
        
        conv.messages.append(message)
        logger.info(f"Mensaje agregado a conversación {thread_ts}")
    
    def get_conversation_context(self, thread_ts: str, max_messages: int = 10) -> str:
        """Obtener contexto de la conversación para el modelo"""
        if thread_ts not in self.conversations:
            return ""
        
        conv = self.conversations[thread_ts]
        
        # Obtener los últimos mensajes
        recent_messages = conv.messages[-max_messages:] if len(conv.messages) > max_messages else conv.messages
        
        context_parts = []
        
        # Agregar resumen de contexto si existe
        if conv.context_summary:
            context_parts.append(f"Resumen de conversación anterior: {conv.context_summary}")
        
        # Agregar mensajes recientes
        for msg in recent_messages:
            role_name = "Usuario" if msg.role == "user" else "Asistente"
            context_parts.append(f"{role_name}: {msg.content}")
        
        return "\n".join(context_parts)
    
    def update_context_summary(self, thread_ts: str, summary: str):
        """Actualizar el resumen de contexto de la conversación"""
        if thread_ts in self.conversations:
            self.conversations[thread_ts].context_summary = summary
    
    def close_conversation(self, thread_ts: str):
        """Cerrar una conversación"""
        if thread_ts in self.conversations:
            self.conversations[thread_ts].is_active = False
            logger.info(f"Conversación cerrada: {thread_ts}")
    
    def _cleanup_inactive_conversations(self):
        """Thread para cerrar conversaciones inactivas"""
        while True:
            try:
                current_time = time.time()
                inactive_threshold = current_time - (self.auto_close_minutes * 60)
                
                to_close = []
                for thread_ts, conv in self.conversations.items():
                    if conv.is_active and conv.last_activity < inactive_threshold:
                        to_close.append(thread_ts)
                
                for thread_ts in to_close:
                    self.close_conversation(thread_ts)
                    logger.info(f"Conversación cerrada por inactividad: {thread_ts}")
                
                # Guardar conversaciones cada 5 minutos
                if int(current_time) % 300 == 0:
                    self.save_conversations()
                
                time.sleep(60)  # Revisar cada minuto
                
            except Exception as e:
                logger.error(f"Error en cleanup thread: {e}")
                time.sleep(60)
    
    def get_active_conversations(self) -> List[Conversation]:
        """Obtener conversaciones activas"""
        return [conv for conv in self.conversations.values() if conv.is_active]
    
    def get_conversation_stats(self) -> Dict:
        """Obtener estadísticas de conversaciones"""
        active_count = len(self.get_active_conversations())
        total_count = len(self.conversations)
        
        return {
            "active_conversations": active_count,
            "total_conversations": total_count,
            "storage_file": self.storage_file
        } 