# 12 — Vacíos de Documentación Detectados

Análisis de lo que **no está documentado** en el código fuente, con propuestas de acción.

---

## Vacíos en código

### V1 — Ausencia de docstrings en serializers

**Afecta**: `apps/modules/sales/serializers.py`, `inventory/serializers.py`, `purchases/serializers.py`

**Problema**: Los serializers son críticos (manejan validación, creación anidada, descuento de stock) pero no tienen docstrings que expliquen su lógica de negocio.

**Propuesta**: Agregar docstring a `VentaSerializer.create()` explicando el flujo: creación de items → descuento de stock → recalculate_total → CashMovement.

---

### V2 — Sin tests unitarios ni de integración

**Afecta**: Todos los archivos `tests.py` en los módulos (están vacíos o son boilerplate).

**Problema**: El único sistema de pruebas automatizado es el evaluador del chatbot (`evaluar_chatbot.py`). No hay tests para:
- Lógica de negocios de serializers
- Aislamiento entre tenants (más allá de los casos del chatbot)
- Endpoints API (integración DRF)
- Flujo de señales (purchases → CashMovement)

**Propuesta**: Implementar tests con `pytest-django` o el framework de testing de DRF (`APITestCase`).

---

### V3 — Sin documentación del modelo ML en producción

**Afecta**: `apps/prediccion/predictor.py`, `ml_models/metadata_v22.json`

**Problema**: `predictor.py` tiene comentarios internos, pero no existe un documento que explique:
- Cómo re-entrenar el modelo
- Cómo actualizar `metadata_v22.json` con nuevos pesos
- Cómo agregar un nuevo tenant al predictor
- El proceso de versioning (v1 → v22)

**Propuesta**: Crear `docs/ml_predictor.md` con la arquitectura del ensemble, el proceso de entrenamiento y el procedimiento de actualización.

---

### V4 — Sin documentación del notebook de entrenamiento

**Afecta**: `ModeloPrediccionVentasFinalDjango.ipynb`

**Problema**: El notebook de 29 celdas no tiene README que explique cómo ejecutarlo, qué datos necesita (CSV de ventas históricas), ni qué produce (5 `.pkl` + `metadata_v22.json`).

**Propuesta**: Agregar celda Markdown al inicio del notebook con prerequisitos, datos de entrada y salidas esperadas. O crear `docs/entrenamiento_modelo.md`.

---

### V5 — Sin schema de base de datos documentado

**Afecta**: Todos los modelos del sistema.

**Problema**: No existe un diagrama entidad-relación (ERD) ni una descripción formal del schema de base de datos.

**Propuesta**: Generar ERD con `django-extensions` + graphviz:
```bash
python manage.py graph_models -a > er_diagram.dot
dot -Tpng er_diagram.dot -o docs/er_diagram.png
```

---

### V6 — Variables de entorno sin `.env.example` completo

**Afecta**: `backend/.env.example` (si existe)

**Problema**: No se verificó si `.env.example` lista todas las variables requeridas. Variables documentadas en README: `SECRET_KEY`, `DB_*`. Variables no mencionadas en README: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `ADMIN_MASTER_KEY`.

**Propuesta**: Verificar que `.env.example` incluya todas las variables con descripción:
```dotenv
# Seguridad
SECRET_KEY=            # Clave secreta Django (50+ chars aleatorios)
DEBUG=False            # True solo en desarrollo
ALLOWED_HOSTS=         # Dominios separados por coma

# Base de datos
DB_NAME=techhive_db
DB_USER=postgres
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432

# Chatbot LLM
OPENAI_API_KEY=sk-...  # GPT-4o mini fallback del chatbot

# Portal admin
ADMIN_MASTER_KEY=      # Clave maestra del portal de administración
```

---

### V7 — Sin CHANGELOG del modelo ML

**Afecta**: `apps/prediccion/ml_models/`

**Problema**: El modelo tiene 22 versiones de mejora continua pero no existe un CHANGELOG que documente qué cambió entre versiones.

---

### V8 — Módulo `reports` sin ViewSet ni router DRF

**Afecta**: `apps/modules/reports/views.py`, `urls.py`

**Problema**: Los reportes usan `@api_view` (función simple) en lugar de ViewSets. No hay documentación de los parámetros de filtrado disponibles en cada endpoint.

---

### V9 — Frontend sin documentación de componentes

**Afecta**: `frontend/src/components/`, `frontend/src/views/`

**Problema**: No existe storybook, ni JSDoc, ni README por componente que explique props, eventos emitidos o comportamiento esperado de `ChatBot.vue`, `AppLayout.vue`, etc.

---

## Vacíos en el README principal

El `README.md` raíz menciona:
- ✅ Inicio rápido
- ✅ Arquitectura general
- ✅ Módulos disponibles
- ✅ Roles de usuario
- ❌ No menciona `OPENAI_API_KEY` como requisito para el chatbot LLM
- ❌ No documenta el modelo ML (nombre, métricas, cómo se integra)
- ❌ No documenta el evaluador del chatbot
- ❌ No documenta los grupos de usuarios (Group M — aislamiento de tenants)
- ❌ Los links a `./backend/README.md` y `./frontend/README.md` apuntan a archivos que no existen

---

## Resumen de acciones recomendadas

| Prioridad | Acción |
|-----------|--------|
| Alta | Crear `.env.example` completo con todas las variables |
| Alta | Agregar tests de integración para serializers y endpoints |
| Alta | Crear `backend/README.md` y `frontend/README.md` (mencionados en raíz pero inexistentes) |
| Media | Crear `docs/ml_predictor.md` con proceso de entrenamiento |
| Media | Generar ERD automático con `django-extensions` |
| Baja | Agregar docstrings a serializers complejos |
| Baja | Implementar rate limiting en chatbot |
