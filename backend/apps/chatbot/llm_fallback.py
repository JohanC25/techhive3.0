"""
Fallback LLM para el chatbot TechHive.
Se invoca SOLO cuando el router regex no detecta intención (desconocido)
Y la consulta pasa el scope guard de dominio.

Flujo:
  regex (alta confianza, gratis)
    → si desconocido → scope guard
        → fuera de dominio → respuesta estática (sin LLM)
        → dentro de dominio → GPT-4o mini (fallback pago, acotado al negocio)
"""

import re
import os
import unicodedata
from openai import OpenAI

_client = None


# ─────────────────────────────────────────────
# SCOPE GUARD
# ─────────────────────────────────────────────

_DOMAIN_KEYWORDS_STAFF = {
    'venta', 'ventas', 'vender', 'vendimos', 'vendido', 'vendiste', 'vendi',
    'compra', 'compras', 'proveedor',
    'producto', 'productos', 'articulo', 'articulos', 'item', 'items',
    'inventario', 'stock', 'existencia', 'existencias',
    'caja', 'balance', 'ingreso', 'ingresos', 'egreso', 'egresos',
    'prediccion', 'proyeccion', 'forecast', 'estimado', 'estimacion',
    'semana', 'mes', 'meses', 'periodo', 'periodos', 'ano', 'anual',
    'ticket', 'servicio', 'tecnico',
    'categoria', 'categorias', 'precio', 'precios', 'costo', 'costos',
    'factura', 'cobro', 'pago', 'total', 'tendencia', 'comparar',
    'dashboard', 'reporte', 'informe',
}

_DOMAIN_KEYWORDS_CLIENTE = {
    'producto', 'productos', 'articulo', 'articulos',
    'precio', 'precios', 'cuesta', 'vale', 'costo',
    'stock', 'disponible', 'disponibles', 'existencia',
    'categoria', 'categorias', 'catalogo',
    'comprar', 'adquirir', 'conseguir',
    'hay', 'tienen', 'tienes', 'buscar', 'busco',
    'oferta', 'descuento', 'promocion',
}


def _normalizar(texto: str) -> str:
    """Convierte a minúsculas y elimina tildes para comparación."""
    nfkd = unicodedata.normalize('NFKD', texto.lower())
    return ''.join(c for c in nfkd if not unicodedata.combining(c))


def is_in_domain(message: str, canal: str) -> bool:
    """
    Determina si un mensaje pertenece al dominio TechHive.

    Retorna True si la consulta menciona términos del negocio
    (ventas, inventario, caja, productos, predicciones, etc.)
    según el canal ('staff' o 'cliente').
    """
    texto = _normalizar(message)
    keywords = _DOMAIN_KEYWORDS_STAFF if canal == 'staff' else _DOMAIN_KEYWORDS_CLIENTE
    palabras = set(re.findall(r'\b[a-z]+\b', texto))
    return bool(palabras & keywords)


def out_of_domain_response(canal: str) -> str:
    """Respuesta estática para consultas fuera del dominio de TechHive."""
    if canal == 'staff':
        return (
            "Lo siento, solo puedo ayudarte con consultas sobre el negocio. "
            "¿En qué puedo ayudarte?\n\n"
            "Por ejemplo puedes preguntarme:\n"
            "• \"¿Cuánto vendimos hoy?\"\n"
            "• \"¿Qué productos tienen bajo stock?\"\n"
            "• \"¿Cuál es el balance de caja?\"\n"
            "• \"Compara enero con febrero\""
        )
    return (
        "Solo puedo ayudarte con consultas sobre nuestro catálogo de productos. "
        "¿Estás buscando algo en particular?\n\n"
        "Por ejemplo:\n"
        "• \"¿Cuánto cuesta el laptop?\"\n"
        "• \"¿Hay auriculares disponibles?\"\n"
        "• \"¿Qué categorías tienen?\""
    )


# ─────────────────────────────────────────────
# CLIENTE OPENAI
# ─────────────────────────────────────────────

def _get_client() -> OpenAI | None:
    """Retorna el cliente de OpenAI, o None si no hay API key configurada."""
    global _client
    if _client is not None:
        return _client
    api_key = os.getenv('OPENAI_API_KEY', '')
    if not api_key:
        return None
    _client = OpenAI(api_key=api_key)
    return _client


# ─────────────────────────────────────────────
# FALLBACKS LLM (solo se llaman si is_in_domain == True)
# ─────────────────────────────────────────────

def fallback_staff(texto: str) -> str | None:
    """
    Fallback para el chatbot de staff (dentro del dominio).
    Claude ayuda a reformular o interpretar la consulta de negocio.
    Retorna None si no hay API key configurada.
    """
    client = _get_client()
    if not client:
        return None

    system = (
        "Eres el asistente comercial de TechHive ERP. "
        "SOLO puedes responder consultas sobre el negocio: "
        "ventas, inventario, caja, compras y predicciones de ventas.\n\n"
        "Puedo responder sobre:\n"
        "• Ventas del día, semana, mes o período específico\n"
        "• Productos más vendidos o búsqueda por producto\n"
        "• Comparación entre períodos (ej: enero vs febrero)\n"
        "• Tendencias y evolución de ventas\n"
        "• Balance de caja e ingresos/egresos\n"
        "• Stock e inventario\n\n"
        "Si la consulta no es sobre estos temas, indica que no puedes ayudar "
        "y sugiere una consulta válida del negocio. "
        "NO respondas temas fuera del dominio comercial. "
        "Responde en español, máximo 4 líneas. Sé directo y útil."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=200,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": texto},
            ],
        )
        return response.choices[0].message.content
    except Exception:
        return None


def fallback_cliente(texto: str, categorias: list[str] | None = None) -> str | None:
    """
    Fallback para el chatbot de clientes (dentro del dominio).
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
        "Tu ÚNICA función es ayudar a los clientes a encontrar productos en el catálogo."
        f"{contexto_categorias}\n\n"
        "Si el cliente describe lo que necesita, mapea su necesidad a las categorías "
        "disponibles y sugiere cómo buscarlo. "
        "Responde en español, máximo 3-4 líneas. Sé amigable y comercial. "
        "NO inventes precios ni disponibilidad. "
        "Si pregunta algo fuera de compras/catálogo, redirige amablemente. "
        "NO respondas sobre temas fuera del catálogo de productos."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=200,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": texto},
            ],
        )
        return response.choices[0].message.content
    except Exception:
        return None
