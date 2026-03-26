"""
Handlers del chatbot para clientes — TechHive.
Solo consulta el catálogo público: nombre, precio, disponibilidad, categoría.
No expone: costo, SKU, stock exacto, datos de ventas ni información interna.
"""

from django.db import connection


# ─────────────────────────────────────────────
# HELPERS DE CONSULTA
# ─────────────────────────────────────────────

def _normalizar(texto: str) -> str:
    """Elimina tildes y convierte a minúsculas para comparaciones."""
    import unicodedata
    texto = texto.lower()
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')


def query_catalogo(search: str = '', only_available: bool = False) -> list:
    """Consulta productos del catálogo del tenant activo.
    El filtrado por texto se hace en Python (tolerante a tildes y plurales).
    """
    try:
        sql = """
            SELECT
                p.name,
                p.description,
                p.price,
                (p.stock > 0) AS available,
                c.name AS category
            FROM inventory_product p
            LEFT JOIN inventory_category c ON p.category_id = c.id
            WHERE p.is_active = TRUE
        """
        params = []
        if only_available:
            sql += " AND p.stock > 0"
        sql += " ORDER BY p.name LIMIT 200"

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            cols = [c[0] for c in cursor.description]
            rows = [dict(zip(cols, row)) for row in cursor.fetchall()]

        if search:
            search_n = _normalizar(search)
            # Palabras de búsqueda, quitando plural simple (cables→cable, audifonos→audifono)
            words = []
            for w in search_n.split():
                if len(w) > 3 and w.endswith('s'):
                    words.append(w[:-1])  # sin la 's' final
                else:
                    words.append(w)
            words = [w for w in words if len(w) > 1]

            def matches(p):
                haystack = _normalizar(
                    f"{p['name']} {p.get('description') or ''} {p.get('category') or ''}"
                )
                return all(w in haystack for w in words)

            rows = [p for p in rows if matches(p)]

        return rows[:10]
    except Exception:
        return []


def query_categorias() -> list:
    """Retorna categorías que tienen al menos un producto activo."""
    try:
        sql = """
            SELECT DISTINCT c.name
            FROM inventory_category c
            INNER JOIN inventory_product p ON p.category_id = c.id
            WHERE p.is_active = TRUE
            ORDER BY c.name
        """
        with connection.cursor() as cursor:
            cursor.execute(sql)
            return [row[0] for row in cursor.fetchall()]
    except Exception:
        return []


def fmt_precio(valor) -> str:
    if valor is None:
        return '$0.00'
    return f'${float(valor):,.2f}'


# ─────────────────────────────────────────────
# HANDLERS
# ─────────────────────────────────────────────

def handle_saludo_cliente(**kwargs) -> str:
    return (
        "¡Hola! Soy el asistente de TechHive 👋\n\n"
        "Puedo ayudarte a:\n"
        "• 🔍 **Buscar productos** en nuestro catálogo\n"
        "• 💰 **Consultar precios** de cualquier artículo\n"
        "• ✅ **Verificar disponibilidad** de stock\n"
        "• 📦 **Explorar categorías** de productos\n"
        "• 🕐 **Consultar horarios** y datos de contacto\n\n"
        "¿Qué estás buscando hoy?"
    )


def handle_ayuda_cliente(**kwargs) -> str:
    return (
        "Aquí tienes ejemplos de lo que puedes preguntarme:\n\n"
        "💰 *Precios:*\n"
        "• \"¿Cuánto cuesta el laptop HP?\"\n"
        "• \"¿Cuál es el precio del mouse?\"\n\n"
        "✅ *Disponibilidad:*\n"
        "• \"¿Tienen teclados disponibles?\"\n"
        "• \"¿Hay auriculares en stock?\"\n\n"
        "🔍 *Buscar productos:*\n"
        "• \"Muéstrame productos de audio\"\n"
        "• \"Busca impresoras\"\n\n"
        "📦 *Categorías:*\n"
        "• \"¿Qué categorías tienen?\"\n"
        "• \"¿Qué tipo de productos venden?\"\n\n"
        "🕐 *Horarios y contacto:*\n"
        "• \"¿A qué hora abren?\"\n"
        "• \"¿Cómo los contacto?\""
    )


def handle_consultar_precio(params: dict, **kwargs) -> str:
    producto = params.get('producto')
    if not producto:
        return (
            "¿De qué producto quieres saber el precio? "
            "Intenta: \"¿Cuánto cuesta el laptop?\""
        )

    resultados = query_catalogo(search=producto)
    if not resultados:
        return (
            f"No encontré productos que coincidan con **\"{producto}\"**.\n"
            f"Intenta con otro nombre o escribe **categorías** para ver lo que tenemos."
        )

    if len(resultados) == 1:
        p = resultados[0]
        estado = "✅ Disponible" if p['available'] else "❌ Sin stock"
        lineas = [
            f"💰 **{p['name']}**\n",
            f"• Precio: **{fmt_precio(p['price'])}**",
            f"• Estado: {estado}",
        ]
        if p['category']:
            lineas.append(f"• Categoría: {p['category']}")
        return '\n'.join(lineas)

    lineas = [f"💰 **Productos que coinciden con \"{producto}\":**\n"]
    for p in resultados[:6]:
        estado = "✅" if p['available'] else "❌"
        lineas.append(f"• {estado} **{p['name']}** — {fmt_precio(p['price'])}")
    return '\n'.join(lineas)


def handle_verificar_disponibilidad(params: dict, **kwargs) -> str:
    producto = params.get('producto')
    if not producto:
        return (
            "¿Qué producto quieres verificar? "
            "Intenta: \"¿Hay laptops disponibles?\""
        )

    resultados = query_catalogo(search=producto)
    if not resultados:
        return (
            f"No encontré **\"{producto}\"** en nuestro catálogo. "
            f"Puede que no esté registrado. Escribe **categorías** para ver lo que tenemos."
        )

    disponibles = [p for p in resultados if p['available']]
    sin_stock = [p for p in resultados if not p['available']]

    if disponibles:
        lineas = [f"✅ **Disponible(s) — \"{producto}\":**\n"]
        for p in disponibles[:5]:
            lineas.append(f"• **{p['name']}** — {fmt_precio(p['price'])}")
        if sin_stock:
            nombres = ', '.join(p['name'] for p in sin_stock[:3])
            lineas.append(f"\n❌ Sin stock: {nombres}")
        return '\n'.join(lineas)
    else:
        nombres = ', '.join(p['name'] for p in sin_stock[:3])
        return (
            f"❌ **\"{producto}\"** está momentáneamente sin stock.\n"
            f"Artículos afectados: {nombres}\n\n"
            f"Te recomendamos consultar pronto por reposición."
        )


def handle_buscar_catalogo(params: dict, **kwargs) -> str:
    producto = params.get('producto')
    resultados = query_catalogo(search=producto or '')

    if not resultados:
        if producto:
            return (
                f"No encontré productos relacionados con **\"{producto}\"**.\n"
                f"Escribe **categorías** para ver lo que tenemos disponible."
            )
        return "No hay productos en el catálogo por el momento."

    titulo = f"Resultados para **\"{producto}\"**" if producto else "**Catálogo de productos**"
    lineas = [f"🔍 {titulo}:\n"]
    for p in resultados:
        estado = "✅" if p['available'] else "❌"
        cat = f" [{p['category']}]" if p['category'] else ""
        lineas.append(f"• {estado} **{p['name']}**{cat} — {fmt_precio(p['price'])}")
    if len(resultados) == 10:
        lineas.append("\n_Mostrando los primeros 10 resultados. Sé más específico para filtrar mejor._")
    return '\n'.join(lineas)


def handle_listar_categorias(**kwargs) -> str:
    categorias = query_categorias()
    if not categorias:
        return "No hay categorías de productos registradas por el momento."

    lineas = ["📦 **Categorías de productos disponibles:**\n"]
    for cat in categorias:
        lineas.append(f"• {cat}")
    lineas.append("\n_Pregúntame por cualquier categoría para ver sus productos._")
    return '\n'.join(lineas)


def handle_horarios_contacto(**kwargs) -> str:
    """
    Responde sobre horarios de atención y contacto del tenant activo.
    Intenta obtener el nombre de la empresa desde el schema público.
    Si los datos de contacto no están configurados, devuelve un fallback genérico.
    """
    empresa = "nuestra empresa"
    try:
        from django.db import connection as conn
        schema = conn.schema_name
        with conn.cursor() as cur:
            cur.execute(
                "SELECT name FROM public.tenants_company WHERE schema_name = %s",
                [schema]
            )
            row = cur.fetchone()
            if row:
                empresa = row[0]
    except Exception:
        pass

    return (
        f"Para conocer los **horarios de atención** y datos de contacto de **{empresa}**, "
        "te recomendamos comunicarte directamente con nosotros.\n\n"
        "Mientras tanto, puedo ayudarte con:\n"
        "• 💰 Consultar precios de productos\n"
        "• ✅ Verificar disponibilidad\n"
        "• 🔍 Buscar en nuestro catálogo"
    )


def handle_desconocido_cliente(texto: str, **kwargs) -> str:
    return (
        f"No entendí bien tu consulta: *\"{texto}\"*\n\n"
        "Puedes preguntarme:\n"
        "• \"¿Cuánto cuesta el laptop?\"\n"
        "• \"¿Tienen auriculares disponibles?\"\n"
        "• \"Muéstrame productos de audio\"\n"
        "• \"¿Qué categorías tienen?\"\n\n"
        "O escribe **ayuda** para ver más ejemplos."
    )


# ─────────────────────────────────────────────
# DISPATCHER
# ─────────────────────────────────────────────

CLIENT_HANDLERS = {
    'saludo':                   handle_saludo_cliente,
    'ayuda':                    handle_ayuda_cliente,
    'horarios_contacto':        handle_horarios_contacto,
    'consultar_precio':         handle_consultar_precio,
    'verificar_disponibilidad': handle_verificar_disponibilidad,
    'buscar_catalogo':          handle_buscar_catalogo,
    'listar_categorias':        handle_listar_categorias,
    'desconocido':              handle_desconocido_cliente,
}


def ejecutar_intencion_cliente(resultado_router: dict) -> str:
    """Recibe el output del client_router y ejecuta el handler correspondiente."""
    intent = resultado_router.get('intent', 'desconocido')
    params = resultado_router.get('params', {})
    texto = resultado_router.get('texto_original', '')

    handler = CLIENT_HANDLERS.get(intent, handle_desconocido_cliente)
    return handler(params=params, texto=texto)
