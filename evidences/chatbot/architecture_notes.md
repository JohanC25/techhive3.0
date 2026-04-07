# Arquitectura del Chatbot — TechHive 3.0

**Versión:** v1.2
**Fecha:** 2026-04-06

---

## Pregunta frecuente: ¿El chatbot fue entrenado con ML?

**No.** El router de intenciones es **basado en reglas (regex)**, no en machine learning.
El modelo ML (CatBoost V22) es un componente separado que el chatbot *invoca* para ciertos intents, pero no define la clasificación de intenciones.

---

## Arquitectura en 3 capas

```
Usuario
  │
  ▼
┌──────────────────────────────────────────────┐
│  Capa 1: Router regex                        │
│  backend/apps/chatbot/router.py              │
│  backend/apps/chatbot/client_router.py       │
│                                              │
│  Entrada → normalizar() → match regex        │
│  Salida → {intent, params, confianza}        │
└──────────────────────────┬───────────────────┘
                           │ intent detectado
                           ▼
┌──────────────────────────────────────────────┐
│  Capa 2: Handlers SQL (Django ORM)           │
│  backend/apps/chatbot/handlers.py            │
│  backend/apps/chatbot/client_handlers.py     │
│                                              │
│  Consultan BD con queries parametrizadas     │
│  Formatean respuesta estructurada            │
│  ↳ 3 intents llaman al predictor ML:         │
│     prediccion, recomendar_compra,           │
│     alerta_demanda                           │
└──────────────────────────┬───────────────────┘
                           │ si intent='desconocido'
                           ▼
┌──────────────────────────────────────────────┐
│  Capa 3: Fallback LLM (GPT-4o mini)          │
│  backend/apps/chatbot/llm_handler.py         │
│                                              │
│  Solo se activa si router retorna            │
│  'desconocido' Y is_in_domain() = True       │
│  (guarda de dominio para evitar respuestas   │
│  fuera de tema)                              │
└──────────────────────────────────────────────┘
```

---

## Capa 1 — Router regex

### Mecanismo de normalización

Ambos routers aplican `normalizar()` **antes** de evaluar cualquier regex:

```python
# router.py:15-21
def normalizar(texto: str) -> str:
    """Elimina tildes y convierte a minúsculas."""
    texto = texto.lower()
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
```

Esto garantiza robustez automática a mayúsculas, tildes y puntuación **sin fuzzy matching**.

### Intents disponibles

| Canal | Intents | Router |
|-------|---------|--------|
| Staff | 15 intents (ventas, predicción, inventario, caja, etc.) | `router.py` |
| Cliente | 7 intents (catálogo, precios, disponibilidad, etc.) | `client_router.py` |

### Orden de evaluación

El orden importa: los patrones más específicos se evalúan primero para evitar capturas erróneas.
Ejemplo: `prediccion_vs_real` (alerta_demanda) se evalúa antes que `prediccion` para que `"prediccion vs reales"` no sea clasificado como intent de predicción pura.

---

## Capa 2 — Handlers SQL

Los handlers reciben el dict `{intent, params, confianza}` del router y ejecutan la lógica de negocio:

```python
# views.py — dispatch de intents
HANDLER_MAP = {
    'ventas_hoy':          handle_ventas_hoy,
    'ventas_ayer':         handle_ventas_ayer,
    'ventas_por_periodo':  handle_ventas_por_periodo,
    'prediccion':          handle_prediccion,        # ← llama ML
    'recomendar_compra':   handle_recomendar_compra, # ← llama ML
    'alerta_demanda':      handle_alerta_demanda,    # ← llama ML
    'inventario_stock':    handle_inventario_stock,
    'comparar_periodos':   handle_comparar_periodos,
    'producto_mas_vendido':handle_producto_mas_vendido,
    'tendencia':           handle_tendencia,
    'caja_balance':        handle_caja_balance,
    'buscar_producto':     handle_buscar_producto,
    # ... (staff y cliente)
}
```

Todos los handlers usan **Django ORM con queries parametrizadas** — el texto del usuario nunca llega como SQL crudo.

---

## Integración con el modelo ML (CatBoost V22)

Tres intents del chatbot requieren predicciones ML:

### `handle_prediccion()`
```python
predictor = get_predictor(tenant_schema)
forecast = predictor.forecast(horizon=dias)
# Retorna lista [{fecha, prediccion}, ...]
```

### `handle_recomendar_compra()`
```python
productos_bajo_stock = Product.objects.filter(low_stock=True)
for producto in productos_bajo_stock:
    demanda_proyectada = predictor.forecast_producto(producto, horizon=30)
    cantidad_sugerida = max(0, demanda_proyectada - producto.stock)
```

### `handle_alerta_demanda()`
```python
real_hoy = ventas_reales_hoy()
predicho_hoy = predictor.forecast(horizon=1)[0]['prediccion']
desviacion = abs(real_hoy - predicho_hoy) / predicho_hoy
if desviacion > UMBRAL_ALERTA:
    return "⚠️ Alerta: las ventas están X% por debajo de lo esperado"
```

---

## El modelo ML — ¿dónde está documentado?

El entrenamiento del modelo CatBoost V22 es independiente del chatbot y está documentado en:

| Recurso | Contenido |
|---------|-----------|
| [`evidences/model/hyperparameters.json`](../model/hyperparameters.json) | Hiperparámetros exactos del entrenamiento |
| [`evidences/model/metrics_summary.csv`](../model/metrics_summary.csv) | RMSE, MAE, MAPE, Acc±20% por tenant |
| [`evidences/model/validation_results.md`](../model/validation_results.md) | Walk-forward 5 folds, ensemble, calibración |
| [`evidences/model/features_list.csv`](../model/features_list.csv) | 78 variables de entrada con grupo y descripción |
| `notebooks/ModeloPrediccionVentasFinalDjango.ipynb` | Notebook completo de entrenamiento |
| `backend/apps/prediccion/ml_models/metadata_v22.json` | Métricas reales y pesos del ensemble |

### Resumen del modelo ML

- **Algoritmo:** CatBoost (gradient boosting)
- **Versión:** V22 (ensemble de 5 modelos por tenant)
- **Features:** 78 variables (temporales, lag, rolling, stock, categoría)
- **Training:** log-space (log1p/expm1), luego calibración por segmento de demanda
- **Validación:** TimeSeriesSplit(n_splits=5) walk-forward
- **Métricas finales:**
  - Magic World: RMSE=55.47, MAPE=16.12%, Acc±20%=80.0%
  - Papelería Alfa: RMSE=10.25, MAPE=14.87%, Acc±20%=76.47%

---

## Resumen: chatbot vs modelo ML

| Aspecto | Chatbot Router | Modelo ML (CatBoost) |
|---------|---------------|----------------------|
| Tecnología | Regex + Python | CatBoost ensemble |
| ¿Fue "entrenado"? | No — reglas escritas a mano | Sí — fit() sobre datos históricos |
| Entrada | Texto del usuario | 78 features numéricas |
| Salida | Intent + params | Predicción de ventas (float) |
| Robustez | `normalizar()` | Calibración por segmento |
| Documentación | Este archivo | `evidences/model/` + notebooks |
| Relación | Orquestador | Servicio interno llamado por 3 handlers |

El chatbot actúa como **orquestador inteligente**: clasifica la intención del usuario con reglas, ejecuta la lógica de negocio con ORM, y cuando la consulta requiere predicción llama al modelo ML como servicio interno.

---

## Archivos fuente del chatbot

```
backend/apps/chatbot/
├── router.py              ← Router staff: 15 intents, normalizar(), extraer_fechas()
├── client_router.py       ← Router cliente: 7 intents, extracción de producto
├── handlers.py            ← Handlers staff (SQL + llamadas al predictor)
├── client_handlers.py     ← Handlers cliente (catálogo, precios, disponibilidad)
├── views.py               ← Endpoint POST /api/chatbot/chat/ (staff + cliente)
├── llm_handler.py         ← Fallback GPT-4o mini con is_in_domain()
└── evaluar_chatbot.py     ← Evaluador: 127 casos (67 staff + 60 cliente + 28 robustez)
```
