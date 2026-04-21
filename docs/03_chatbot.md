# 03 — Arquitectura del Chatbot

## Visión general

El chatbot de TechHive 3.0 es un sistema conversacional de **3 capas** que funciona dentro del contexto del tenant activo. Adapta su comportamiento según el rol del usuario autenticado:

- **Canal staff** (roles: `admin`, `manager`, `employee`): acceso a datos operativos y analíticos del ERP.
- **Canal cliente** (rol: `client`): acceso limitado al catálogo público (precios, disponibilidad, búsqueda).

## Diagrama de arquitectura

```
Usuario (JWT authenticated)
         │
         ▼
POST /api/chatbot/mensaje/
         │
         ▼
  ┌──────────────────────────────┐
  │     chatbot/views.py         │
  │  enviar_mensaje()            │
  │  1. Valida mensaje (≤500 ch) │
  │  2. Obtener/crear ChatSession│
  │  3. Guarda msg usuario en DB │
  │  4. Detecta rol              │
  └──────────┬───────────────────┘
             │
     ┌───────┴────────┐
     │                │
  role=client      role=staff/admin/manager
     │                │
     ▼                ▼
client_router.py   router.py
detectar_intencion_cliente()  detectar_intencion()
  7 intenciones       14 intenciones
  regex + priority    regex + priority
     │                │
     ▼                ▼
client_handlers.py  handlers.py
ejecutar_intencion_cliente()  ejecutar_intencion()
  SQL seguro (solo catálogo)  SQL completo + llamadas ML
     │                │
     └───────┬────────┘
             │
             ▼
      intent == 'desconocido'?
             │
     NO ─────┴───── SÍ
     │               │
     ▼               ▼
  Respuesta      llm_fallback.py
  directa        is_in_domain()
                 │
         NO ─────┴──── SÍ (en dominio)
         │              │
         ▼         ┌────┴────┐
   out_of_domain  cliente  staff
   response()      │        │
                   ▼        ▼
             fallback_   fallback_
             cliente()   staff()
             GPT-4o mini GPT-4o mini
             (openai)    (openai)
             │
             ▼
    Guarda respuesta en ChatMessage
             │
             ▼
    Response JSON:
    { respuesta, intent, session_id, confianza }
```

## Capa 1 — Router por regex

### Staff router (`apps/chatbot/router.py`)

14 intenciones detectadas por patrones de expresiones regulares en orden de prioridad:

| # | Intención | Ejemplo de mensaje |
|---|-----------|-------------------|
| 1 | `alerta_demanda` | "alerta de demanda", "productos con baja demanda" |
| 2 | `producto_mas_vendido` | "producto más vendido", "qué se vende más" |
| 3 | `ventas_hoy` | "ventas de hoy", "cuánto vendí hoy" |
| 4 | `ventas_semana` | "ventas de esta semana", "resumen semanal" |
| 5 | `ventas_mes` | "ventas del mes", "total mensual" |
| 6 | `comparar_periodos` | "comparar esta semana con la anterior" |
| 7 | `ventas_rango` | "ventas entre el 1 y el 15 de marzo" |
| 8 | `ventas_por_dia` | "ventas por día", "desglose diario" |
| 9 | `inventario_stock` | "stock de inventario", "qué productos hay" |
| 10 | `recomendar_compra` | "qué debo comprar", "recomendación de reposición" |
| 11 | `prediccion` | "predicción para 7 días", "pronostico ventas" |
| 12 | `ticket_servicio` | "tickets pendientes", "órdenes de servicio" |
| 13 | `resumen_caja` | "resumen de caja", "movimientos de caja" |
| 14 | `saludo` | "hola", "buenos días" |

Función clave: `detectar_intencion(mensaje)` → retorna `{'intent': str, 'params': dict, 'confianza': str}`

**Pre-check especial**: `_ALERTA_PRIORITY` evalúa la intención `alerta_demanda` antes del bucle principal para evitar falsos positivos con `ventas_hoy`.

### Client router (`apps/chatbot/client_router.py`)

7 intenciones para clientes:

| Intención | Ejemplo |
|-----------|---------|
| `saludo` | "hola", "buenas" |
| `ayuda` | "qué puedes hacer", "ayuda" |
| `horarios_contacto` | "horario de atención", "teléfono" |
| `listar_categorias` | "qué categorías hay", "secciones" |
| `consultar_precio` | "precio del cuaderno", "cuánto cuesta X" |
| `verificar_disponibilidad` | "hay stock de X", "tienen X disponible" |
| `buscar_catalogo` | "buscar lápices", "quiero ver mochilas" |

## Capa 2 — SQL Handlers

### Staff handlers (`apps/chatbot/handlers.py`)

Cada intención mapea a una función Python que ejecuta SQL raw sobre el schema activo del tenant.

Ejemplos de handlers clave:

- **`handle_ventas_hoy()`**: `SELECT SUM(total), COUNT(*) FROM ventas_venta WHERE fecha_venta = today()`
- **`handle_prediccion()`**: Llama a `TechHivePredictor.forecast(dias=N)` y formatea el resultado
- **`handle_recomendar_compra()`**: Combina inventario bajo stock con predicción ML para recomendar cantidad: `GREATEST(p.stock_min * 3 - p.stock, p.stock_min)`
- **`handle_alerta_demanda()`**: Compara las últimas 2 semanas vs las 2 semanas anteriores para detectar caídas
- **`handle_inventario_stock()`**: Query con `p.name` explícito para evitar columna ambigua en JOINs

### Client handlers (`apps/chatbot/client_handlers.py`)

Los handlers de cliente solo acceden a datos públicos del catálogo:

```sql
SELECT name, description, price,
       (stock > 0) AS available,
       category
FROM inventory_product
WHERE is_active = TRUE
```

**Nunca exponen**: `cost`, `sku` exacto, cantidad exacta de stock, ni datos de ventas.

Búsqueda tolerante a acentos y plurales:
```python
def _normalizar(texto):
    # Elimina acentos, minúsculas
    ...

# Plurales: word.rstrip('s') si len > 3
```

## Capa 3 — LLM Fallback

### Scope guard (`apps/chatbot/llm_fallback.py`)

Antes de llamar al LLM, `is_in_domain(mensaje, canal)` verifica si el mensaje pertenece al dominio del ERP usando conjuntos de palabras clave por canal. Si el mensaje es irrelevante (ej.: "qué es la física cuántica"), se retorna una respuesta estática sin consumir tokens de API.

```python
DOMAIN_KEYWORDS_STAFF = {
    'venta', 'ventas', 'producto', 'inventario', 'stock', 'caja',
    'compra', 'proveedor', 'ticket', 'servicio', 'prediccion',
    'reporte', 'factura', 'pago', 'precio', ...
}
```

### Llamada a GPT-4o mini

```python
# staff channel
client.chat.completions.create(
    model="gpt-4o-mini",
    max_tokens=200,
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT_STAFF},
        {"role": "user",   "content": mensaje}
    ]
)
```

- `SYSTEM_PROMPT_STAFF`: limita al asistente al contexto del ERP, prohíbe inventar datos.
- `SYSTEM_PROMPT_CLIENTE`: prohíbe exponer precios de costo, datos internos, información de otros clientes.

## Modelos de datos del chatbot

### `ChatSession` (`apps/chatbot/models.py`)

```
session_id    (UUID único)
tenant_schema (schema activo cuando se creó la sesión)
created_at / updated_at
```

### `ChatMessage`

```
session      → FK a ChatSession
role         → 'user' | 'bot'
content      → texto del mensaje
intent       → intención detectada (puede ser null)
created_at
```

## Endpoints del chatbot

| Método | URL | Descripción |
|--------|-----|-------------|
| POST | `/api/chatbot/mensaje/` | Enviar mensaje y recibir respuesta |
| GET | `/api/chatbot/historial/<session_id>/` | Ver historial de una sesión |
| DELETE | `/api/chatbot/historial/<session_id>/limpiar/` | Borrar sesión (nuevo chat) |
| GET | `/api/chatbot/health/` | Health check del servicio |

## Evaluación del chatbot

El script `apps/chatbot/evaluar_chatbot.py` ejecuta 123 casos de prueba (67 staff + 56 cliente) y calcula:
- Accuracy, Macro F1, Macro Precision, Macro Recall
- Matriz de confusión por intención
- Grupos especiales: K (seguridad, 8 casos), L (LLM fallback), M (aislamiento de tenants)

Ejecución:
```bash
python evaluar_chatbot.py           # modo staff
python evaluar_chatbot.py --modo cliente
```
