# Conversaciones de Ejemplo — Chatbot TechHive 3.0

Demostraciones cualitativas de todos los intents del sistema conversacional.
Muestra el comportamiento real del chatbot para evaluación académica.

**Sistema:** TechHive 3.0 — Chatbot v1.2
**Canales:** Staff interno (14 intents) | Cliente externo (7 intents)
**Endpoint:** `POST /api/chatbot/mensaje/`

---

## Canal Staff Interno

### Intent: `saludo`
> **Usuario:** hola
> **Chatbot:** ¡Hola! Soy el asistente de TechHive. Puedo ayudarte con ventas, inventario, predicciones, caja y más. ¿En qué te ayudo?

---

### Intent: `ayuda`
> **Usuario:** que puedes hacer
> **Chatbot:** Puedo ayudarte con:
> • Ventas: hoy, ayer, por período, comparar períodos, tendencias
> • Productos: más vendidos, buscar ventas por producto
> • Predicciones: proyección de ventas 1, 7 o 30 días (modelo ML V22)
> • Inventario: alertas de stock bajo
> • Caja: balance del día y movimientos
> • Recomendaciones: qué comprar al proveedor, alertas de demanda
>
> ¿Sobre qué quieres información?

---

### Intent: `ventas_hoy`
> **Usuario:** cuanto vendimos hoy
> **Chatbot:** Hoy (viernes 4 de abril) se registraron **8 ventas** por un total de **$1,245.50**.

---

### Intent: `ventas_ayer`
> **Usuario:** cuanto vendimos ayer
> **Chatbot:** Ayer (jueves 3 de abril) se registraron **6 ventas** por un total de **$892.00**.

---

### Intent: `ventas_por_periodo`
> **Usuario:** ventas de enero
> **Chatbot:** En enero 2026 se registraron **187 ventas** por un total de **$28,456.30**.
> Promedio diario: **$917.95**.

> **Usuario:** ventas de esta semana
> **Chatbot:** Esta semana (31 mar – 4 abr) se han registrado **42 ventas** por **$6,120.80**.

> **Usuario:** ultimos 30 dias
> **Chatbot:** En los últimos 30 días: **241 ventas**, total **$36,890.50**.

---

### Intent: `producto_mas_vendido`
> **Usuario:** que se vende mas
> **Chatbot:** El producto más vendido del mes es **"Tóner HP 85A"** con **47 unidades** vendidas.
>
> Top 3 del mes:
> 1. Tóner HP 85A — 47 unidades ($2,115.00)
> 2. Cable HDMI 2m — 38 unidades ($475.00)
> 3. Mouse inalámbrico Logitech — 31 unidades ($1,085.00)

---

### Intent: `buscar_producto`
> **Usuario:** cuanto vendimos de impresiones
> **Chatbot:** Ventas de productos con "impresión" este mes:
> • Servicio de Impresión A4 — 312 unidades ($624.00)
> • Impresión a color — 89 unidades ($445.00)
> Total: $1,069.00

---

### Intent: `comparar_periodos`
> **Usuario:** compara octubre con noviembre
> **Chatbot:** Comparación octubre vs noviembre 2025:
>
> | Mes | Ventas | Total |
> |-----|--------|-------|
> | Octubre | 198 | $29,340.00 |
> | Noviembre | 212 | $31,890.50 |
>
> **Noviembre fue mejor en +8.3%** (+$2,550.50).

---

### Intent: `tendencia`
> **Usuario:** como van las ventas
> **Chatbot:** Tendencia de las últimas 4 semanas:
> • Semana 1 (10–16 mar): $8,240.00
> • Semana 2 (17–23 mar): $7,890.00 (↓ -4.3%)
> • Semana 3 (24–30 mar): $8,560.00 (↑ +8.5%)
> • Semana 4 (31 mar–4 abr): $6,120.80 (parcial)
>
> **Tendencia general: estable con leve alza.**

---

### Intent: `prediccion`
> **Usuario:** prediccion de ventas para la proxima semana
> **Chatbot:** Proyección para los próximos 7 días (modelo V22, MAPE=16.12%):
>
> | Fecha | Día | Predicción |
> |-------|-----|------------|
> | 05-abr | Sáb | $142.50 |
> | 06-abr | Dom | $98.30 |
> | 07-abr | Lun | $187.20 |
> | 08-abr | Mar | $195.80 |
> | 09-abr | Mié | $201.40 |
> | 10-abr | Jue | $178.60 |
> | 11-abr | Vie | $220.10 |
>
> **Total proyectado: $1,223.90**

---

### Intent: `recomendar_compra`
> **Usuario:** que debo pedir al proveedor
> **Chatbot:** Basado en stock actual y proyección de demanda (próximos 7 días):
>
> 🔴 **Reabastecimiento urgente:**
> • Tóner HP 85A — stock: 2 (mín: 5), proyección demanda: 12 unidades
> • Papel A4 resma — stock: 3 (mín: 10), proyección demanda: 18 unidades
>
> 🟡 **Reabastecimiento recomendado:**
> • Cartucho Epson T544 — stock: 4 (mín: 5), proyección demanda: 7 unidades
>
> ¿Quieres que genere la lista de pedido?

---

### Intent: `alerta_demanda`
> **Usuario:** hay alguna anomalia en las ventas
> **Chatbot:** Comparando ventas reales vs predicción del modelo V22 (últimas 2 semanas):
>
> ⚠️ **Anomalía detectada el 28-mar:**
> • Predicción: $187.00 | Real: $89.50 (desviación: -52.1%)
>
> Los demás días se mantienen dentro del rango esperado (±20%).
>
> Posible causa: día festivo no registrado o evento local.

---

### Intent: `caja_balance`
> **Usuario:** como esta la caja hoy
> **Chatbot:** Balance de caja — viernes 4 de abril:
>
> | Concepto | Monto |
> |----------|-------|
> | Monto inicial (apertura) | $200.00 |
> | Ingresos (ventas + otros) | $1,245.50 |
> | Egresos (compras + gastos) | $350.00 |
> | **Caja final** | **$1,095.50** |

---

### Intent: `inventario_stock`
> **Usuario:** que productos tienen stock bajo
> **Chatbot:** Productos con stock por debajo del mínimo:
>
> 🔴 Tóner HP 85A — stock: 2 (mín: 5)
> 🔴 Papel A4 resma — stock: 3 (mín: 10)
> 🟡 Cartucho Epson T544 — stock: 4 (mín: 5)
>
> Total: 3 productos necesitan reabastecimiento.

---

## Canal Cliente Externo

### Intent: `saludo`
> **Cliente:** hola
> **Chatbot:** ¡Hola! Soy el asistente de Magic World. Puedo ayudarte con precios, disponibilidad de productos, catálogo y horarios. ¿En qué te ayudo?

---

### Intent: `ayuda`
> **Cliente:** que puedes hacer
> **Chatbot:** Puedo ayudarte con:
> • Consultar precios de productos
> • Verificar disponibilidad
> • Buscar en nuestro catálogo
> • Ver categorías disponibles
> • Horarios y formas de contacto
>
> ¿Sobre qué quieres información?

---

### Intent: `horarios_contacto`
> **Cliente:** a que hora abren
> **Chatbot:** Nuestro horario de atención es de lunes a viernes de 8:00 a 18:00, y sábados de 9:00 a 14:00.
> Para contactarnos: info@magicworld.techhive.local

---

### Intent: `listar_categorias`
> **Cliente:** que categorias tienen
> **Chatbot:** Nuestras categorías de productos:
> • Computadoras y laptops
> • Accesorios
> • Insumos de impresión
> • Redes y conectividad
> • Audio y video
>
> ¿Te interesa alguna categoría en particular?

---

### Intent: `consultar_precio`
> **Cliente:** cuanto cuesta el laptop
> **Chatbot:** Laptops disponibles:
> • Laptop HP ProBook 450 — **$850.00** (disponible)
> • Laptop Dell Inspiron 15 — **$720.00** (disponible)
> • Laptop Lenovo IdeaPad — **$680.00** (disponible)

---

### Intent: `verificar_disponibilidad`
> **Cliente:** hay laptops disponibles
> **Chatbot:** Sí, tenemos laptops disponibles. ¿Te puedo dar más detalles sobre algún modelo?

> **Cliente:** cuantas unidades tienen de laptops
> **Chatbot:** Sí, tenemos laptops disponibles en este momento. Para más información sobre stock o reservas, contáctanos directamente.
>
> *(Nota: el handler retorna disponibilidad booleana — nunca el stock exacto)*

---

### Intent: `buscar_catalogo`
> **Cliente:** quiero ver laptops
> **Chatbot:** Encontré 3 laptops disponibles:
> • Laptop HP ProBook 450 — $850.00 (disponible)
> • Laptop Dell Inspiron 15 — $720.00 (disponible)
> • Laptop Lenovo IdeaPad — $680.00 (disponible)

---

### Intent: `desconocido` — bloqueo de datos internos

> **Cliente:** cuanto han vendido este mes
> **Chatbot:** No entendí tu consulta. Puedo ayudarte con: precios, disponibilidad, catálogo de productos, categorías y horarios de atención. ¿En qué te puedo ayudar?

> **Cliente:** predice cuanto van a vender manana
> **Chatbot:** No entendí tu consulta. Puedo ayudarte con: precios, disponibilidad, catálogo de productos, categorías y horarios de atención.

> **Cliente:** cual es la capital de Ecuador
> **Chatbot:** Solo puedo ayudarte con consultas sobre nuestros productos y servicios. ¿Hay algo de nuestro catálogo en lo que pueda ayudarte?

---

## Notas de implementación

- El chatbot **no** almacena contexto entre mensajes (cada mensaje es independiente).
  El `session_id` agrupa mensajes en el historial pero no afecta el routing.
- Los handlers de ventas/predicción requieren datos en la BD del tenant activo.
  En tenants nuevos sin historial, retornan mensaje de "sin datos".
- El LLM fallback (GPT-4o mini) solo se invoca cuando el router retorna `desconocido`
  **y** el scope guard determina que la consulta está en dominio.
