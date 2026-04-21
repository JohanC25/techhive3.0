# 10 — Dependencias

## Backend Python (`backend/requirements.txt`)

### Framework y servidor

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| `Django` | 6.0.2 | Framework web principal |
| `djangorestframework` | 3.16.1 | API REST (serializers, viewsets, permissions) |
| `django-tenants` | 3.10.0 | Arquitectura multi-tenant con schemas PostgreSQL |
| `djangorestframework_simplejwt` | 5.5.1 | Autenticación JWT (access + refresh tokens) |
| `asgiref` | 3.11.1 | Soporte ASGI (requerido por Django 6) |

### Base de datos

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| `psycopg2-binary` | 2.9.11 | Driver PostgreSQL para Python |
| `sqlparse` | 0.5.5 | Parser SQL (requerido por Django ORM) |

### Autenticación y utilidades

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| `PyJWT` | 2.11.0 | JWT para el token del portal admin (master key) |
| `python-dotenv` | 1.2.1 | Carga variables de `.env` |
| `python-dateutil` | 2.9.0 | Parseo flexible de fechas en handlers del chatbot |
| `six` | 1.17.0 | Utilidades Python 2/3 (dep transitiva) |
| `tzdata` | 2025.3 | Base de datos de zonas horarias (America/Guayaquil) |

### Machine Learning

| Paquete | Versión mín. | Propósito |
|---------|-------------|-----------|
| `catboost` | ≥ 1.2 | 5 modelos CatBoostRegressor del ensemble v22 |
| `joblib` | ≥ 1.2 | Serialización/deserialización de modelos (`.pkl`) |
| `numpy` | ≥ 1.24 | Cálculos numéricos (feature engineering) |
| `pandas` | ≥ 2.0 | Manipulación de DataFrames para forecast |
| `scipy` | ≥ 1.10 | Funciones matemáticas (sin/cos Fourier) |
| `meteostat` | ≥ 1.6 | Datos climáticos históricos de Quito (lat/lon/alt) |
| `holidays` | ≥ 0.46 | Calendario de feriados de Ecuador |

### LLM / Chatbot

| Paquete | Versión mín. | Propósito |
|---------|-------------|-----------|
| `openai` | ≥ 1.0 | Cliente para GPT-4o mini (fallback del chatbot) |
| `anthropic` | ≥ 0.40.0 | Cliente Anthropic (importado pero el fallback usa OpenAI) |

### Visualización (no usada en producción)

| Paquete | Versión mín. | Propósito |
|---------|-------------|-----------|
| `plotly` | ≥ 5.0 | Gráficas (usado en notebook de desarrollo, no en Django) |

---

## Frontend Node.js (`frontend/package.json`)

### Dependencias de runtime

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| `vue` | ^3.5.28 | Framework UI reactivo (Composition API) |
| `vue-router` | ^5.0.3 | Enrutado SPA con guards |
| `pinia` | ^3.0.4 | Estado global reactivo (reemplaza Vuex) |
| `axios` | ^1.13.5 | Cliente HTTP con interceptores JWT |

### DevDependencies

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| `vite` | ^7.3.1 | Bundler y servidor de desarrollo con HMR |
| `@vitejs/plugin-vue` | ^6.0.4 | Plugin Vue para Vite |
| `@vitejs/plugin-vue-jsx` | ^5.1.4 | Soporte JSX en Vue (devDep) |
| `typescript` | ~5.9.3 | Tipado estático |
| `vue-tsc` | ^3.2.4 | Type-check de archivos `.vue` |
| `vitest` | ^4.0.18 | Testing unitario (compatible con Vite) |
| `@vue/test-utils` | ^2.4.6 | Utilidades de testing para componentes Vue |
| `jsdom` | ^28.1.0 | DOM simulado para tests |
| `eslint` | ^9.39.2 | Linter JavaScript/TypeScript |
| `eslint-plugin-vue` | ~10.8.0 | Reglas ESLint específicas para Vue |
| `oxlint` | ~1.47.0 | Linter Rust ultrarrápido (complementa ESLint) |
| `prettier` | 3.8.1 | Formateador de código |
| `npm-run-all2` | ^8.0.4 | Ejecutar scripts npm en paralelo/serie |

### Versión de Node requerida

```json
"engines": { "node": "^20.19.0 || >=22.12.0" }
```

---

## Servicios externos

| Servicio | API Key necesaria | Variable en .env | Uso |
|---------|------------------|-------------------|-----|
| OpenAI | Sí | `OPENAI_API_KEY` | GPT-4o mini — fallback del chatbot |
| Meteostat | No (libre) | — | Datos climáticos Quito para predicción ML |
| Anthropic Claude | Sí (opcional) | `ANTHROPIC_API_KEY` | Alternativa a OpenAI (importado, no activo por defecto) |

---

## Resumen de versiones críticas

```
Python     3.11+
Django     6.0.2
DRF        3.16.1
SimpleJWT  5.5.1
django-tenants  3.10.0
PostgreSQL 14+
CatBoost   1.2+
Node.js    20.19+ / 22.12+
Vue        3.5.28
Pinia      3.0.4
```
