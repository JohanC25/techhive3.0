"""
Router de intenciones del chatbot para clientes — TechHive v1.
Orientado exclusivamente al catálogo: precios, disponibilidad y búsqueda.
No expone información de ventas, costos ni stock exacto.
"""

import re
try:
    from .router import normalizar
except ImportError:
    from router import normalizar


# ─────────────────────────────────────────────
# PATRONES — orden importa: más específico primero
# ─────────────────────────────────────────────

CLIENT_INTENT_PATTERNS = {
    'saludo': [
        r'\b(hola|buenas|buenos dias|buenas tardes|buenas noches|hey|hi|saludos)\b',
    ],
    'ayuda': [
        r'\b(ayuda|ayudame|que puedes hacer|para que sirves|como funciona|que haces|comandos)\b',
        r'\b(en que me ayudas|como te uso)\b',
    ],
    'listar_categorias': [
        r'\b(categorias|tipos de producto|que productos tienen|que tipo de productos)\b',
        r'\b(cuales son las categorias|ver categorias|mostrar categorias|lineas de productos)\b',
        r'\bque\b.{0,20}\b(venden|manejan|ofrecen|trabajan|tienen)\b',
    ],
    # Precio ANTES que disponibilidad y buscar_catalogo (más específico)
    'consultar_precio': [
        r'\b(cuanto cuesta|cuanto vale|cuanto sale|cual es el precio|precio de|precio del|cuanto es)\b',
        r'\bprecio\b.{0,20}\bde\b',
        r'\bcuanto.{0,10}(cuesta|vale|sale)\b',
    ],
    'verificar_disponibilidad': [
        r'\b(hay|tienen|tienes|existe|lo tienen|lo tienes|cuentan con)\b.{1,40}',
        r'\b(esta disponible|tiene stock|hay stock|en stock|disponible|en existencia)\b',
        r'\b(puedo comprar|puedo conseguir|se puede conseguir|lo puedo encontrar)\b',
    ],
    'buscar_catalogo': [
        r'\b(busca|buscar|busco|muestra|mostrar|ver|quiero ver|dame|ensenme|muestrame)\b.{1,40}',
        r'\b(productos de|articulos de|que tienen de|catalogo de)\b',
        r'\bver (el )?catalogo\b',
    ],
}

# Orden de evaluación de intenciones
PRIORITY_ORDER = [
    'saludo',
    'ayuda',
    'listar_categorias',
    'consultar_precio',
    'verificar_disponibilidad',
    'buscar_catalogo',
]


# ─────────────────────────────────────────────
# EXTRACCIÓN DE PRODUCTO
# ─────────────────────────────────────────────

def extraer_nombre_producto_cliente(texto: str) -> str | None:
    """Extrae el nombre del producto de una consulta de cliente."""
    texto_n = normalizar(texto)
    patrones = [
        r'cuanto cuesta (?:el |la |los |las |un |una )?(.+)',
        r'cuanto vale (?:el |la |los |las |un |una )?(.+)',
        r'precio de(?:l)? (?:el |la |los |las |un |una )?(.+)',
        r'hay (?:el |la |los |las |un |una )?(.+)',
        r'tienen (?:el |la |los |las |un |una )?(.+)',
        r'tienes (?:el |la |los |las |un |una )?(.+)',
        r'cuentan con (?:el |la |los |las |un |una )?(.+)',
        r'esta disponible (?:el |la |los |las |un |una )?(.+)',
        r'busca(?:r)? (?:el |la |los |las |un |una )?(.+)',
        r'muestra(?:me)? (?:el |la |los |las |un |una )?(.+)',
        r'muestrame (?:el |la |los |las |un |una )?(.+)',
        r'quiero ver (?:el |la |los |las |un |una )?(.+)',
        r'dame (?:el |la |los |las |un |una )?(.+)',
        r'ver (?:el |la |los |las |un |una )?(.+)',
        r'productos de (.+)',
        r'articulos de (.+)',
        r'catalogo de (.+)',
    ]
    for patron in patrones:
        match = re.search(patron, texto_n)
        if match:
            nombre = match.group(1).strip()
            # Limpiar artículos y palabras sobrantes al final
            nombre = re.sub(
                r'\b(en stock|disponible|ahora|por favor|porfavor|gracias|'
                r'hoy|disponibles|please)\s*$',
                '', nombre
            ).strip()
            nombre = re.sub(r'\s+', ' ', nombre).strip()
            if len(nombre) > 2:
                return nombre
    return None


# ─────────────────────────────────────────────
# FUNCIÓN PRINCIPAL
# ─────────────────────────────────────────────

def detectar_intencion_cliente(texto: str) -> dict:
    """
    Detecta la intención de un mensaje de cliente.
    Retorna dict compatible con ejecutar_intencion_cliente().
    """
    texto_n = normalizar(texto)

    intent_detectado = 'desconocido'
    confianza = 'baja'

    for intent in PRIORITY_ORDER:
        for patron in CLIENT_INTENT_PATTERNS.get(intent, []):
            if re.search(patron, texto_n):
                intent_detectado = intent
                confianza = 'alta'
                break
        if intent_detectado != 'desconocido':
            break

    producto = extraer_nombre_producto_cliente(texto)

    return {
        'intent': intent_detectado,
        'params': {'producto': producto},
        'confianza': confianza,
        'texto_original': texto,
    }
