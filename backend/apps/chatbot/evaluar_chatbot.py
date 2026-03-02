"""
Evaluador del router de intenciones - TechHive Chatbot
Uso: python evaluar_chatbot.py --version "v1-baseline"
"""

import sys
import os
import argparse
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from router import detectar_intencion

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

def evaluar(version="baseline"):
    print(f"\n{'='*60}")
    print(f"  EVALUACION DEL ROUTER - TechHive Chatbot")
    print(f"  Version: {version}")
    print(f"  Fecha:   {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")

    correctos = 0
    total = len(CASOS_DE_PRUEBA)
    errores = []
    tp = defaultdict(int)
    fp = defaultdict(int)
    fn = defaultdict(int)

    for pregunta, esperado in CASOS_DE_PRUEBA:
        resultado = detectar_intencion(pregunta)
        obtenido = resultado['intent']
        if obtenido == esperado:
            correctos += 1
            tp[esperado] += 1
        else:
            fn[esperado] += 1
            fp[obtenido] += 1
            errores.append({
                'pregunta': pregunta,
                'esperado': esperado,
                'obtenido': obtenido,
            })

    accuracy = (correctos / total) * 100
    intenciones = sorted(set([e for _, e in CASOS_DE_PRUEBA]))
    f1_scores = []

    print(f"{'INTENCION':<25} {'TP':>4} {'FP':>4} {'FN':>4} {'Precision':>10} {'Recall':>8} {'F1':>8}")
    print(f"{'-'*65}")

    for intent in intenciones:
        t = tp[intent]
        f = fp[intent]
        fn_val = fn[intent]
        precision = t / (t + f) if (t + f) > 0 else 0
        recall = t / (t + fn_val) if (t + fn_val) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        f1_scores.append(f1)
        print(f"{intent:<25} {t:>4} {f:>4} {fn_val:>4} {precision:>9.1%} {recall:>7.1%} {f1:>7.1%}")

    macro_f1 = sum(f1_scores) / len(f1_scores)

    print(f"\n{'='*60}")
    print(f"  Accuracy:   {accuracy:.1f}%")
    print(f"  Macro F1:   {macro_f1:.1%}")
    print(f"  Correctos:  {correctos}/{total}")
    print(f"{'='*60}")

    if errores:
        print(f"\n  ERRORES ({len(errores)}):")
        for e in errores:
            print(f"  x '{e['pregunta']}'")
            print(f"    Esperado: {e['esperado']} | Obtenido: {e['obtenido']}")

    print(f"\n  FILA PARA TU TABLA:")
    print(f"  | {version} | <describe el cambio> | {accuracy:.1f}% | {macro_f1:.1%} | {correctos}/{total} | {datetime.now().strftime('%Y-%m-%d')} |")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', default='baseline')
    args = parser.parse_args()
    evaluar(version=args.version)