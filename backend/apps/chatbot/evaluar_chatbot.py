"""
Evaluador del router de intenciones - TechHive Chatbot
Uso:
  python evaluar_chatbot.py --version "v3-fix-meses"           # evalúa router staff
  python evaluar_chatbot.py --version "v1-client" --modo cliente # evalúa router cliente
"""

import sys
import os
import argparse
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from router import detectar_intencion
from client_router import detectar_intencion_cliente

CASOS_DE_PRUEBA = [
    # SALUDO
    ("hola",                                        "saludo"),
    ("buenos dias",                                 "saludo"),
    ("buenas tardes",                               "saludo"),
    ("hey",                                         "saludo"),
    ("hola como estas",                             "saludo"),
    # AYUDA
    ("ayuda",                                       "ayuda"),
    ("que puedes hacer",                            "ayuda"),
    ("para que sirves",                             "ayuda"),
    ("como funciona",                               "ayuda"),
    # VENTAS HOY
    ("cuanto vendimos hoy",                         "ventas_hoy"),
    ("ventas de hoy",                               "ventas_hoy"),
    ("cuanto se vendio hoy",                        "ventas_hoy"),
    ("total de hoy",                                "ventas_hoy"),
    ("hoy cuanto vendimos",                         "ventas_hoy"),
    # VENTAS AYER
    ("ventas de ayer",                              "ventas_ayer"),
    ("cuanto vendimos ayer",                        "ventas_ayer"),
    ("total de ayer",                               "ventas_ayer"),
    # VENTAS POR PERIODO
    ("ventas de enero",                             "ventas_por_periodo"),
    ("ventas de septiembre",                        "ventas_por_periodo"),
    ("cuanto vendimos en octubre",                  "ventas_por_periodo"),
    ("resumen de ventas de noviembre",              "ventas_por_periodo"),
    ("ventas de esta semana",                       "ventas_por_periodo"),
    ("ventas de la semana pasada",                  "ventas_por_periodo"),
    ("ventas del mes pasado",                       "ventas_por_periodo"),
    ("ultimos 30 dias",                             "ventas_por_periodo"),
    ("ventas de octubre 2025",                      "ventas_por_periodo"),
    ("cuanto vendimos este mes",                    "ventas_por_periodo"),
    # PRODUCTO MAS VENDIDO
    ("producto mas vendido",                        "producto_mas_vendido"),
    ("cual es el producto mas vendido",             "producto_mas_vendido"),
    ("que se vende mas",                            "producto_mas_vendido"),
    ("top productos",                               "producto_mas_vendido"),
    ("articulo mas vendido",                        "producto_mas_vendido"),
    ("que vendemos mas",                            "producto_mas_vendido"),
    # BUSCAR PRODUCTO
    ("cuanto vendimos de impresiones",              "buscar_producto"),
    ("ventas de recargas",                          "buscar_producto"),
    ("cuanto de copias",                            "buscar_producto"),
    ("buscame ventas de cables",                    "buscar_producto"),
    # COMPARAR
    ("compara octubre con noviembre",               "comparar_periodos"),
    ("octubre vs noviembre",                        "comparar_periodos"),
    ("diferencia entre enero y febrero",            "comparar_periodos"),
    ("comparacion de meses",                        "comparar_periodos"),
    ("cual fue el mejor mes",                       "comparar_periodos"),
    ("compara septiembre y octubre",                "comparar_periodos"),
    # TENDENCIA
    ("como van las ventas",                         "tendencia"),
    ("tendencia de ventas",                         "tendencia"),
    ("las ventas estan subiendo",                   "tendencia"),
    ("evolucion de ventas",                         "tendencia"),
    # PREDICCION
    ("cuanto vamos a vender la proxima semana",     "prediccion"),
    ("prediccion de ventas",                        "prediccion"),
    ("proyeccion para el proximo mes",              "prediccion"),
    ("cuanto venderemos en febrero",                "prediccion"),
]

# ─────────────────────────────────────────────
# TEST SET — ROUTER CLIENTE (v1-client-baseline)
# ─────────────────────────────────────────────
CASOS_CLIENTE = [
    # SALUDO
    ("hola",                                            "saludo"),
    ("buenos dias",                                     "saludo"),
    ("buenas tardes",                                   "saludo"),
    ("hey",                                             "saludo"),
    ("saludos",                                         "saludo"),
    # AYUDA
    ("ayuda",                                           "ayuda"),
    ("que puedes hacer",                                "ayuda"),
    ("para que sirves",                                 "ayuda"),
    ("como te uso",                                     "ayuda"),
    # LISTAR CATEGORIAS
    ("que categorias tienen",                           "listar_categorias"),
    ("que tipo de productos venden",                    "listar_categorias"),
    ("que productos manejan",                           "listar_categorias"),
    ("cuales son las categorias",                       "listar_categorias"),
    ("que tienen disponible",                           "listar_categorias"),
    # CONSULTAR PRECIO
    ("cuanto cuesta el laptop",                         "consultar_precio"),
    ("cual es el precio del mouse",                     "consultar_precio"),
    ("cuanto vale la impresora",                        "consultar_precio"),
    ("precio de auriculares",                           "consultar_precio"),
    ("cuanto sale el teclado mecanico",                 "consultar_precio"),
    ("cuanto es el monitor",                            "consultar_precio"),
    # VERIFICAR DISPONIBILIDAD
    ("hay laptops disponibles",                         "verificar_disponibilidad"),
    ("tienen teclados en stock",                        "verificar_disponibilidad"),
    ("esta disponible el mouse",                        "verificar_disponibilidad"),
    ("hay auriculares",                                 "verificar_disponibilidad"),
    ("cuentan con impresoras",                          "verificar_disponibilidad"),
    ("se puede conseguir una camara",                   "verificar_disponibilidad"),
    # BUSCAR CATALOGO
    ("muéstrame productos de audio",                    "buscar_catalogo"),
    ("busca impresoras",                                "buscar_catalogo"),
    ("quiero ver laptops",                              "buscar_catalogo"),
    ("muestrame el catalogo",                           "buscar_catalogo"),
    ("buscar teclados",                                 "buscar_catalogo"),
    ("ver productos de computadoras",                   "buscar_catalogo"),
    ("dame opciones de monitores",                      "buscar_catalogo"),
    # DESCONOCIDO
    ("cuanto vendimos hoy",                             "desconocido"),
    ("ventas de enero",                                 "desconocido"),
    ("producto mas vendido",                            "desconocido"),
]


def _calcular_metricas(casos, fn_detectar):
    correctos = 0
    total = len(casos)
    errores = []
    tp = defaultdict(int)
    fp = defaultdict(int)
    fn = defaultdict(int)

    for pregunta, esperado in casos:
        resultado = fn_detectar(pregunta)
        obtenido = resultado['intent']
        if obtenido == esperado:
            correctos += 1
            tp[esperado] += 1
        else:
            fn[esperado] += 1
            fp[obtenido] += 1
            errores.append({'pregunta': pregunta, 'esperado': esperado, 'obtenido': obtenido})

    accuracy = (correctos / total) * 100
    intenciones = sorted(set(e for _, e in casos))
    f1_scores = []

    print(f"{'INTENCION':<28} {'TP':>4} {'FP':>4} {'FN':>4} {'Precision':>10} {'Recall':>8} {'F1':>8}")
    print(f"{'-'*68}")

    for intent in intenciones:
        t = tp[intent]
        f = fp[intent]
        fn_val = fn[intent]
        precision = t / (t + f) if (t + f) > 0 else 0
        recall = t / (t + fn_val) if (t + fn_val) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        f1_scores.append(f1)
        print(f"{intent:<28} {t:>4} {f:>4} {fn_val:>4} {precision:>9.1%} {recall:>7.1%} {f1:>7.1%}")

    macro_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0
    return correctos, total, accuracy, macro_f1, errores


def evaluar(version="baseline", modo="staff"):
    casos = CASOS_CLIENTE if modo == "cliente" else CASOS_DE_PRUEBA
    fn_detectar = detectar_intencion_cliente if modo == "cliente" else detectar_intencion
    etiqueta = "CLIENTE" if modo == "cliente" else "STAFF"

    print(f"\n{'='*68}")
    print(f"  EVALUACION DEL ROUTER [{etiqueta}] - TechHive Chatbot")
    print(f"  Version: {version}")
    print(f"  Fecha:   {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*68}\n")

    correctos, total, accuracy, macro_f1, errores = _calcular_metricas(casos, fn_detectar)

    print(f"\n{'='*68}")
    print(f"  Accuracy:   {accuracy:.1f}%")
    print(f"  Macro F1:   {macro_f1:.1%}")
    print(f"  Correctos:  {correctos}/{total}")
    print(f"{'='*68}")

    if errores:
        print(f"\n  ERRORES ({len(errores)}):")
        for e in errores:
            print(f"  x '{e['pregunta']}'")
            print(f"    Esperado: {e['esperado']} | Obtenido: {e['obtenido']}")

    print(f"\n  FILA PARA TU TABLA:")
    print(f"  | {version} | [{etiqueta}] <describe el cambio> | {accuracy:.1f}% | {macro_f1:.1%} | {correctos}/{total} |")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', default='baseline')
    parser.add_argument('--modo', choices=['staff', 'cliente'], default='staff',
                        help='staff = router de ventas, cliente = router de catálogo')
    args = parser.parse_args()
    evaluar(version=args.version, modo=args.modo)