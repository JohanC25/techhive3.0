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
    'compra', 'compras', 'proveedor', 'proveedores',
    'producto', 'productos', 'articulo', 'articulos', 'item', 'items',
    'inventario', 'stock', 'existencia', 'existencias',
    'caja', 'balance', 'ingreso', 'ingresos', 'egreso', 'egresos',
    'prediccion', 'proyeccion', 'forecast', 'estimado', 'estimacion',
    'semana', 'mes', 'meses', 'periodo', 'periodos', 'ano', 'anual',
    'ticket', 'servicio', 'tecnico',
    'categoria', 'categorias', 'precio', 'precios', 'costo', 'costos',
    'factura', 'cobro', 'pago', 'total', 'tendencia', 'comparar',
    'dashboard', 'reporte', 'informe',
    # estrategia y gestión comercial
    'cliente', 'clientes', 'estrategia', 'estrategias', 'consejo', 'consejos',
    'fidelizar', 'fidelizacion', 'promocion', 'promociones', 'descuento', 'descuentos',
    'aumentar', 'mejorar', 'crecer', 'crecimiento', 'ganancia', 'ganancias',
    'negocio', 'comercial', 'rentabilidad', 'margen', 'utilidad',
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
        "Eres el asistente comercial inteligente de TechHive ERP, "
        "un sistema para pequeñas y medianas empresas ecuatorianas.\n\n"
        "Puedes ayudar con:\n"
        "• Estrategias comerciales: cómo vender más, temporadas, promociones, precios\n"
        "• Gestión de inventario: rotación, reabastecimiento, stock mínimo\n"
        "• Análisis de negocio: tendencias, estacionalidad, indicadores clave\n"
        "• Mejores prácticas para PyMES: atención al cliente, fidelización\n"
        "• Cualquier consulta operativa del negocio\n\n"
        "Contexto: el usuario es dueño o empleado de una tienda pequeña en Ecuador. "
        "Responde con consejos prácticos y concretos, adaptados a su realidad. "
        "Si te preguntan sobre estrategias estacionales (diciembre, feriados, etc.), "
        "da recomendaciones útiles para comercio minorista ecuatoriano. "
        "NO respondas sobre temas completamente ajenos al negocio (política, deportes, etc.). "
        "Responde en español, máximo 5 líneas. Sé directo, práctico y motivador."
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
        "Eres el asistente virtual de TechHive. "
        "Tu ÚNICA función es ayudar a los clientes con el catálogo de productos."
        f"{contexto_categorias}\n\n"
        "SOLO puedes responder sobre:\n"
        "- Productos disponibles en el catálogo\n"
        "- Precios y descripciones de productos\n"
        "- Categorías disponibles\n"
        "- Información general de la tienda (productos, servicios)\n\n"
        "NUNCA respondas sobre:\n"
        "- Ventas internas o facturación de la empresa\n"
        "- Niveles de stock exactos (solo disponible/no disponible)\n"
        "- Costos de adquisición o márgenes\n"
        "- Información de otras empresas o tenants\n"
        "- Predicciones de demanda o proyecciones\n"
        "- Temas fuera del catálogo (clima, noticias, etc.)\n\n"
        "Si la pregunta está fuera de estos temas, responde exactamente: "
        "'Esa información no está disponible. Puedo ayudarte con el catálogo de "
        "productos, precios y disponibilidad.'\n\n"
        "NO inventes precios ni disponibilidad. "
        "Responde en español, máximo 3-4 líneas. Sé amigable y comercial."
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
