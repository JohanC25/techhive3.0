"""
Views del chatbot TechHive.
Endpoint principal que recibe mensajes y devuelve respuestas.
"""

import uuid
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import ChatSession, ChatMessage
from .router import detectar_intencion
from .handlers import ejecutar_intencion


@api_view(['POST'])
@permission_classes([AllowAny])
def enviar_mensaje(request):
    """
    POST /api/chatbot/mensaje/
    Body: { "mensaje": "¿Cuánto vendimos hoy?", "session_id": "opcional-uuid" }
    Response: { "respuesta": "...", "intent": "...", "session_id": "..." }
    """
    mensaje = request.data.get('mensaje', '').strip()
    session_id = request.data.get('session_id', '')

    if not mensaje:
        return Response(
            {'error': 'El campo "mensaje" es requerido.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(mensaje) > 500:
        return Response(
            {'error': 'El mensaje no puede superar los 500 caracteres.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Obtener o crear sesión
    if not session_id:
        session_id = str(uuid.uuid4())

    # Detectar schema del tenant activo
    # Con django-tenants, connection.schema_name tiene el schema actual
    try:
        from django.db import connection
        tenant_schema = connection.schema_name
    except Exception:
        tenant_schema = 'public'

    session, _ = ChatSession.objects.get_or_create(
        session_id=session_id,
        defaults={'tenant_schema': tenant_schema}
    )

    # Guardar mensaje del usuario
    ChatMessage.objects.create(
        session=session,
        role='user',
        content=mensaje,
    )

    # Procesar con el router
    resultado_router = detectar_intencion(mensaje)
    intent = resultado_router['intent']

    # Ejecutar handler correspondiente
    respuesta = ejecutar_intencion(resultado_router)

    # Guardar respuesta del bot
    ChatMessage.objects.create(
        session=session,
        role='bot',
        content=respuesta,
        intent=intent,
    )

    return Response({
        'respuesta': respuesta,
        'intent': intent,
        'session_id': session_id,
        'confianza': resultado_router.get('confianza', 'baja'),
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def historial_sesion(request, session_id):
    """
    GET /api/chatbot/historial/<session_id>/
    Retorna el historial de mensajes de una sesión.
    """
    try:
        session = ChatSession.objects.get(session_id=session_id)
    except ChatSession.DoesNotExist:
        return Response(
            {'error': 'Sesión no encontrada.'},
            status=status.HTTP_404_NOT_FOUND
        )

    mensajes = session.messages.all().values(
        'role', 'content', 'intent', 'created_at'
    )

    return Response({
        'session_id': session_id,
        'mensajes': list(mensajes),
    })


@api_view(['DELETE'])
@permission_classes([AllowAny])
def limpiar_sesion(request, session_id):
    """
    DELETE /api/chatbot/historial/<session_id>/
    Elimina el historial de una sesión (nuevo chat).
    """
    ChatSession.objects.filter(session_id=session_id).delete()
    return Response({'mensaje': 'Sesión eliminada correctamente.'})


@api_view(['GET'])
def health_check(request):
    """GET /api/chatbot/health/ — verifica que el chatbot está activo"""
    return Response({'status': 'ok', 'servicio': 'chatbot-techhive'})
