# Resultados de Tests — Chatbot Staff

**Evaluador:** `backend/apps/chatbot/evaluar_chatbot.py`
**Versión:** TechHive Chatbot v1.2
**Fecha:** 2026-03-23
**Modo:** Staff interno (router.py)
**Comando de ejecución:** `python evaluar_chatbot.py --version "v1.2"`

---

## Resumen ejecutivo

| Métrica | Valor |
|---------|-------|
| Total casos | **67** |
| Casos PASS | **67** |
| Casos FAIL | **0** |
| Precisión global | **100.0%** |
| Macro F1-Score | **100.0%** |
| Intents evaluados | 12 de 14* |

> *`caja_balance` e `inventario_stock` están implementados en `handlers.py` pero no incluidos en el test set (sin BD).
> Los 12 intents evaluados obtuvieron 100%. Los 2 intents `recomendar_compra` y `alerta_demanda` fueron añadidos en v1.2.
> **Nota:** El conteo real del archivo `evaluar_chatbot.py` es 67 casos (prediccion: 7, producto_mas_vendido: 7).
> El `CHATBOT_COMPLETE_REPORT.md` indica 63 porque fue redactado antes de que se añadieran 4 casos adicionales.

---

## Métricas por intent

| Intent | TP | FP | FN | Precisión | Recall | F1 | Casos |
|--------|----|----|-----|-----------|--------|----|-------|
| saludo | 5 | 0 | 0 | 100.0% | 100.0% | 100.0% | 5 |
| ayuda | 4 | 0 | 0 | 100.0% | 100.0% | 100.0% | 4 |
| ventas_hoy | 5 | 0 | 0 | 100.0% | 100.0% | 100.0% | 5 |
| ventas_ayer | 3 | 0 | 0 | 100.0% | 100.0% | 100.0% | 3 |
| ventas_por_periodo | 10 | 0 | 0 | 100.0% | 100.0% | 100.0% | 10 |
| producto_mas_vendido | 7 | 0 | 0 | 100.0% | 100.0% | 100.0% | 7 |
| buscar_producto | 4 | 0 | 0 | 100.0% | 100.0% | 100.0% | 4 |
| comparar_periodos | 6 | 0 | 0 | 100.0% | 100.0% | 100.0% | 6 |
| tendencia | 4 | 0 | 0 | 100.0% | 100.0% | 100.0% | 4 |
| prediccion | 7 | 0 | 0 | 100.0% | 100.0% | 100.0% | 7 |
| recomendar_compra | 6 | 0 | 0 | 100.0% | 100.0% | 100.0% | 6 |
| alerta_demanda | 6 | 0 | 0 | 100.0% | 100.0% | 100.0% | 6 |
| **TOTAL** | **67** | **0** | **0** | **100.0%** | **100.0%** | **100.0%** | **67** |

---

## Casos de prueba completos

### SALUDO (5 casos)
| Input | Esperado | Obtenido | Resultado |
|-------|----------|----------|-----------|
| `hola` | saludo | saludo | ✅ PASS |
| `buenos dias` | saludo | saludo | ✅ PASS |
| `buenas tardes` | saludo | saludo | ✅ PASS |
| `hey` | saludo | saludo | ✅ PASS |
| `hola como estas` | saludo | saludo | ✅ PASS |

### AYUDA (4 casos)
| Input | Esperado | Obtenido | Resultado |
|-------|----------|----------|-----------|
| `ayuda` | ayuda | ayuda | ✅ PASS |
| `que puedes hacer` | ayuda | ayuda | ✅ PASS |
| `para que sirves` | ayuda | ayuda | ✅ PASS |
| `como funciona` | ayuda | ayuda | ✅ PASS |

### VENTAS HOY (5 casos)
| Input | Esperado | Obtenido | Resultado |
|-------|----------|----------|-----------|
| `cuanto vendimos hoy` | ventas_hoy | ventas_hoy | ✅ PASS |
| `ventas de hoy` | ventas_hoy | ventas_hoy | ✅ PASS |
| `cuanto se vendio hoy` | ventas_hoy | ventas_hoy | ✅ PASS |
| `total de hoy` | ventas_hoy | ventas_hoy | ✅ PASS |
| `hoy cuanto vendimos` | ventas_hoy | ventas_hoy | ✅ PASS |

### VENTAS AYER (3 casos)
| Input | Esperado | Obtenido | Resultado |
|-------|----------|----------|-----------|
| `ventas de ayer` | ventas_ayer | ventas_ayer | ✅ PASS |
| `cuanto vendimos ayer` | ventas_ayer | ventas_ayer | ✅ PASS |
| `total de ayer` | ventas_ayer | ventas_ayer | ✅ PASS |

### VENTAS POR PERIODO (10 casos)
| Input | Esperado | Obtenido | Resultado |
|-------|----------|----------|-----------|
| `ventas de enero` | ventas_por_periodo | ventas_por_periodo | ✅ PASS |
| `ventas de septiembre` | ventas_por_periodo | ventas_por_periodo | ✅ PASS |
| `cuanto vendimos en octubre` | ventas_por_periodo | ventas_por_periodo | ✅ PASS |
| `resumen de ventas de noviembre` | ventas_por_periodo | ventas_por_periodo | ✅ PASS |
| `ventas de esta semana` | ventas_por_periodo | ventas_por_periodo | ✅ PASS |
| `ventas de la semana pasada` | ventas_por_periodo | ventas_por_periodo | ✅ PASS |
| `ventas del mes pasado` | ventas_por_periodo | ventas_por_periodo | ✅ PASS |
| `ultimos 30 dias` | ventas_por_periodo | ventas_por_periodo | ✅ PASS |
| `ventas de octubre 2025` | ventas_por_periodo | ventas_por_periodo | ✅ PASS |
| `cuanto vendimos este mes` | ventas_por_periodo | ventas_por_periodo | ✅ PASS |

### PRODUCTO MAS VENDIDO (6 casos)
| Input | Esperado | Obtenido | Resultado |
|-------|----------|----------|-----------|
| `producto mas vendido` | producto_mas_vendido | producto_mas_vendido | ✅ PASS |
| `cual es el producto mas vendido` | producto_mas_vendido | producto_mas_vendido | ✅ PASS |
| `que se vende mas` | producto_mas_vendido | producto_mas_vendido | ✅ PASS |
| `top productos` | producto_mas_vendido | producto_mas_vendido | ✅ PASS |
| `articulo mas vendido` | producto_mas_vendido | producto_mas_vendido | ✅ PASS |
| `que vendemos mas` | producto_mas_vendido | producto_mas_vendido | ✅ PASS |

### BUSCAR PRODUCTO (4 casos)
| Input | Esperado | Obtenido | Resultado |
|-------|----------|----------|-----------|
| `cuanto vendimos de impresiones` | buscar_producto | buscar_producto | ✅ PASS |
| `ventas de recargas` | buscar_producto | buscar_producto | ✅ PASS |
| `cuanto de copias` | buscar_producto | buscar_producto | ✅ PASS |
| `buscame ventas de cables` | buscar_producto | buscar_producto | ✅ PASS |

### COMPARAR PERIODOS (6 casos)
| Input | Esperado | Obtenido | Resultado |
|-------|----------|----------|-----------|
| `compara octubre con noviembre` | comparar_periodos | comparar_periodos | ✅ PASS |
| `octubre vs noviembre` | comparar_periodos | comparar_periodos | ✅ PASS |
| `diferencia entre enero y febrero` | comparar_periodos | comparar_periodos | ✅ PASS |
| `comparacion de meses` | comparar_periodos | comparar_periodos | ✅ PASS |
| `cual fue el mejor mes` | comparar_periodos | comparar_periodos | ✅ PASS |
| `compara septiembre y octubre` | comparar_periodos | comparar_periodos | ✅ PASS |

### TENDENCIA (4 casos)
| Input | Esperado | Obtenido | Resultado |
|-------|----------|----------|-----------|
| `como van las ventas` | tendencia | tendencia | ✅ PASS |
| `tendencia de ventas` | tendencia | tendencia | ✅ PASS |
| `las ventas estan subiendo` | tendencia | tendencia | ✅ PASS |
| `evolucion de ventas` | tendencia | tendencia | ✅ PASS |

### PREDICCION (4 casos)
| Input | Esperado | Obtenido | Resultado |
|-------|----------|----------|-----------|
| `cuanto vamos a vender la proxima semana` | prediccion | prediccion | ✅ PASS |
| `prediccion de ventas` | prediccion | prediccion | ✅ PASS |
| `proyeccion para el proximo mes` | prediccion | prediccion | ✅ PASS |
| `cuanto venderemos en febrero` | prediccion | prediccion | ✅ PASS |

### RECOMENDAR COMPRA (6 casos — añadidos v1.2)
| Input | Esperado | Obtenido | Resultado |
|-------|----------|----------|-----------|
| `que debo pedir al proveedor` | recomendar_compra | recomendar_compra | ✅ PASS |
| `que productos debo reponer` | recomendar_compra | recomendar_compra | ✅ PASS |
| `recomiendame que comprar` | recomendar_compra | recomendar_compra | ✅ PASS |
| `que debo ordenar al proveedor` | recomendar_compra | recomendar_compra | ✅ PASS |
| `reabastecer productos` | recomendar_compra | recomendar_compra | ✅ PASS |
| `cuanto pedir de cables` | recomendar_compra | recomendar_compra | ✅ PASS |

### ALERTA DEMANDA (6 casos — añadidos v1.2)
| Input | Esperado | Obtenido | Resultado |
|-------|----------|----------|-----------|
| `hay alguna anomalia en las ventas` | alerta_demanda | alerta_demanda | ✅ PASS |
| `las ventas estan por debajo de lo esperado` | alerta_demanda | alerta_demanda | ✅ PASS |
| `hubo alguna caida de ventas` | alerta_demanda | alerta_demanda | ✅ PASS |
| `algo inusual en las ventas` | alerta_demanda | alerta_demanda | ✅ PASS |
| `ventas inusuales esta semana` | alerta_demanda | alerta_demanda | ✅ PASS |
| `prediccion vs ventas reales` | alerta_demanda | alerta_demanda | ✅ PASS |

---

## Casos FAIL

**Ninguno. 67/67 casos PASS (100.0%)**

---

## Cómo reproducir

```bash
cd backend/apps/chatbot
python evaluar_chatbot.py --version "v1.2"
```

**Output real (verificado 2026-04-04):**
```
====================================================================
  EVALUACION DEL ROUTER [STAFF] - TechHive Chatbot
  Version: v1.2
  Fecha:   2026-04-04 23:40
====================================================================

INTENCION                      TP   FP   FN  Precision   Recall       F1
--------------------------------------------------------------------
alerta_demanda                  6    0    0    100.0%  100.0%  100.0%
ayuda                           4    0    0    100.0%  100.0%  100.0%
buscar_producto                 4    0    0    100.0%  100.0%  100.0%
comparar_periodos               6    0    0    100.0%  100.0%  100.0%
prediccion                      7    0    0    100.0%  100.0%  100.0%
producto_mas_vendido            7    0    0    100.0%  100.0%  100.0%
recomendar_compra               6    0    0    100.0%  100.0%  100.0%
saludo                          5    0    0    100.0%  100.0%  100.0%
tendencia                       4    0    0    100.0%  100.0%  100.0%
ventas_ayer                     3    0    0    100.0%  100.0%  100.0%
ventas_hoy                      5    0    0    100.0%  100.0%  100.0%
ventas_por_periodo             10    0    0    100.0%  100.0%  100.0%

====================================================================
  Accuracy:   100.0%
  Macro F1:   100.0%
  Correctos:  67/67
====================================================================
```
