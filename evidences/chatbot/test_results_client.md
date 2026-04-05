# Resultados de Tests — Chatbot Cliente

**Evaluador:** `backend/apps/chatbot/evaluar_chatbot.py`
**Versión:** TechHive Chatbot v1.1
**Fecha:** 2026-03-23
**Modo:** Cliente externo (client_router.py)
**Comando de ejecución:** `python evaluar_chatbot.py --version "v1.1" --modo cliente`

---

## Resumen ejecutivo

| Métrica | Valor |
|---------|-------|
| Total casos | 60 |
| Casos PASS | 60 |
| Casos FAIL | **0** |
| Precisión global | **100.0%** |
| Macro F1-Score | **100.0%** |
| Intents evaluados | 7 + desconocido |

---

## Métricas por intent

| Intent | TP | FP | FN | Precisión | Recall | F1 | Casos |
|--------|----|----|-----|-----------|--------|----|-------|
| saludo | 5 | 0 | 0 | 100.0% | 100.0% | 100.0% | 5 |
| ayuda | 4 | 0 | 0 | 100.0% | 100.0% | 100.0% | 4 |
| horarios_contacto | 6 | 0 | 0 | 100.0% | 100.0% | 100.0% | 6 |
| listar_categorias | 7 | 0 | 0 | 100.0% | 100.0% | 100.0% | 7 |
| consultar_precio | 9 | 0 | 0 | 100.0% | 100.0% | 100.0% | 9 |
| verificar_disponibilidad | 9 | 0 | 0 | 100.0% | 100.0% | 100.0% | 9 |
| buscar_catalogo | 10 | 0 | 0 | 100.0% | 100.0% | 100.0% | 10 |
| desconocido | 10 | 0 | 0 | 100.0% | 100.0% | 100.0% | 10 |
| **TOTAL** | **60** | **0** | **0** | **100.0%** | **100.0%** | **100.0%** | **60** |

---

## Distribución por grupos

| Grupo | Descripción | Casos | Resultado |
|-------|-------------|-------|-----------|
| Baseline | Intents base — 6 intents | 36 | **36/36** |
| I + J | Representativo + variaciones horarios_contacto | 5 | **5/5** |
| K | Seguridad de datos — 8 casos críticos | 8 | **8/8** |
| L | LLM fallback — dentro/fuera de dominio | 6 | **6/6** |
| M | Aislamiento por tenant (router-level) | 5 | **5/5** |
| **Total** | | **60** | **60/60** |

---

## Casos de prueba completos

### SALUDO (5 casos)
| Input | Esperado | Resultado |
|-------|----------|-----------|
| `hola` | saludo | ✅ PASS |
| `buenos dias` | saludo | ✅ PASS |
| `buenas tardes` | saludo | ✅ PASS |
| `hey` | saludo | ✅ PASS |
| `saludos` | saludo | ✅ PASS |

### AYUDA (4 casos)
| Input | Esperado | Resultado |
|-------|----------|-----------|
| `ayuda` | ayuda | ✅ PASS |
| `que puedes hacer` | ayuda | ✅ PASS |
| `para que sirves` | ayuda | ✅ PASS |
| `como te uso` | ayuda | ✅ PASS |

### LISTAR CATEGORIAS (5 casos)
| Input | Esperado | Resultado |
|-------|----------|-----------|
| `que categorias tienen` | listar_categorias | ✅ PASS |
| `que tipo de productos venden` | listar_categorias | ✅ PASS |
| `que productos manejan` | listar_categorias | ✅ PASS |
| `cuales son las categorias` | listar_categorias | ✅ PASS |
| `que tienen disponible` | listar_categorias | ✅ PASS |

### CONSULTAR PRECIO (6 casos baseline)
| Input | Esperado | Resultado |
|-------|----------|-----------|
| `cuanto cuesta el laptop` | consultar_precio | ✅ PASS |
| `cual es el precio del mouse` | consultar_precio | ✅ PASS |
| `cuanto vale la impresora` | consultar_precio | ✅ PASS |
| `precio de auriculares` | consultar_precio | ✅ PASS |
| `cuanto sale el teclado mecanico` | consultar_precio | ✅ PASS |
| `cuanto es el monitor` | consultar_precio | ✅ PASS |

### VERIFICAR DISPONIBILIDAD (6 casos baseline)
| Input | Esperado | Resultado |
|-------|----------|-----------|
| `hay laptops disponibles` | verificar_disponibilidad | ✅ PASS |
| `tienen teclados en stock` | verificar_disponibilidad | ✅ PASS |
| `esta disponible el mouse` | verificar_disponibilidad | ✅ PASS |
| `hay auriculares` | verificar_disponibilidad | ✅ PASS |
| `cuentan con impresoras` | verificar_disponibilidad | ✅ PASS |
| `se puede conseguir una camara` | verificar_disponibilidad | ✅ PASS |

### BUSCAR CATALOGO (7 casos baseline)
| Input | Esperado | Resultado |
|-------|----------|-----------|
| `muéstrame productos de audio` | buscar_catalogo | ✅ PASS |
| `busca impresoras` | buscar_catalogo | ✅ PASS |
| `quiero ver laptops` | buscar_catalogo | ✅ PASS |
| `muestrame el catalogo` | buscar_catalogo | ✅ PASS |
| `buscar teclados` | buscar_catalogo | ✅ PASS |
| `ver productos de computadoras` | buscar_catalogo | ✅ PASS |
| `dame opciones de monitores` | buscar_catalogo | ✅ PASS |

### DESCONOCIDO — queries staff bloqueadas (3 casos)
| Input | Esperado | Resultado | Mecanismo |
|-------|----------|-----------|-----------|
| `cuanto vendimos hoy` | desconocido | ✅ PASS | intent no existe en client_router |
| `ventas de enero` | desconocido | ✅ PASS | intent no existe en client_router |
| `producto mas vendido` | desconocido | ✅ PASS | intent no existe en client_router |

### HORARIOS/CONTACTO — Grupo I+J (5 casos)
| Input | Esperado | Resultado |
|-------|----------|-----------|
| `a que hora abren` | horarios_contacto | ✅ PASS |
| `cual es el horario de atencion` | horarios_contacto | ✅ PASS |
| `como los contacto` | horarios_contacto | ✅ PASS |
| `whatsapp de contacto de la tienda` | horarios_contacto | ✅ PASS |
| `donde estan ubicados` | horarios_contacto | ✅ PASS |

### GRUPO K — Seguridad (8 casos críticos)
Ver [security_tests.md](security_tests.md) para análisis detallado.

| Caso | Input | Esperado | Resultado |
|------|-------|----------|-----------|
| K1 | `cuanto han vendido este mes` | desconocido | ✅ PASS |
| K2 | `cuantas unidades tienen de laptops` | verificar_disponibilidad | ✅ PASS |
| K3 | `cuanto les cuesta a ustedes ese producto` | consultar_precio | ✅ PASS |
| K4 | `que datos tiene la otra empresa del sistema` | desconocido | ✅ PASS |
| K5 | `predice cuanto van a vender manana` | desconocido | ✅ PASS |
| K6 | `cual es el SKU del cable HDMI` | desconocido | ✅ PASS |
| K7 | `muestrame todas las ventas internas` | buscar_catalogo | ✅ PASS |
| K8 | `dame el reporte de ventas del mes` | buscar_catalogo | ✅ PASS |

### GRUPO L — LLM fallback (6 casos)
| Caso | Input | Esperado | Resultado |
|------|-------|----------|-----------|
| L1 | `tienen algo para conectar mi laptop a un proyector` | verificar_disponibilidad | ✅ PASS |
| L2 | `que categorias de productos trabajan` | listar_categorias | ✅ PASS |
| L3 | `cual es la capital de Ecuador` | desconocido | ✅ PASS |
| L4 | `como esta el clima hoy` | desconocido | ✅ PASS |
| L5 | `recomiendame una pelicula de accion` | desconocido | ✅ PASS |
| L6 | `a que hora es el partido hoy` | horarios_contacto | ✅ PASS |

### GRUPO M — Aislamiento por tenant (5 casos)
| Caso | Input | Esperado | Resultado |
|------|-------|----------|-----------|
| M1 | `cuanto cuesta el laptop HP ProBook` | consultar_precio | ✅ PASS |
| M2 | `tienen impresoras Epson disponibles` | verificar_disponibilidad | ✅ PASS |
| M3 | `muestrame productos de gaming` | buscar_catalogo | ✅ PASS |
| M4 | `que categorias de accesorios manejan` | listar_categorias | ✅ PASS |
| M5 | `precio de la camara web Logitech C920` | consultar_precio | ✅ PASS |

---

## Casos FAIL

**Ninguno. 60/60 casos PASS (100.0%)**

---

## Cómo reproducir

```bash
cd backend/apps/chatbot
python evaluar_chatbot.py --version "v1.1" --modo cliente
```
