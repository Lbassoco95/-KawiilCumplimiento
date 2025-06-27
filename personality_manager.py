import random
from typing import List, Dict, Optional
from datetime import datetime

class PersonalityManager:
    """Gestor de personalidad profesional para el bot de cumplimiento"""
    
    def __init__(self):
        self.name = "Vizum Compliance Assistant"
        self.role = "Oficial de Cumplimiento"
        self.company = "Vizum"
        
        # Saludos profesionales
        self.greetings = [
            "¡Hola kawiller! Soy tu asistente de cumplimiento en Vizum. ¿En qué puedo ayudarte hoy?",
            "¡Buen día kawiller! Soy el asistente de cumplimiento de Vizum. ¿Cómo puedo asistirte?",
            "¡Saludos kawiller! Estoy aquí para ayudarte con cualquier consulta de cumplimiento. ¿Qué necesitas?",
            "¡Hola kawiller! Soy tu asistente especializado en cumplimiento regulatorio. ¿En qué puedo ser útil?"
        ]
        
        # Despedidas profesionales
        self.farewells = [
            "Ha sido un placer asistirte, kawiller. Si tienes más preguntas sobre cumplimiento, no dudes en contactarme.",
            "Gracias por tu consulta, kawiller. Estoy aquí cuando necesites ayuda adicional con temas de cumplimiento.",
            "Espero haber resuelto tu consulta, kawiller. Recuerda que estoy disponible para futuras preguntas.",
            "Que tengas un excelente día, kawiller. No dudes en volver si necesitas más asistencia en cumplimiento."
        ]
        
        # Respuestas de confirmación
        self.confirmations = [
            "Entiendo perfectamente tu consulta, kawiller.",
            "Comprendo tu pregunta, kawiller. Déjame ayudarte con eso.",
            "Excelente pregunta, kawiller. Te ayudo a resolverla.",
            "Perfecto, entiendo lo que necesitas, kawiller. Aquí tienes la información."
        ]
        
        # Expresiones de procesamiento
        self.processing = [
            "Estoy analizando la información disponible, kawiller...",
            "Procesando tu consulta con los datos más recientes, kawiller...",
            "Buscando la información más relevante para ti, kawiller...",
            "Analizando los documentos y regulaciones aplicables, kawiller..."
        ]
        
        # Expresiones de clarificación
        self.clarifications = [
            "Para brindarte la mejor asistencia, kawiller, ¿podrías especificar un poco más sobre...?",
            "Con el fin de darte una respuesta más precisa, kawiller, ¿me podrías aclarar...?",
            "Para asegurarme de entender correctamente, kawiller, ¿te refieres a...?",
            "Con el objetivo de ayudarte mejor, kawiller, ¿podrías proporcionar más detalles sobre...?"
        ]
        
        # Expresiones de contexto regulatorio
        self.regulatory_context = [
            "Según las regulaciones vigentes...",
            "De acuerdo con la normativa aplicable...",
            "Basándome en los lineamientos regulatorios...",
            "Conforme a las disposiciones legales..."
        ]
    
    def get_greeting(self, is_new_conversation: bool = True) -> str:
        """Obtener saludo apropiado"""
        if is_new_conversation:
            return random.choice(self.greetings)
        else:
            return "Continuemos con tu consulta de cumplimiento, kawiller. ¿Qué más necesitas saber?"
    
    def get_farewell(self) -> str:
        """Obtener despedida apropiada"""
        return random.choice(self.farewells)
    
    def get_confirmation(self) -> str:
        """Obtener confirmación de entendimiento"""
        return random.choice(self.confirmations)
    
    def get_processing_message(self) -> str:
        """Obtener mensaje de procesamiento"""
        return random.choice(self.processing)
    
    def get_clarification(self, topic: str) -> str:
        """Obtener solicitud de clarificación"""
        base = random.choice(self.clarifications)
        return f"{base} {topic}"
    
    def get_regulatory_intro(self) -> str:
        """Obtener introducción regulatoria"""
        return random.choice(self.regulatory_context)
    
    def format_professional_response(self, content: str, include_greeting: bool = False) -> str:
        """Formatear respuesta de manera profesional"""
        parts = []
        
        if include_greeting:
            parts.append(self.get_greeting())
        
        parts.append(content)
        
        return "\n\n".join(parts)
    
    def get_conversation_summary_prompt(self, context: str) -> str:
        """Generar prompt para resumir conversación"""
        return f"""
        Como oficial de cumplimiento de Vizum, genera un resumen profesional y conciso de la siguiente conversación.
        Enfócate en los puntos clave de cumplimiento regulatorio discutidos.
        
        Contexto de la conversación:
        {context}
        
        Resumen (máximo 2-3 oraciones):
        """
    
    def get_enhanced_prompt(self, user_question: str, conversation_context: str = "", pinecone_context: str = "", user_learning_context: str = "") -> Dict[str, str]:
        """Generar prompt mejorado para el modelo"""
        
        system_prompt = f"""
        Eres {self.name}, un asistente de IA especializado en cumplimiento regulatorio para {self.company}.
        
        Tu rol como {self.role} incluye:
        - Proporcionar orientación sobre regulaciones financieras y de cumplimiento
        - Analizar documentos y políticas de cumplimiento
        - Responder consultas sobre auditorías y reportes regulatorios
        - Mantener un tono profesional, respetuoso y confiable
        - Ser preciso y basar tus respuestas en la información disponible
        - Aprender de las interacciones previas con cada usuario para personalizar las respuestas
        
        Instrucciones de comunicación:
        - Usa un tono profesional pero accesible
        - Sé claro y directo en tus explicaciones
        - Cuando sea apropiado, cita regulaciones específicas
        - Si no estás seguro de algo, indícalo claramente
        - Ofrece información adicional cuando sea relevante
        - Considera el historial del usuario para proporcionar respuestas más relevantes
        """
        
        context_parts = []
        
        if conversation_context:
            context_parts.append(f"Historial de la conversación:\n{conversation_context}")
        
        if user_learning_context:
            context_parts.append(f"Contexto de aprendizaje del usuario:\n{user_learning_context}")
        
        if pinecone_context:
            context_parts.append(f"Información relevante de documentos:\n{pinecone_context}")
        
        context_text = "\n\n".join(context_parts) if context_parts else ""
        
        user_prompt = f"""
        Pregunta del usuario: {user_question}
        
        {context_text}
        
        Responde de manera profesional y completa, considerando el contexto de la conversación, el historial del usuario y la información disponible.
        """
        
        return {
            "system": system_prompt,
            "user": user_prompt
        }
    
    def get_file_processing_message(self, filename: str, with_ocr: bool = False) -> str:
        """Mensaje para procesamiento de archivos"""
        if with_ocr:
            return f"🔍 ¡Atención kawiller! Detecté que el archivo *{filename}* requiere procesamiento OCR. Estoy extrayendo el texto con reconocimiento de caracteres. Esto puede tomar unos momentos..."
        else:
            return f"📄 Kawiller, estoy procesando el archivo *{filename}* para extraer información relevante de cumplimiento..."
    
    def get_file_completion_message(self, filename: str, chunks_count: int, with_ocr: bool = False) -> str:
        """Mensaje de completado de procesamiento"""
        ocr_text = " con OCR" if with_ocr else ""
        return f"✅ ¡Listo kawiller! He terminado de procesar el archivo *{filename}*{ocr_text} y lo agregué a la base de conocimiento ({chunks_count} secciones). Ahora puedo responder preguntas sobre su contenido."
    
    def get_error_message(self, error: str) -> str:
        """Mensaje de error profesional"""
        return f"Kawiller, lamento los inconvenientes. He encontrado un problema técnico: {error}. Por favor, intenta nuevamente o contacta al equipo de soporte si el problema persiste."

    def get_thread_followup_message(self) -> str:
        """Mensaje de seguimiento explícito en hilos"""
        return "Kawiller, continúo con tu consulta en este hilo. Si tienes más preguntas, solo escríbelas aquí."

    def get_inactivity_warning_message(self) -> str:
        """Mensaje de advertencia por inactividad en el hilo"""
        return "Kawiller, ¿seguirás con la consulta? Si no recibo respuesta en breve, cerraré este hilo. Puedes reactivarlo enviando un nuevo mensaje."

    def get_thread_closed_message(self) -> str:
        """Mensaje de cierre de hilo por inactividad"""
        return "Hilo cerrado por inactividad. Si necesitas continuar, solo escribe un nuevo mensaje en este hilo y lo reactivaré." 