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
    # horarios_contacto ANTES que listar_categorias y verificar_disponibilidad
    # para capturar "que horario tienen" antes de que listar_categorias intercepte
    'horarios_contacto': [
        r'\bhorario\b',
        r'a\s+que\s+hora',
        r'como\s+(?:los\s+)?contact(?:o|an)',
        r'telefono\s+de\s+(?:contacto|la\s+tienda|la\s+empresa|ustedes)',
        r'whatsapp\s+de\s+(?:la\s+tienda|la\s+empresa|contacto|ustedes)',
        r'donde\s+estan\s+ubicados?',
        r'direccion\s+de\s+la\s+(?:tienda|empresa)',
    ],
    'listar_categorias': [
        r'\b(categorias|tipos de producto|que productos tienen|que tipo de productos)\b',
        r'\b(cuales son las categorias|ver categorias|mostrar categorias|lineas de productos)\b',
        r'\bque\b.{0,20}\b(venden|manejan|ofrecen|trabajan|tienen)\b',
    ],
    # Precio ANTES que disponibilidad y buscar_catalogo (más específico)
    'consultar_precio': [
        r'\b(cuanto cuesta|cuanto cuestan|cuanto vale|cuanto valen|cuanto sale|cuanto salen|cual es el precio|precio de|precio del|cuanto es)\b',
        r'\bprecio\b.{0,20}\bde\b',
        r'\bcuanto.{0,10}(cuesta|cuestan|vale|valen|sale)\b',
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
    'horarios_contacto',        # antes de listar_categorias para capturar "que horario tienen"
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
        r'cuanto cuesta(?:n)? (?:el |la |los |las |un |una )?(.+)',
        r'cuanto vale(?:n)? (?:el |la |los |las |un |una )?(.+)',
        r'cuanto sale(?:n)? (?:el |la |los |las |un |una )?(.+)',
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
            # Eliminar frases de ruido (en cualquier posición)
            noise = [
                r'\ben stock\b', r'\bdisponibles?\b', r'\ben existencia\b',
                r'\bpor favor\b', r'\bporfavor\b', r'\bgracias\b', r'\bplease\b',
                r'\bahora\b', r'\bhoy\b',
            ]
            for n in noise:
                nombre = re.sub(n, '', nombre)
            nombre = re.sub(r'\s+', ' ', nombre).strip()
            nombre = re.sub(r'[?!.,;:"\']+$', '', nombre).strip()
            nombre = re.sub(r'^(dentro de|en la|en el|de la|del|de los|de las|en)\s+', '', nombre).strip()
            # Quitar "productos de" al inicio (buscar_catalogo)
            nombre = re.sub(r'^productos? de\s+', '', nombre).strip()
            nombre = re.sub(r'^articulos? de\s+', '', nombre).strip()
            nombre = re.sub(r'^catalogo de\s+', '', nombre).strip()
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
