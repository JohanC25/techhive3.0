"""
Router de intenciones para el chatbot TechHive v3.
Mejoras:
- Comparación entre dos meses detecta correctamente
- Detección de año explícito en consultas
- Orden de prioridad corregido
"""

import re
import unicodedata
from datetime import datetime, timedelta, date
from calendar import monthrange


def normalizar(texto: str) -> str:
    """Elimina tildes y convierte a minúsculas."""
    texto = texto.lower()
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )


MESES = {
    'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
    'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
    'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12,
}

# ─────────────────────────────────────────────
# PATRONES — orden importa, van de más específico a más general
# ─────────────────────────────────────────────

INTENT_PATTERNS = {
    'saludo': [
        r'\b(hola|buenas|buenos dias|buenas tardes|buenas noches|hey|hi|saludos)\b',
    ],
    'ayuda': [
        r'\b(ayuda|ayudame|que puedes hacer|para que sirves|como funciona|que haces)\b',
    ],
    'prediccion': [
        r'\b(predecir|prediccion|proyeccion|forecast|estimado)\b',
        r'proxima semana',
        r'proximo mes',
        r'cuanto vamos a vender',
        r'va a vender',
        r'cuanto venderemos',
        r'cuanto.*vender[aeéiíu]\b',     # cuanto venderé / vendere / venderá
        r'vend\w+\s+(de\s+)?manana',      # venderé mañana / ventas de mañana
        r'ventas?\s+(de\s+)?manana',      # ventas mañana / ventas de mañana
    ],
    # ⚠️ caja_balance ANTES que ventas_por_periodo
    'caja_balance': [
        r'\bcaja\b',
        r'\bbalance\b',
        r'\bingresos?\b',
        r'\begresos?\b',
        r'cuanto.*caja',
        r'total.*caja',
        r'cierre.*caja',
        r'apertura.*caja',
        r'como.*caja',
        r'movimientos? de caja',
        r'flujo de caja',
    ],
    # ⚠️ recomendar_compra ANTES que inventario_stock (evitar captura por r'reponer' / r'stock')
    'recomendar_compra': [
        r'\b(recomendar|recomienda|recomiendame)\b',
        r'que\s+debo\s+(pedir|comprar|reponer|ordenar)',
        r'(pedir|ordenar)\s+al?\s+proveedor',
        r'que\s+productos?.{0,15}(reponer|pedir|comprar|ordenar)',
        r'\breabastecer\b',
        r'cuanto\s+(pedir|comprar)\s+de',
    ],
    'inventario_stock': [
        r'\b(inventario|stock)\b',
        r'bajo stock',
        r'sin stock',
        r'agotado',
        r'productos? (disponibles?|escasos?|faltantes?)',
        r'cuanto.{0,15}(stock|inventario)',
        r'que (productos?|articulos?).{0,20}(poco|bajo|quedan)',
        r'reponer',
        r'stock minimo',
    ],
    # ⚠️ comparar ANTES que ventas_por_periodo
    'comparar_periodos': [
        r'\b(comparar|comparacion|versus|comparame|compara)\b',
        r'\bvs\b',
        r'mejor mes',
        r'peor mes',
        r'diferencia entre',
        r'contra ',
    ],
    # ⚠️ producto_mas_vendido ANTES que ventas_hoy (evita que "hoy" capture "producto más vendido hoy")
    'producto_mas_vendido': [
        r'producto mas vendido',
        r'que se vende mas',
        r'mas popular',
        r'top producto',
        r'mejor vendido',
        r'mas demandado',
        r'cual se vende',
        r'que vendemos mas',
        r'articulo mas vendido',
        r'item mas vendido',
        r'top \d+',
    ],
    'ventas_hoy': [
        r'\bhoy\b',
        r'ventas de hoy',
        r'cuanto.*hoy',
        r'vendimos.*hoy',
    ],
    'ventas_ayer': [
        r'\bayer\b',
        r'ventas de ayer',
    ],
    # ⚠️ alerta_demanda ANTES que tendencia (evita captura por r'como va')
    'alerta_demanda': [
        r'\b(alertas?|anomalias?)\b',
        r'algo\s+(inusual|raro)\b',
        r'(caida|desplome|bajada)\s+de\s+ventas',
        r'prediccion\s+vs\s+(reales?|actual)',
        r'reales?\s+vs\s+prediccion',
        r'por\s+(debajo|encima)\s+de\s+lo\s+(esperado|predicho)',
        r'ventas\s+inusuales?',
    ],
    'tendencia': [
        r'\b(tendencia|crecimiento|evolucion|progreso)\b',
        r'como va',
        r'como han ido',
        r'estan? (subiendo|bajando)',
        r'como van las ventas',
    ],
    'buscar_producto': [
    r'cuanto.*vendimos de ',
    r'buscame',
    r'buscar producto',
    r'cuanto de \w+',          # ← nuevo
    r'ventas de (?!enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre|hoy|ayer|esta|esta|este|la|el)[a-z]+',
    ],
    'ventas_por_periodo': [
        r'\b(semana|mes|ano|enero|febrero|marzo|abril|mayo|junio|julio|agosto|'
        r'septiembre|octubre|noviembre|diciembre)\b',
        r'ultimos \d+ dias',
        r'hace \d+ dias',
        r'cuanto.*vendimos',
        r'total.*ventas',
        r'ventas.*total',
        r'resumen.*ventas',
        r'esta semana',
        r'este mes',
        r'mes pasado',
        r'semana pasada',
    ],
}


# ─────────────────────────────────────────────
# DETECCIÓN DE PARES MES+AÑO (para comparación)
# ─────────────────────────────────────────────

def detectar_pares_mes_año(texto: str) -> list:
    """
    Extrae todos los pares (mes, año_opcional) del texto en orden de aparición.

    Ejemplos:
      "enero 2025 y enero 2026"  → [("enero", 2025), ("enero", 2026)]
      "compara enero con febrero" → [("enero", None), ("febrero", None)]
      "enero 2025 vs febrero"    → [("enero", 2025), ("febrero", None)]
      "ventas de enero"          → [("enero", None)]  ← solo 1, no es comparación
    """
    meses_pattern = '|'.join(MESES.keys())
    # Captura: nombre_mes  opcionalmente seguido de un año de 4 dígitos
    pattern = rf'\b({meses_pattern})\b(?:\s+(20\d{{2}}))?'
    pares = []
    for m in re.finditer(pattern, texto):
        año = int(m.group(2)) if m.group(2) else None
        pares.append((m.group(1), año))
    return pares


# ─────────────────────────────────────────────
# EXTRACCIÓN DE FECHAS
# ─────────────────────────────────────────────

def rango_mes(año: int, mes: int) -> tuple:
    """Retorna (primer_dia, ultimo_dia) de un mes."""
    ultimo_dia = monthrange(año, mes)[1]
    return date(año, mes, 1), date(año, mes, ultimo_dia)


def inferir_año(num_mes: int, año_explicito: int | None = None) -> int:
    """
    Infiere el año correcto para un mes.
    Si hay año explícito lo usa. Si no, usa el más reciente
    que no sea futuro respecto a hoy.
    """
    if año_explicito:
        return año_explicito
    hoy = date.today()
    if num_mes <= hoy.month:
        return hoy.year
    else:
        return hoy.year - 1


def extraer_año_explicito(texto: str) -> int | None:
    """Busca un año de 4 dígitos en el texto (ej: 2024, 2025)."""
    match = re.search(r'\b(20\d{2})\b', texto)
    return int(match.group(1)) if match else None


def extraer_fechas(texto: str) -> dict:
    texto_n = normalizar(texto)
    hoy = date.today()
    fecha_inicio = None
    fecha_fin = None

    año_explicito = extraer_año_explicito(texto_n)

    if re.search(r'\bhoy\b', texto_n):
        fecha_inicio = fecha_fin = hoy

    elif re.search(r'\bayer\b', texto_n):
        fecha_inicio = fecha_fin = hoy - timedelta(days=1)

    elif re.search(r'esta semana', texto_n):
        fecha_inicio = hoy - timedelta(days=hoy.weekday())
        fecha_fin = hoy

    elif re.search(r'semana pasada', texto_n):
        lunes = hoy - timedelta(days=hoy.weekday())
        fecha_inicio = lunes - timedelta(days=7)
        fecha_fin = lunes - timedelta(days=1)

    elif re.search(r'este mes', texto_n):
        fecha_inicio = hoy.replace(day=1)
        fecha_fin = hoy

    elif re.search(r'mes pasado', texto_n):
        primer_dia = hoy.replace(day=1)
        fecha_fin = primer_dia - timedelta(days=1)
        fecha_inicio = fecha_fin.replace(day=1)

    else:
        for nombre_mes, num_mes in MESES.items():
            if re.search(rf'\b{nombre_mes}\b', texto_n):
                año = inferir_año(num_mes, año_explicito)
                fecha_inicio, fecha_fin = rango_mes(año, num_mes)
                break

        match = re.search(r'ultimos (\d+) dias', texto_n)
        if match:
            n = int(match.group(1))
            fecha_inicio = hoy - timedelta(days=n)
            fecha_fin = hoy

    return {
        'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d') if fecha_inicio else None,
        'fecha_fin': fecha_fin.strftime('%Y-%m-%d') if fecha_fin else None,
        'año_explicito': año_explicito,
    }


def extraer_dos_rangos(texto: str) -> dict:
    """
    Para comparaciones, extrae dos rangos de fechas con soporte para:
      - Distintos meses mismo año:     "enero vs febrero"
      - Mismo mes distintos años:      "enero 2025 vs enero 2026"
      - Combinaciones mixtas:          "enero 2025 vs febrero 2026"
    """
    texto_n = normalizar(texto)
    pares = detectar_pares_mes_año(texto_n)

    rangos = []
    # Determinar si los dos meses son iguales (necesitamos mostrar el año en el nombre)
    mismo_mes = len(pares) >= 2 and pares[0][0] == pares[1][0]

    for nombre_mes, año_explicito in pares[:2]:
        num_mes = MESES[nombre_mes]
        año = inferir_año(num_mes, año_explicito)
        inicio, fin = rango_mes(año, num_mes)
        # Incluir año en el nombre si es el mismo mes o si se especificó explícitamente
        nombre = f"{nombre_mes.capitalize()} {año}" if (mismo_mes or año_explicito) else nombre_mes.capitalize()
        rangos.append({
            'nombre': nombre,
            'fecha_inicio': inicio.strftime('%Y-%m-%d'),
            'fecha_fin': fin.strftime('%Y-%m-%d'),
        })

    return {
        'rango1': rangos[0] if len(rangos) > 0 else None,
        'rango2': rangos[1] if len(rangos) > 1 else None,
    }


def extraer_producto(texto: str) -> str | None:
    texto_n = normalizar(texto)
    patrones = [
        r'vendimos de (.+)',
        r'ventas de (.+)',
        r'cuanto.*de (.+)',
        r'buscame (.+)',
        r'buscar (.+)',
    ]
    for patron in patrones:
        match = re.search(patron, texto_n)
        if match:
            producto = match.group(1).strip()
            producto = re.sub(r'\b(en|del|de|la|el|los|las|este|esta)\s*$', '', producto).strip()
            producto = re.sub(r'[?!.,;:"\']+$', '', producto).strip()
            if len(producto) > 2:
                return producto
    return None


# ─────────────────────────────────────────────
# FUNCIÓN PRINCIPAL
# ─────────────────────────────────────────────

def detectar_intencion(texto: str) -> dict:
    texto_normalizado = normalizar(texto)

    intent_detectado = 'desconocido'
    confianza = 'baja'

    # Caso especial: patrones de alerta_demanda que contienen "prediccion"
    # deben evaluarse ANTES del bucle general (prediccion se evalúa primero en el dict)
    _ALERTA_PRIORITY = [
        r'prediccion\s+vs\b',
        r'\bvs\b.{0,20}prediccion',
        r'reales?\s+vs\s+prediccion',
        r'por\s+(debajo|encima)\s+de\s+lo\s+(esperado|predicho)',
    ]
    for _pat in _ALERTA_PRIORITY:
        if re.search(_pat, texto_normalizado):
            intent_detectado = 'alerta_demanda'
            confianza = 'alta'
            break

    if intent_detectado == 'desconocido':
        # Caso especial: si hay dos o más pares mes(+año) → comparación
        pares_mes_año = detectar_pares_mes_año(texto_normalizado)
        if len(pares_mes_año) >= 2:
            intent_detectado = 'comparar_periodos'
            confianza = 'alta'
        else:
            for intent, patrones in INTENT_PATTERNS.items():
                for patron in patrones:
                    if re.search(patron, texto_normalizado):
                        intent_detectado = intent
                        confianza = 'alta'
                        break
                if intent_detectado != 'desconocido':
                    break

    # Extraer parámetros
    fechas = extraer_fechas(texto)
    producto = extraer_producto(texto)

    # Para comparaciones extraer dos rangos
    rangos_comparacion = None
    if intent_detectado == 'comparar_periodos':
        rangos_comparacion = extraer_dos_rangos(texto)

    if intent_detectado == 'desconocido' and fechas['fecha_inicio']:
        intent_detectado = 'ventas_por_periodo'
        confianza = 'media'

    return {
        'intent': intent_detectado,
        'params': {
            'fecha_inicio': fechas['fecha_inicio'],
            'fecha_fin': fechas['fecha_fin'],
            'producto': producto,
            'rangos_comparacion': rangos_comparacion,
            'año_explicito': fechas.get('año_explicito'),
        },
        'confianza': confianza,
        'texto_original': texto,
    }
