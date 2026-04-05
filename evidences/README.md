# Evidencias — TechHive 3.0

Carpeta centralizada de evidencias técnicas para evaluación académica.
Cada subcarpeta contiene archivos reproducibles, métricas reales y ejemplos ejecutables.

**Sistema evaluado:** TechHive 3.0 — ERP SaaS multi-tenant con ML y chatbot inteligente
**Fecha de corte:** 2026-04-04
**Versión del modelo:** v22 (CatBoost ensemble)
**Versión del chatbot:** v1.2

---

## Estructura

```
evidences/
├── README.md                          ← este archivo (índice)
│
├── model/                             ← Evidencias del modelo de predicción ML
│   ├── metrics_summary.csv            ← Métricas finales por tenant (valores reales)
│   ├── hyperparameters.json           ← Hiperparámetros del modelo V22
│   ├── features_list.csv              ← 78 variables de entrada con grupo y descripción
│   ├── validation_results.md          ← Walk-forward 5 folds + análisis de métricas
│   └── export_metrics.py              ← Script: regenera metrics_summary.csv desde metadata
│
├── api/                               ← Evidencias de los endpoints REST
│   ├── endpoints_summary.md           ← Tabla completa de endpoints con métodos y permisos
│   ├── request_response_examples.json ← Ejemplos reales de request/response por endpoint
│   └── test_api.sh                    ← Script curl para probar todos los endpoints
│
├── chatbot/                           ← Evidencias del sistema conversacional
│   ├── conversations.md               ← Conversaciones completas para los 21 intents
│   ├── test_results_staff.md          ← Resultados 63 casos staff (precisión/F1 por intent)
│   ├── test_results_client.md         ← Resultados 60 casos cliente (precisión/F1 por intent)
│   ├── security_tests.md              ← Grupo K (8 casos) + análisis de seguridad de datos
│   └── run_eval.sh                    ← Script: ejecuta evaluar_chatbot.py y captura salida
│
└── integration/                       ← Evidencias de integración del sistema
    ├── system_flow.md                 ← Flujos completos multi-tenant con diagramas
    ├── tenant_isolation.md            ← Prueba técnica del aislamiento por tenant
    └── erp_workflow.md                ← Flujos ERP: venta→caja, compra→caja, inventario
```

---

## Clasificación por prioridad

### Obligatorias (para aprobar)

| # | Archivo | Propósito |
|---|---------|-----------|
| 1 | `model/metrics_summary.csv` | Métricas ML reales (RMSE, MAPE, Acc±20%) |
| 2 | `model/validation_results.md` | Validación walk-forward 5 folds del modelo |
| 3 | `chatbot/test_results_staff.md` | Precisión 100% en 67 casos staff |
| 4 | `chatbot/test_results_client.md` | Precisión 100% en 60 casos cliente |
| 5 | `chatbot/security_tests.md` | 8/8 casos de seguridad PASS |
| 6 | `api/request_response_examples.json` | Funcionamiento real de los endpoints |

### Recomendadas (para destacar)

| # | Archivo | Propósito |
|---|---------|-----------|
| 7 | `model/features_list.csv` | Transparencia del modelo: 78 variables explicadas |
| 8 | `model/hyperparameters.json` | Reproducibilidad: configuración exacta del entrenamiento |
| 9 | `chatbot/conversations.md` | Demostración cualitativa del chatbot |
| 10 | `integration/tenant_isolation.md` | Prueba técnica del aislamiento de datos |
| 11 | `integration/erp_workflow.md` | Integración entre módulos ERP |
| 12 | `api/test_api.sh` | Prueba activa de todos los endpoints |

---

## Resumen de métricas clave

### Modelo de predicción V22

| Tenant | RMSE | MAE | MAPE | Acc@MAPE | Acc@±20% |
|--------|------|-----|------|----------|---------|
| Magic World | 55.47 | 13.86 | 16.12% | 83.88% | **80.00%** |
| Papelería Alfa | 10.25 | 7.87 | 14.87% | 85.13% | **76.47%** |

> Fuente: `backend/apps/prediccion/ml_models/metadata_v22.json`

### Chatbot v1.2

| Canal | Intents | Casos | Precisión | Macro F1 |
|-------|---------|-------|-----------|----------|
| Staff interno | 14 | **67** | **100.0%** | **100.0%** |
| Cliente externo | 7 | 60 | **100.0%** | **100.0%** |
| Seguridad (Grupo K) | — | 8 | **100.0%** | — |
| Aislamiento (Grupo M) | — | 5 | **100.0%** | — |

> Fuente: `evaluar_chatbot.py` ejecutado 2026-04-04 — salida real: **67/67** staff, **60/60** cliente

---

## Cómo reproducir las evidencias

```bash
# 1. Métricas del modelo (regenerar CSV desde metadata_v22.json)
cd backend
python evidences/model/export_metrics.py

# 2. Tests del chatbot (requiere solo Python, sin BD ni servidor)
cd backend/apps/chatbot
python evaluar_chatbot.py --version "v1.2" --modo staff
python evaluar_chatbot.py --version "v1.2" --modo cliente

# 3. Tests de API (requiere servidor corriendo en localhost:8000)
bash evidences/api/test_api.sh
```
