# Cambios en la Lógica de Temporizadores de Inactividad

## Resumen de Cambios

Se han realizado los siguientes ajustes para mejorar el comportamiento del bot en cuanto a la gestión de conversaciones inactivas:

### 1. Tiempos Ajustados
- **Antes**: 2.5 minutos → mensaje de advertencia → 30 segundos → cierre
- **Ahora**: 3 minutos → mensaje de advertencia → 2 minutos → cierre
- **Total**: 5 minutos de inactividad total antes del cierre

### 2. Constantes Modificadas
```python
# slack_bot.py
INACTIVITY_WARNING_SECONDS = 180  # 3 minutos antes del mensaje de advertencia
INACTIVITY_CLOSE_SECONDS = 120    # 2 minutos después del mensaje de advertencia para cerrar

# conversation_manager.py
auto_close_minutes = 5  # Tiempo total antes del cierre automático
```

### 3. Lógica Mejorada
- **Verificación de actividad**: Antes de mostrar el mensaje de advertencia, se verifica si realmente han pasado 3 minutos sin actividad
- **Reprogramación inteligente**: Si hay actividad reciente, el temporizador se reprograma automáticamente
- **Cancelación robusta**: Mejor manejo de errores al cancelar temporizadores
- **Limpieza de memoria**: Los temporizadores se limpian correctamente cuando ya no son necesarios

### 4. Logs de Depuración
Se agregaron prints de depuración para rastrear:
- Cuándo se inician los temporizadores
- Cuándo se ejecutan las funciones de advertencia y cierre
- Tiempos transcurridos desde la última actividad
- Reprogramación de temporizadores
- Limpieza de temporizadores

## Comportamiento Esperado

### Durante Comunicación Activa
- ✅ **NO se muestran mensajes de cierre** mientras hay comunicación activa
- ✅ Los temporizadores se cancelan y reinician con cada mensaje
- ✅ El contexto se mantiene correctamente en los hilos

### Después de 3 Minutos de Inactividad
- ⚠️ Se muestra el mensaje: *"Kawiller, ¿seguirás con la consulta? Si no recibo respuesta en breve, cerraré este hilo."*

### Después de 2 Minutos Adicionales Sin Respuesta
- 🔒 Se cierra la conversación con el mensaje: *"Hilo cerrado por inactividad. Si necesitas continuar, solo escribe un nuevo mensaje."*

### Si Hay Actividad Durante la Advertencia
- ✅ Se cancela el temporizador de cierre
- ✅ La conversación continúa normalmente
- ✅ Se reinicia el ciclo de 3 minutos

## Archivos Modificados

1. **slack_bot.py**
   - Líneas 77-78: Nuevas constantes de tiempo
   - Líneas 185-195: Mejorada cancelación de temporizadores
   - Líneas 207-250: Lógica mejorada de temporizadores con verificaciones
   - Línea 320: Mensaje actualizado en estadísticas

2. **conversation_manager.py**
   - Línea 41: Tiempo de auto-cierre ajustado a 5 minutos

3. **test_timers.py** (nuevo)
   - Script de prueba para verificar la lógica sin afectar el bot en producción

## Instrucciones de Prueba

### 1. Reiniciar el Bot
```bash
# Detener el bot actual
pkill -f slack_bot.py

# Reiniciar con los nuevos cambios
nohup python slack_bot.py > nohup.out 2>&1 &
```

### 2. Verificar Logs
```bash
# Monitorear logs en tiempo real
tail -f nohup.out

# Ver logs recientes
tail -30 nohup.out
```

### 3. Probar Comportamiento
1. **Iniciar una conversación** en Slack
2. **Enviar varios mensajes** para verificar que no aparecen mensajes de cierre
3. **Esperar 3 minutos** sin enviar mensajes
4. **Verificar** que aparece el mensaje de advertencia
5. **Enviar un mensaje** durante la advertencia para verificar que no se cierra
6. **Esperar 2 minutos adicionales** sin actividad para verificar el cierre

### 4. Probar Script de Prueba (Opcional)
```bash
# Ejecutar script de prueba
python test_timers.py
```

## Logs Esperados

Durante el funcionamiento normal, deberías ver logs como:
```
DEBUG: Temporizador de inactividad iniciado para thread 1234567890.123456 (180s)
DEBUG: Temporizador cancelado para thread 1234567890.123456
DEBUG: Función inactivity_warning ejecutada para thread 1234567890.123456
DEBUG: Tiempo desde última actividad: 180.5s
DEBUG: Mostrando mensaje de advertencia para thread 1234567890.123456
DEBUG: Temporizador de cierre iniciado para thread 1234567890.123456
```

## Notas Importantes

- Los errores de linter sobre importaciones no afectan la funcionalidad
- El bot mantiene compatibilidad con conversaciones existentes
- Los temporizadores se manejan de forma independiente por cada hilo
- La lógica es robusta contra condiciones de carrera 