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
        "• 🔮 **Predicciones de ventas ML**\n"
        "• 🛒 **Recomendación de compra a proveedores**\n"
        "• ⚠️ **Alertas de demanda inusual**\n\n"
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
        "• \"¿Cuánto vamos a vender la próxima semana?\"\n\n"
        "🛒 *Compras:*\n"
        "• \"¿Qué debo pedir al proveedor?\"\n"
        "• \"¿Qué productos reabastecer?\"\n\n"
        "⚠️ *Alertas de demanda:*\n"
        "• \"¿Hay alguna anomalía en las ventas?\"\n"
        "• \"¿Las ventas están por debajo de lo esperado?\""
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
            "SELECT vi.description, SUM(vi.quantity) as veces_vendido, "
            "SUM(vi.subtotal) as total_generado "
            "FROM ventas_ventaitem vi "
            "JOIN ventas_venta v ON v.id = vi.venta_id "
            "WHERE DATE(v.fecha_venta) BETWEEN %s AND %s "
            "GROUP BY vi.description "
            "ORDER BY total_generado DESC "
            "LIMIT 5",
            [fecha_inicio, fecha_fin]
        )
        if resultado:
            lineas = [f"🏆 **Top 5 productos más vendidos ({periodo_texto}):**\n"]
            medallas = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣']
            for i, r in enumerate(resultado):
                lineas.append(
                    f"{medallas[i]} {r['description']} — "
                    f"**{formatear_monto(r['total_generado'])}** "
                    f"({r['veces_vendido']} unidades)"
                )
            return '\n'.join(lineas)
        else:
            return f"No se encontraron ítems de venta {periodo_texto}."
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
            "SELECT COUNT(DISTINCT v.id) as transacciones, SUM(vi.subtotal) as total_ventas "
            "FROM ventas_ventaitem vi "
            "JOIN ventas_venta v ON v.id = vi.venta_id "
            "WHERE LOWER(vi.description) LIKE LOWER(%s) "
            "AND DATE(v.fecha_venta) BETWEEN %s AND %s",
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


def handle_prediccion(params: dict = None, **kwargs) -> str:
    """
    Proyecta ventas usando el modelo ML CatBoost v22.
    Extrae el horizonte del mensaje: día, semana (default) o mes.
    """
    import re
    texto = kwargs.get('texto', '')
    from .router import normalizar
    texto_n = normalizar(texto)

    # Extraer número explícito: "próximos 14 días", "7 días", etc.
    m = re.search(r'(\d+)\s*dias?', texto_n)
    if m:
        horizon = min(int(m.group(1)), 30)  # máximo 30 días
        label = f'los próximos {horizon} días'
    elif 'manana' in texto_n or re.search(r'\bdia\b', texto_n):
        horizon = 1
        label = 'mañana'
    elif 'mes' in texto_n or 'mensual' in texto_n:
        horizon = 30
        label = 'el próximo mes'
    else:
        horizon = 7
        label = 'la próxima semana'

    try:
        from django.db import connection as _conn
        tenant_slug = _conn.schema_name
        from apps.prediccion.predictor import get_predictor
        predicciones = get_predictor().forecast(tenant_slug=tenant_slug, horizon=horizon)

        total = sum(p['prediccion'] for p in predicciones)
        lineas = [f"🔮 **Proyección ML para {label}:**\n"]
        for p in predicciones:
            lineas.append(f"• {p['fecha']}: **{formatear_monto(p['prediccion'])}**")
        if horizon > 1:
            lineas.append(f"\n📊 **Total estimado: {formatear_monto(total)}**")
        lineas.append("\n_Modelo CatBoost v22 entrenado con datos históricos de TechHive._")
        return '\n'.join(lineas)

    except ValueError as exc:
        return (
            "🔮 **Proyección de ventas:**\n"
            f"No es posible generar una predicción: {exc}\n"
            "_Se necesitan al menos 28 días de ventas registradas._"
        )
    except Exception as e:
        return _error_bd(str(e))


def handle_caja(params: dict = None, **kwargs) -> str:
    """
    Consulta el balance de caja (ingresos, egresos, neto) para el período indicado.
    Por defecto muestra el balance del día actual.
    """
    params = params or {}
    fecha_inicio = params.get('fecha_inicio')
    fecha_fin = params.get('fecha_fin')

    hoy = date.today().strftime('%Y-%m-%d')
    if not fecha_inicio:
        fecha_inicio = fecha_fin = hoy
        periodo_texto = 'hoy'
    else:
        periodo_texto = formatear_periodo(fecha_inicio, fecha_fin)

    try:
        movimientos = query_tenant(
            "SELECT type, SUM(amount) as total FROM cash_movement "
            "WHERE date BETWEEN %s AND %s GROUP BY type",
            [fecha_inicio, fecha_fin]
        )
        ingresos = 0.0
        egresos = 0.0
        for r in movimientos:
            if r['type'] == 'income':
                ingresos = float(r['total'])
            elif r['type'] == 'expense':
                egresos = float(r['total'])

        # Monto inicial de la sesión si el período es un solo día
        monto_inicial = 0.0
        if fecha_inicio == fecha_fin:
            sesion = query_tenant(
                "SELECT opening_amount FROM cash_session WHERE date = %s",
                [fecha_inicio]
            )
            if sesion:
                monto_inicial = float(sesion[0]['opening_amount'])

        balance = monto_inicial + ingresos - egresos
        emoji = '✅' if balance >= 0 else '⚠️'

        lineas = [f"💰 **Balance de caja ({periodo_texto}):**\n"]
        if monto_inicial:
            lineas.append(f"• Apertura: **{formatear_monto(monto_inicial)}**")
        lineas += [
            f"• Ingresos: **{formatear_monto(ingresos)}**",
            f"• Egresos: **{formatear_monto(egresos)}**",
            f"• {emoji} Caja final: **{formatear_monto(balance)}**",
        ]
        return '\n'.join(lineas)
    except Exception as e:
        return _error_bd(str(e))


def handle_inventario_stock(params: dict = None, **kwargs) -> str:
    """
    Muestra productos con stock bajo (stock <= stock_min) del inventario.
    """
    try:
        resultado = query_tenant(
            "SELECT p.name, p.stock, p.stock_min, "
            "COALESCE(c.name, 'Sin categoría') AS categoria "
            "FROM inventory_product p "
            "LEFT JOIN inventory_category c ON c.id = p.category_id "
            "WHERE p.is_active = TRUE AND p.stock <= p.stock_min "
            "ORDER BY p.stock ASC LIMIT 10",
            []
        )
        total_bajo = query_tenant(
            "SELECT COUNT(*) as total FROM inventory_product "
            "WHERE is_active = TRUE AND stock <= stock_min",
            []
        )
        n_total = total_bajo[0]['total'] if total_bajo else 0

        if not resultado:
            return "✅ **Stock al día:** todos los productos tienen stock suficiente."

        lineas = [f"⚠️ **Productos con stock bajo ({n_total} en total):**\n"]
        for r in resultado:
            lineas.append(
                f"• **{r['name']}** [{r['categoria']}] — "
                f"Stock: {r['stock']} / Mínimo: {r['stock_min']}"
            )
        if n_total > 10:
            lineas.append(f"\n_Mostrando los 10 más críticos de {n_total}._")
        return '\n'.join(lineas)
    except Exception as e:
        return _error_bd(str(e))


def handle_recomendar_compra(params: dict = None, **kwargs) -> str:
    """
    Sugiere qué productos pedir al proveedor basándose en stock bajo
    y proyección de demanda del predictor ML.
    """
    try:
        productos_bajo = query_tenant(
            "SELECT p.name, p.stock, p.stock_min, "
            "GREATEST(p.stock_min * 3 - p.stock, p.stock_min) AS cantidad_sugerida, "
            "COALESCE(c.name, 'Sin categoría') AS categoria "
            "FROM inventory_product p "
            "LEFT JOIN inventory_category c ON c.id = p.category_id "
            "WHERE p.is_active = TRUE AND p.stock <= p.stock_min * 2 "
            "ORDER BY (p.stock_min - p.stock) DESC LIMIT 10",
            []
        )
    except Exception as e:
        return _error_bd(str(e))

    # Intentar obtener proyección ML para enriquecer la respuesta
    proyeccion_texto = ""
    try:
        from django.db import connection as _conn
        from apps.prediccion.predictor import get_predictor
        predicciones = get_predictor().forecast(tenant_slug=_conn.schema_name, horizon=7)
        total_semana = sum(p['prediccion'] for p in predicciones)
        proyeccion_texto = f"\n\n📈 _Proyección ML próxima semana: **{formatear_monto(total_semana)}** — ten stock suficiente._"
    except Exception:
        pass

    if not productos_bajo:
        return (
            "✅ **Stock suficiente:** todos los productos tienen inventario adecuado "
            "para las próximas semanas." + proyeccion_texto
        )

    lineas = [f"🛒 **Recomendación de compra ({len(productos_bajo)} productos):**\n"]
    for r in productos_bajo:
        sugerido = int(r['cantidad_sugerida'])
        lineas.append(
            f"• **{r['name']}** [{r['categoria']}] — "
            f"Stock actual: {r['stock']} / Mínimo: {r['stock_min']} → "
            f"Pedir: **{sugerido} unidades**"
        )
    lineas.append(proyeccion_texto)
    return '\n'.join(lineas)


def handle_alerta_demanda(params: dict = None, **kwargs) -> str:
    """
    Detecta anomalías comparando ventas reales de las últimas 2 semanas
    contra la proyección del modelo ML.
    """
    hoy = date.today()
    hace_7 = (hoy - timedelta(days=6)).strftime('%Y-%m-%d')
    hace_14 = (hoy - timedelta(days=13)).strftime('%Y-%m-%d')
    hace_8 = (hoy - timedelta(days=7)).strftime('%Y-%m-%d')
    hoy_str = hoy.strftime('%Y-%m-%d')

    try:
        sem_actual = query_tenant(
            "SELECT SUM(total) as total FROM ventas_venta "
            "WHERE DATE(fecha_venta) BETWEEN %s AND %s",
            [hace_7, hoy_str]
        )
        sem_anterior = query_tenant(
            "SELECT SUM(total) as total FROM ventas_venta "
            "WHERE DATE(fecha_venta) BETWEEN %s AND %s",
            [hace_14, hace_8]
        )
    except Exception as e:
        return _error_bd(str(e))

    real_actual = float(sem_actual[0]['total'] or 0) if sem_actual else 0.0
    real_anterior = float(sem_anterior[0]['total'] or 0) if sem_anterior else 0.0

    # Proyección ML de la semana actual
    proyectado = None
    try:
        from django.db import connection as _conn
        from apps.prediccion.predictor import get_predictor
        predicciones = get_predictor().forecast(tenant_slug=_conn.schema_name, horizon=7)
        proyectado = sum(p['prediccion'] for p in predicciones)
    except Exception:
        pass

    lineas = ["🔍 **Análisis de demanda — últimas 2 semanas:**\n"]
    lineas.append(f"• Semana anterior (hace 14→8 días): **{formatear_monto(real_anterior)}**")
    lineas.append(f"• Semana actual (últimos 7 días):   **{formatear_monto(real_actual)}**")

    # Variación semana a semana
    if real_anterior > 0:
        variacion = ((real_actual - real_anterior) / real_anterior) * 100
        emoji = "📈" if variacion >= 0 else "📉"
        lineas.append(f"\n{emoji} Variación semanal: **{variacion:+.1f}%**")
        if abs(variacion) >= 20:
            direction = "caída" if variacion < 0 else "pico"
            lineas.append(f"⚠️ **Alerta: {direction} inusual de {abs(variacion):.0f}% respecto a la semana anterior.**")

    # Mostrar proyección ML como referencia (no comparar con histórico: son períodos distintos)
    if proyectado:
        lineas.append(f"\n🔮 **Proyección ML próxima semana: {formatear_monto(proyectado)}**")

    return '\n'.join(lineas)


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
    'caja_balance': handle_caja,
    'inventario_stock': handle_inventario_stock,
    'recomendar_compra': handle_recomendar_compra,
    'alerta_demanda': handle_alerta_demanda,
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
