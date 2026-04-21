# 00 — Resumen del Sistema

## ¿Qué es TechHive 3.0?

TechHive 3.0 es un sistema ERP (*Enterprise Resource Planning*) SaaS multi-tenant orientado a pequeñas y medianas empresas (PyMES). Permite que múltiples empresas compartan la misma instalación de software mientras mantienen sus datos completamente aislados entre sí mediante esquemas de PostgreSQL separados.

El sistema combina tres capacidades diferenciadas:

1. **ERP modular**: gestión de ventas, inventario, compras, caja, servicio técnico y reportes.
2. **Chatbot inteligente**: asistente conversacional que adapta su comportamiento al rol del usuario (staff interno / cliente externo), con fallback a un modelo de lenguaje (GPT-4o mini via OpenAI).
3. **Predicción de ventas ML**: ensemble de modelos CatBoost (v22) que genera pronósticos diarios de ventas para cada tenant, integrando datos climáticos, calendarios de feriados y patrones históricos.

## Tenants en producción (datos académicos)

| Tenant | Schema PostgreSQL | Descripción |
|--------|-------------------|-------------|
| Magic World | `magic_world` | Tienda de artículos de magia |
| Papelería Alfa & Omega | `papeleria` | Papelería y suministros |
| Demo | `demo` | Entorno de prueba (usa modelo de papelería) |

## Métricas del modelo predictivo (v22)

| Tenant | MAPE | Accuracy MAPE | Accuracy ±20 % |
|--------|------|--------------|----------------|
| Magic World | 16.12 % | 83.88 % | 80.0 % |
| Papelería Alfa & Omega | 14.87 % | 85.13 % | 76.47 % |

## Métricas del chatbot

| Canal | Intenciones | Casos de prueba | Precisión | F1 macro |
|-------|-------------|-----------------|-----------|----------|
| Staff | 14 | 67 | 100 % | 100 % |
| Cliente | 7 | 56 | 100 % | 100 % |
| Total | 21 | 123 | 100 % | 100 % |

## Portales de acceso

| Portal | URL | Descripción |
|--------|-----|-------------|
| Admin maestro | `http://localhost:5173` (desde `admin.localhost`) | Gestión global de empresas |
| Tenant ERP | `http://<dominio>.localhost:5173` | ERP completo por empresa |
| Catálogo cliente | `/catalog` (mismo dominio del tenant) | Vista pública de productos |

## Tecnologías clave

- **Backend**: Python 3.11+, Django 6.0.2, DRF 3.16, django-tenants 3.10, PostgreSQL 14+
- **Frontend**: Vue 3.5, Vite 7, TypeScript 5.9, Pinia 3, Axios 1.13
- **ML**: CatBoost ≥ 1.2, Meteostat ≥ 1.6, Pandas ≥ 2.0, NumPy ≥ 1.24
- **Chatbot LLM**: OpenAI GPT-4o mini (`openai >= 1.0`)
- **Auth**: JWT via `djangorestframework-simplejwt 5.5`

---
*Ver [01_arquitectura_general.md](./01_arquitectura_general.md) para el diagrama de capas.*
