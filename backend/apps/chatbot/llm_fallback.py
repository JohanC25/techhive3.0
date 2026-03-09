"""
Fallback LLM para el chatbot TechHive.
Se invoca SOLO cuando el router regex no detecta intención (desconocido).
Usa claude-haiku para velocidad y bajo costo.

Flujo:
  regex (alta confianza, gratis) → si desconocido → Claude API (fallback pago)
"""

import os
import anthropic

_client = None


def _get_client() -> anthropic.Anthropic | None:
    """Retorna el cliente de Anthropic, o None si no hay API key configurada."""
    global _client
    if _client is not None:
        return _client
    api_key = os.getenv('ANTHROPIC_API_KEY', '')
    if not api_key:
        return None
    _client = anthropic.Anthropic(api_key=api_key)
    return _client


def fallback_staff(texto: str) -> str | None:
    """
    Fallback para el chatbot de staff.
    Claude conoce el contexto del ERP (ventas, inventario, caja)
    pero NO tiene acceso a la BD — ayuda a redirigir al usuario.
    Retorna None si no hay API key configurada.
    """
    client = _get_client()
    if not client:
        return None

    system = (
        "Eres el asistente comercial de TechHive ERP. "
        "Ayudas al equipo con consultas de negocio.\n\n"
        "Puedo responder preguntas sobre:\n"
        "• Ventas del día, semana, mes o período específico\n"
        "• Productos más vendidos o búsqueda de ventas por producto\n"
        "• Comparación entre períodos (ej: enero vs febrero)\n"
        "• Tendencias y evolución de ventas\n\n"
        "Si la consulta es ambigua, intenta interpretarla como una de las opciones anteriores "
        "y sugiere la forma exacta de preguntarla. "
        "Responde en español, máximo 4 líneas. Sé directo y útil."
    )

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            system=system,
            messages=[{"role": "user", "content": texto}],
        )
        return response.content[0].text
    except Exception:
        return None


def fallback_cliente(texto: str, categorias: list[str] | None = None) -> str | None:
    """
    Fallback para el chatbot de clientes.
    Claude conoce las categorías del catálogo y ayuda a encontrar productos.
    Retorna None si no hay API key configurada.
    """
    client = _get_client()
    if not client:
        return None

    contexto_categorias = ""
    if categorias:
        lista = ", ".join(categorias)
        contexto_categorias = f"\n\nCategorías disponibles en el catálogo: {lista}."

    system = (
        "Eres el asistente de compras de TechHive. "
        "Tu única función es ayudar a los clientes a encontrar productos en el catálogo."
        f"{contexto_categorias}\n\n"
        "Si el cliente describe lo que necesita (aunque no sepa el nombre exacto), "
        "mapea su necesidad a las categorías disponibles y sugiere cómo buscarlo. "
        "Responde en español, máximo 3-4 líneas. Sé amigable y comercial. "
        "NO inventes precios ni disponibilidad. "
        "Si pregunta algo fuera de compras, redirige amablemente al catálogo."
    )

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            system=system,
            messages=[{"role": "user", "content": texto}],
        )
        return response.content[0].text
    except Exception:
        return None
