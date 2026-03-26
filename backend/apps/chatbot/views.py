"""
Views del chatbot TechHive.
Endpoint principal que recibe mensajes y devuelve respuestas.
"""

import uuid
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import ChatSession, ChatMessage
from .router import detectar_intencion
from .handlers import ejecutar_intencion
from .client_router import detectar_intencion_cliente
from .client_handlers import ejecutar_intencion_cliente


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enviar_mensaje(request):
    """
    POST /api/chatbot/mensaje/
    Body: { "mensaje": "...", "session_id": "opcional-uuid" }
    Ruta al router de clientes o de staff según el rol del usuario.
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

    # Enrutar según rol: clientes usan el router de catálogo
    es_cliente = getattr(request.user, 'role', '') == 'client'

    if es_cliente:
        resultado_router = detectar_intencion_cliente(mensaje)
        respuesta = ejecutar_intencion_cliente(resultado_router)
    else:
        resultado_router = detectar_intencion(mensaje)
        respuesta = ejecutar_intencion(resultado_router)

    intent = resultado_router['intent']

    # Fallback LLM: cuando el regex no detectó intención, aplicar scope guard primero
    if intent == 'desconocido':
        from .llm_fallback import (
            fallback_staff, fallback_cliente,
            is_in_domain, out_of_domain_response,
        )
        canal = 'cliente' if es_cliente else 'staff'

        if not is_in_domain(mensaje, canal):
            # Fuera del dominio → respuesta estática sin llamar a Haiku
            respuesta = out_of_domain_response(canal)
        elif es_cliente:
            # Dentro del dominio cliente → fallback con contexto de categorías
            try:
                from django.db import connection as conn
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT DISTINCT c.name FROM inventory_category c "
                        "INNER JOIN inventory_product p ON p.category_id = c.id "
                        "WHERE p.is_active = TRUE ORDER BY c.name LIMIT 15"
                    )
                    categorias = [r[0] for r in cur.fetchall()]
            except Exception:
                categorias = []
            llm_resp = fallback_cliente(mensaje, categorias=categorias)
            if llm_resp:
                respuesta = llm_resp
        else:
            # Dentro del dominio staff → fallback con system prompt acotado
            llm_resp = fallback_staff(mensaje)
            if llm_resp:
                respuesta = llm_resp

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
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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
