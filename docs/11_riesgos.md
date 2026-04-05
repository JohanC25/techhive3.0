# 11 — Riesgos Técnicos

## Clasificación de riesgos

**Impacto**: Alto (A) / Medio (M) / Bajo (B)
**Probabilidad en producción**: Alta (A) / Media (M) / Baja (B)

---

## R1 — Configuración insegura para producción

| Atributo | Valor |
|----------|-------|
| Impacto | Alto |
| Probabilidad | Alta (si no se configura) |
| Archivos | `config/settings.py` |

**Descripción**: Tres valores por defecto son inseguros fuera de desarrollo:
- `ALLOWED_HOSTS = ['*']` → acepta requests de cualquier dominio
- `DEBUG = True` por defecto → expone tracebacks con SQL y stack traces en errores HTTP 500
- `SECRET_KEY` con valor de fallback `'django-insecure-change-me-in-production'`

**Mitigación**: Establecer en `.env`:
```dotenv
DEBUG=False
ALLOWED_HOSTS=mi-dominio.com,www.mi-dominio.com
SECRET_KEY=<clave-aleatoria-de-50-caracteres>
```

---

## R2 — Tokens JWT almacenados en localStorage

| Atributo | Valor |
|----------|-------|
| Impacto | Alto |
| Probabilidad | Media |
| Archivos | `frontend/src/stores/auth.ts`, `services/api.ts` |

**Descripción**: Los tokens `access_token` y `refresh_token` se guardan en `localStorage`, que es accesible desde cualquier JavaScript en el mismo origen. Un ataque XSS exitoso podría robarlos.

**Mitigación alternativa** (no implementada): Usar `httpOnly` cookies para los tokens. Requiere cambios en DRF (cookie authentication) y CORS/CSRF configuration.

**Contexto académico**: Para un prototipo académico con usuarios internos, el riesgo es bajo. El riesgo escala en despliegue público.

---

## R3 — SQL raw en handlers del chatbot

| Atributo | Valor |
|----------|-------|
| Impacto | Alto |
| Probabilidad | Baja |
| Archivos | `apps/chatbot/handlers.py`, `client_handlers.py` |

**Descripción**: Los handlers usan `cursor.execute(query, params)` con SQL escrito manualmente. Si algún parámetro no se pasa correctamente como parámetro parametrizado sino interpolado con format strings, podría ser vulnerable a SQL injection.

**Estado actual**: Los handlers revisados usan `cursor.execute(query, [param])` correctamente (parámetros escapados por psycopg2). Sin embargo, la ausencia de ORM implica que futuras modificaciones podrían introducir vulnerabilidades.

**Mitigación**: Mantener siempre el patrón `cursor.execute(sql, [lista_de_params])`. Nunca usar f-strings o `.format()` con entrada del usuario.

---

## R4 — Cold start del modelo ML

| Atributo | Valor |
|----------|-------|
| Impacto | Medio |
| Probabilidad | Alta (primer request después de restart) |
| Archivos | `apps/prediccion/apps.py`, `predictor.py` |

**Descripción**: Cargar 5 modelos CatBoost (`.pkl`) + metadata toma entre 3-10 segundos. Si el warmup en thread daemon falla silenciosamente, el primer request de predicción experimentará alta latencia.

**Mitigación actual**: `AppConfig.ready()` lanza un thread daemon que pre-carga el predictor. El `except Exception: pass` evita que un fallo de carga bloquee el arranque del servidor.

**Riesgo residual**: Si los archivos `.pkl` no están presentes (ej: deploy sin incluir `ml_models/`), el predictor falla silenciosamente y devuelve error en runtime.

---

## R5 — Dependencia de servicio externo para el chatbot LLM

| Atributo | Valor |
|----------|-------|
| Impacto | Medio |
| Probabilidad | Media |
| Archivos | `apps/chatbot/llm_fallback.py` |

**Descripción**: El fallback del chatbot depende de la API de OpenAI (GPT-4o mini). Si la API no está disponible, tiene rate limiting, o la `OPENAI_API_KEY` no está configurada, el fallback falla.

**Comportamiento actual**: El fallback retorna `None` en caso de excepción, y la vista del chatbot devuelve la respuesta vacía o un mensaje genérico. No hay reintentos automáticos.

**Mitigación sugerida**: Implementar respuesta de fallback estática cuando el LLM falla, con un mensaje como "Lo siento, en este momento no puedo responder esa pregunta. Por favor contacta a un asesor."

---

## R6 — Datos climáticos de Meteostat

| Atributo | Valor |
|----------|-------|
| Impacto | Medio |
| Probabilidad | Baja |
| Archivos | `apps/prediccion/predictor.py` |

**Descripción**: El predictor obtiene datos climáticos históricos de Quito via Meteostat en cada solicitud de forecast (con caché de 24h). Si Meteostat no responde o cambia su API, el predictor falla.

**Mitigación actual**: El predictor rellena valores faltantes con interpolación (`ffill`/`bfill`/media). Si Meteostat falla completamente, el predictor podría devolver predicciones de menor calidad o error.

---

## R7 — Aislamiento de tenants en schema público

| Atributo | Valor |
|----------|-------|
| Impacto | Alto |
| Probabilidad | Baja |
| Archivos | `apps/tenants/views.py`, `config/public_urls.py` |

**Descripción**: Las vistas del portal admin (`CompanyListView`, `CompanyDetailView`) tienen `authentication_classes = [NoAuthentication]` y `permission_classes = [AllowAny]`. La protección la provee el decorador `@admin_required`. Si se olvida ese decorador en un endpoint nuevo, quedaría expuesto sin autenticación.

**Mitigación**: El patrón `@admin_required` está centralizado en `admin_auth.py`. Los endpoints de solo lectura (GET) son públicos intencionalmente (listar empresas no expone datos sensibles).

---

## R8 — Sin HTTPS configurado

| Atributo | Valor |
|----------|-------|
| Impacto | Alto |
| Probabilidad | Alta (en despliegue sin configurar) |

**Descripción**: No existe configuración de TLS/HTTPS en el proyecto. Los tokens JWT transmitidos por HTTP plano son interceptables en redes no seguras.

**Mitigación**: En producción, usar nginx como reverse proxy con certificados SSL (Let's Encrypt).

---

## R9 — Sin rate limiting en el chatbot

| Atributo | Valor |
|----------|-------|
| Impacto | Medio |
| Probabilidad | Media |
| Archivos | `apps/chatbot/views.py`, `apps/chatbot/llm_fallback.py` |

**Descripción**: No hay límite de frecuencia en el endpoint `POST /api/chatbot/mensaje/`. Un usuario podría generar múltiples llamadas a la API de OpenAI automáticamente, incurriendo en costos.

**Mitigación sugerida**: Agregar `django-ratelimit` o DRF throttling por usuario/IP.

---

## R10 — Acoplamiento del predictor a schemas específicos

| Atributo | Valor |
|----------|-------|
| Impacto | Bajo |
| Probabilidad | Baja |
| Archivos | `apps/prediccion/predictor.py` (TENANT_ID_MAP) |

**Descripción**: El mapa `TENANT_ID_MAP` asocia schemas a IDs de modelos de forma estática:
```python
TENANT_ID_MAP = {"magic_world": 0, "papeleria": 1, "demo": 1}
```
Un tenant nuevo (`empresa3`) no tiene modelos entrenados y recibirá un error al solicitar predicciones.

**Mitigación actual**: El predictor devuelve un mensaje de error amigable si el tenant no está en el mapa. No bloquea otros módulos del ERP.

---

## Resumen de riesgos

| ID | Riesgo | Impacto | Prob. | Estado |
|----|--------|---------|-------|--------|
| R1 | Config insegura producción | A | A | Mitigable con .env |
| R2 | JWT en localStorage (XSS) | A | M | Aceptable en prototipo |
| R3 | SQL raw en chatbot handlers | A | B | Implementado correctamente |
| R4 | Cold start ML | M | A | Mitigado con warmup |
| R5 | Dependencia OpenAI API | M | M | Sin fallback de degradación |
| R6 | Meteostat indisponible | M | B | Mitigado con interpolación |
| R7 | Endpoint admin sin `@admin_required` | A | B | Patrón centralizado |
| R8 | Sin HTTPS | A | A | Requiere nginx en producción |
| R9 | Sin rate limiting chatbot | M | M | No implementado |
| R10 | Tenant nuevo sin modelo ML | B | B | Error manejado amigablemente |
