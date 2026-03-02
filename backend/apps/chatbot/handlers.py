"""
Handlers del chatbot TechHive.
Cada función recibe los parámetros extraídos por el router,
consulta la BD del tenant activo y retorna una respuesta en lenguaje natural.
"""

from datetime import date, timedelta
from django.db import connection


# ─────────────────────────────────────────────
# HELPER: ejecutar query en el schema del tenant
# ─────────────────────────────────────────────

def query_tenant(sql: str, params: list = None) -> list:
    """
    Ejecuta una query raw en la conexión actual.
    En arquitectura multi-tenant con django-tenants, el schema
    ya está seteado en el middleware según el dominio del request.
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def formatear_monto(valor) -> str:
    """Formatea un número como moneda: $1,234.56"""
    if valor is None:
        return '$0.00'
    return f'${float(valor):,.2f}'


def formatear_periodo(fecha_inicio: str, fecha_fin: str) -> str:
    """Convierte fechas a texto legible"""
    if fecha_inicio == fecha_fin:
        return f"el {fecha_inicio}"
    return f"del {fecha_inicio} al {fecha_fin}"


# ─────────────────────────────────────────────
# HANDLERS POR INTENCIÓN
# ─────────────────────────────────────────────

def handle_saludo(**kwargs) -> str:
    return (
        "¡Hola! Soy el asistente de TechHive 👋\n\n"
        "Puedo ayudarte con:\n"
        "• 📊 **Ventas del día, semana o mes**\n"
        "• 🏆 **Productos más vendidos**\n"
        "• 📈 **Tendencias y comparaciones**\n"
        "• 🔮 **Predicciones de ventas** (próximamente)\n\n"
        "¿Qué quieres consultar?"
    )


def handle_ayuda(**kwargs) -> str:
    return (
        "Aquí tienes ejemplos de lo que puedes preguntarme:\n\n"
        "🗓️ *Ventas por período:*\n"
        "• \"¿Cuánto vendimos hoy?\"\n"
        "• \"Total de ventas de enero\"\n"
        "• \"Resumen de la semana pasada\"\n\n"
        "🏆 *Productos:*\n"
        "• \"¿Cuál es el producto más vendido?\"\n"
        "• \"¿Cuánto vendimos de impresiones?\"\n\n"
        "📈 *Comparaciones:*\n"
        "• \"Compara enero vs febrero\"\n"
        "• \"¿Cómo van las ventas este mes?\"\n\n"
        "🔮 *Predicciones:*\n"
        "• \"¿Cuánto vamos a vender la próxima semana?\""
    )


def handle_ventas_hoy(**kwargs) -> str:
    hoy = date.today().strftime('%Y-%m-%d')
    try:
        resultado = query_tenant(
            "SELECT COUNT(*) as transacciones, SUM(total) as total_ventas "
            "FROM ventas_venta WHERE DATE(fecha_venta) = %s",
            [hoy]
        )
        if resultado and resultado[0]['total_ventas']:
            r = resultado[0]
            return (
                f"📊 **Ventas de hoy ({hoy}):**\n"
                f"• Total: **{formatear_monto(r['total_ventas'])}**\n"
                f"• Transacciones: **{r['transacciones']}**"
            )
        else:
            return f"No se registraron ventas hoy ({hoy}) todavía."
    except Exception as e:
        return _error_bd(str(e))


def handle_ventas_ayer(**kwargs) -> str:
    ayer = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    try:
        resultado = query_tenant(
            "SELECT COUNT(*) as transacciones, SUM(total) as total_ventas "
            "FROM ventas_venta WHERE DATE(fecha_venta) = %s",
            [ayer]
        )
        if resultado and resultado[0]['total_ventas']:
            r = resultado[0]
            return (
                f"📊 **Ventas de ayer ({ayer}):**\n"
                f"• Total: **{formatear_monto(r['total_ventas'])}**\n"
                f"• Transacciones: **{r['transacciones']}**"
            )
        else:
            return f"No se encontraron ventas para ayer ({ayer})."
    except Exception as e:
        return _error_bd(str(e))


def handle_ventas_por_periodo(params: dict, **kwargs) -> str:
    fecha_inicio = params.get('fecha_inicio')
    fecha_fin = params.get('fecha_fin')

    if not fecha_inicio or not fecha_fin:
        return (
            "No pude detectar el período que quieres consultar. "
            "Intenta con algo como: \"ventas de enero\" o \"ventas de esta semana\"."
        )

    try:
        resultado = query_tenant(
            "SELECT COUNT(*) as transacciones, SUM(total) as total_ventas, "
            "AVG(total) as promedio_venta "
            "FROM ventas_venta WHERE DATE(fecha_venta) BETWEEN %s AND %s",
            [fecha_inicio, fecha_fin]
        )
        periodo = formatear_periodo(fecha_inicio, fecha_fin)
        if resultado and resultado[0]['total_ventas']:
            r = resultado[0]
            return (
                f"📊 **Ventas {periodo}:**\n"
                f"• Total: **{formatear_monto(r['total_ventas'])}**\n"
                f"• Transacciones: **{r['transacciones']}**\n"
                f"• Promedio por venta: **{formatear_monto(r['promedio_venta'])}**"
            )
        else:
            return f"No se encontraron ventas {periodo}."
    except Exception as e:
        return _error_bd(str(e))


def handle_producto_mas_vendido(params: dict, **kwargs) -> str:
    fecha_inicio = params.get('fecha_inicio')
    fecha_fin = params.get('fecha_fin')

    # Si no hay fechas, usar el mes actual
    if not fecha_inicio:
        hoy = date.today()
        fecha_inicio = hoy.replace(day=1).strftime('%Y-%m-%d')
        fecha_fin = hoy.strftime('%Y-%m-%d')
        periodo_texto = "este mes"
    else:
        periodo_texto = formatear_periodo(fecha_inicio, fecha_fin)

    try:
        resultado = query_tenant(
            "SELECT descripcion, COUNT(*) as veces_vendido, SUM(total) as total_generado "
            "FROM ventas_venta "
            "WHERE DATE(fecha_venta) BETWEEN %s AND %s "
            "GROUP BY descripcion "
            "ORDER BY total_generado DESC "
            "LIMIT 5",
            [fecha_inicio, fecha_fin]
        )
        if resultado:
            lineas = [f"🏆 **Top 5 productos más vendidos ({periodo_texto}):**\n"]
            medallas = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣']
            for i, r in enumerate(resultado):
                lineas.append(
                    f"{medallas[i]} {r['descripcion']} — "
                    f"**{formatear_monto(r['total_generado'])}** "
                    f"({r['veces_vendido']} ventas)"
                )
            return '\n'.join(lineas)
        else:
            return f"No se encontraron ventas {periodo_texto}."
    except Exception as e:
        return _error_bd(str(e))


def handle_buscar_producto(params: dict, **kwargs) -> str:
    producto = params.get('producto')
    fecha_inicio = params.get('fecha_inicio')
    fecha_fin = params.get('fecha_fin')

    if not producto:
        return "¿De qué producto quieres ver las ventas? Intenta: \"ventas de impresiones\"."

    if not fecha_inicio:
        hoy = date.today()
        fecha_inicio = hoy.replace(day=1).strftime('%Y-%m-%d')
        fecha_fin = hoy.strftime('%Y-%m-%d')
        periodo_texto = "este mes"
    else:
        periodo_texto = formatear_periodo(fecha_inicio, fecha_fin)

    try:
        resultado = query_tenant(
            "SELECT COUNT(*) as transacciones, SUM(total) as total_ventas "
            "FROM ventas_venta "
            "WHERE LOWER(descripcion) LIKE LOWER(%s) "
            "AND DATE(fecha_venta) BETWEEN %s AND %s",
            [f'%{producto}%', fecha_inicio, fecha_fin]
        )
        if resultado and resultado[0]['total_ventas']:
            r = resultado[0]
            return (
                f"🔍 **Ventas de \"{producto}\" ({periodo_texto}):**\n"
                f"• Total: **{formatear_monto(r['total_ventas'])}**\n"
                f"• Transacciones: **{r['transacciones']}**"
            )
        else:
            return (
                f"No encontré ventas de \"{producto}\" {periodo_texto}. "
                f"Verifica el nombre del producto."
            )
    except Exception as e:
        return _error_bd(str(e))


def handle_comparar_periodos(params: dict, **kwargs) -> str:
    """
    Compara dos períodos. Si el usuario especificó dos meses los usa,
    si no, compara mes actual vs mes anterior.
    """
    rangos = params.get('rangos_comparacion')

    # Si hay dos rangos explícitos del router
    if rangos and rangos.get('rango1') and rangos.get('rango2'):
        r1 = rangos['rango1']
        r2 = rangos['rango2']
        nombre1 = r1['nombre'].capitalize()
        nombre2 = r2['nombre'].capitalize()
        inicio1, fin1 = r1['fecha_inicio'], r1['fecha_fin']
        inicio2, fin2 = r2['fecha_inicio'], r2['fecha_fin']
    else:
        # Fallback: mes actual vs mes anterior
        from datetime import date, timedelta
        hoy = date.today()
        inicio1_d = hoy.replace(day=1)
        fin1_d = hoy
        fin2_d = inicio1_d - timedelta(days=1)
        inicio2_d = fin2_d.replace(day=1)
        inicio1, fin1 = inicio1_d.strftime('%Y-%m-%d'), fin1_d.strftime('%Y-%m-%d')
        inicio2, fin2 = inicio2_d.strftime('%Y-%m-%d'), fin2_d.strftime('%Y-%m-%d')
        nombre1, nombre2 = 'Mes actual', 'Mes anterior'

    try:
        res1 = query_tenant(
            "SELECT COUNT(*) as tx, SUM(total) as total FROM ventas_venta "
            "WHERE DATE(fecha_venta) BETWEEN %s AND %s",
            [inicio1, fin1]
        )
        res2 = query_tenant(
            "SELECT COUNT(*) as tx, SUM(total) as total FROM ventas_venta "
            "WHERE DATE(fecha_venta) BETWEEN %s AND %s",
            [inicio2, fin2]
        )

        total1 = float(res1[0]['total'] or 0)
        total2 = float(res2[0]['total'] or 0)
        tx1 = res1[0]['tx']
        tx2 = res2[0]['tx']

        if total2 > 0:
            variacion = ((total1 - total2) / total2) * 100
            emoji = "📈" if variacion >= 0 else "📉"
            direccion = "más" if variacion >= 0 else "menos"
            comparativa = f"{emoji} **{nombre1}** vendió un **{abs(variacion):.1f}% {direccion}** que **{nombre2}**"
        else:
            comparativa = f"No hay datos de {nombre2} para comparar."

        return (
            f"📊 **Comparación {nombre1} vs {nombre2}:**\n\n"
            f"• {nombre1}: **{formatear_monto(total1)}** ({tx1} ventas)\n"
            f"• {nombre2}: **{formatear_monto(total2)}** ({tx2} ventas)\n\n"
            f"{comparativa}"
        )
    except Exception as e:
        return _error_bd(str(e))


def handle_tendencia(**kwargs) -> str:
    # Últimas 4 semanas
    hoy = date.today()
    lineas = ["📈 **Tendencia de ventas (últimas 4 semanas):**\n"]

    try:
        for i in range(3, -1, -1):
            fin = hoy - timedelta(weeks=i)
            inicio = fin - timedelta(days=6)
            resultado = query_tenant(
                "SELECT SUM(total) as total FROM ventas_venta "
                "WHERE DATE(fecha_venta) BETWEEN %s AND %s",
                [inicio.strftime('%Y-%m-%d'), fin.strftime('%Y-%m-%d')]
            )
            total = float(resultado[0]['total'] or 0) if resultado else 0
            semana_label = "Semana actual" if i == 0 else f"Hace {i} semana(s)"
            lineas.append(f"• {semana_label}: **{formatear_monto(total)}**")
        return '\n'.join(lineas)
    except Exception as e:
        return _error_bd(str(e))


def handle_prediccion(**kwargs) -> str:
    # Mock hasta que el modelo esté listo
    return (
        "🔮 **Predicción de ventas:**\n"
        "El módulo predictivo está en desarrollo. Pronto podrás consultar "
        "proyecciones de ventas para los próximos días y semanas.\n\n"
        "_Mientras tanto puedes consultar tendencias históricas._"
    )


def handle_desconocido(texto: str, **kwargs) -> str:
    return (
        f"No entendí bien tu consulta: *\"{texto}\"*\n\n"
        "Intenta con preguntas como:\n"
        "• \"¿Cuánto vendimos hoy?\"\n"
        "• \"Ventas de enero\"\n"
        "• \"¿Cuál es el producto más vendido?\"\n\n"
        "O escribe **ayuda** para ver todos los ejemplos."
    )


def _error_bd(detalle: str) -> str:
    return (
        "⚠️ Hubo un problema al consultar los datos. "
        "Verifica que la base de datos esté configurada correctamente."
    )


# ─────────────────────────────────────────────
# DISPATCHER — mapea intención → handler
# ─────────────────────────────────────────────

HANDLERS = {
    'saludo': handle_saludo,
    'ayuda': handle_ayuda,
    'ventas_hoy': handle_ventas_hoy,
    'ventas_ayer': handle_ventas_ayer,
    'ventas_por_periodo': handle_ventas_por_periodo,
    'producto_mas_vendido': handle_producto_mas_vendido,
    'buscar_producto': handle_buscar_producto,
    'comparar_periodos': handle_comparar_periodos,
    'tendencia': handle_tendencia,
    'prediccion': handle_prediccion,
    'desconocido': handle_desconocido,
}


def ejecutar_intencion(resultado_router: dict) -> str:
    """
    Recibe el output del router y ejecuta el handler correspondiente.
    """
    intent = resultado_router.get('intent', 'desconocido')
    params = resultado_router.get('params', {})
    texto = resultado_router.get('texto_original', '')

    handler = HANDLERS.get(intent, handle_desconocido)
    return handler(params=params, texto=texto)
