# 06 — Seguridad

## 1. Autenticación JWT

TechHive 3.0 usa **JSON Web Tokens** via `djangorestframework-simplejwt 5.5`.

### Flujo de autenticación

```
1. POST /api/login/ { username, password }
        │
        ▼
   DRF SimpleJWT → valida credenciales → genera par de tokens
        │
        ▼
   { "access": "eyJ...", "refresh": "eyJ..." }
        │
        ▼
   Frontend guarda en localStorage:
     - access_token  (corta duración, enviado en cada request)
     - refresh_token (larga duración, solo para renovar)
        │
        ▼
   Cada request: Authorization: Bearer <access_token>
        │
        ▼
   En 401: POST /api/refresh/ { refresh }
         → nuevo access_token
         → reintenta petición original
```

### Configuración DRF

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}
```

### Renovación automática (frontend)

El interceptor de respuesta en `src/services/api.ts` implementa un patrón de cola para evitar múltiples intentos de refresh concurrentes:

```typescript
if (error.response?.status === 401 && !original._retry) {
    // Solo un refresh en vuelo a la vez
    // Las otras peticiones se encolan y resuelven juntas
}
```

---

## 2. Sistema de roles y permisos

### Roles de usuario (por tenant)

| Rol | Descripción | Acceso |
|-----|-------------|--------|
| `admin` | Administrador del tenant | Acceso total al ERP |
| `manager` | Gerente | Igual que admin (puede gestionar usuarios) |
| `employee` | Empleado | Acceso a módulos habilitados, sin gestión de usuarios |
| `client` | Cliente externo | Solo catálogo y chatbot de cliente |

El rol se almacena en el modelo `User` (`users_user.role`), incluido en el payload JWT.

### Clase de permiso `IsNotClient` (`apps/core/permissions.py`)

```python
class IsNotClient(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'role', '') != 'client'
        )
```

Aplicada en todos los ViewSets de módulos internos (inventario, ventas, compras, caja, reportes, servicio técnico). Devuelve HTTP 403 si el usuario tiene rol `client`.

### Clase `IsAdminOrManager` (`apps/users/views.py`)

Solo admin y manager pueden crear, editar o eliminar usuarios.

### Permisos por acción en `UserViewSet`

```python
def get_permissions(self):
    if action in ['create', 'destroy', 'update', 'partial_update']:
        return [IsAuthenticated(), IsAdminOrManager()]
    if action in ['me', 'update_me', 'change_password', 'modules']:
        return [IsAuthenticated()]   # cualquier usuario
    return [IsAuthenticated(), IsNotClient()]
```

---

## 3. Aislamiento de tenants

### Aislamiento de datos

El aislamiento es **a nivel de motor de base de datos**: cada tenant tiene su propio schema PostgreSQL. No existe filtrado por campo `tenant_id` en las queries — el schema activo lo garantiza el middleware.

```python
# TenantMainMiddleware (django-tenants)
connection.set_schema(company.schema_name)
```

Después de esto, toda la ORM opera exclusivamente en ese schema. Es imposible que una query filtre accidentalmente datos de otro tenant.

### Aislamiento en el chatbot

El chatbot verifica explícitamente el schema activo:

```python
from django.db import connection
tenant_schema = connection.schema_name
```

El `ChatSession` almacena `tenant_schema` para asegurar que el historial pertenece al contexto correcto.

Los SQL raw en los handlers no llevan prefijo de schema — dependen de que `set_schema()` ya fue llamado.

### Prueba de aislamiento (Grupo M)

El evaluador `evaluar_chatbot.py` incluye el **Grupo M** (aislamiento entre tenants) para verificar que los datos de un tenant no son accesibles desde otro.

---

## 4. Control de acceso a módulos

### `ModuleAccessMiddleware` (`apps/core/middleware.py`)

Bloquea acceso a módulos no habilitados para el tenant activo:

```python
module_code = resolver.namespace  # 'sales', 'inventory', etc.
EXCLUDED = {"users", "chatbot"}   # siempre accesibles

if not request.tenant.modules.filter(code=module_code).exists():
    return JsonResponse({"detail": "módulo no habilitado"}, status=403)
```

**Excepción**: el endpoint `inventory/product-catalog/` (catálogo público) es accesible aunque el módulo `inventory` no esté habilitado:

```python
if module_code == "inventory" and resolver.url_name == "product-catalog":
    return None
```

---

## 5. Seguridad del chatbot cliente

Los handlers de cliente nunca exponen:
- `cost` (precio de costo)
- `sku` exacto
- Cantidad exacta de stock (solo `stock > 0`)
- Datos de ventas o movimientos de caja
- Información de otros clientes

```sql
SELECT name, description, price,
       (stock > 0) AS available,  -- solo booleano, no cantidad
       category
FROM inventory_product
WHERE is_active = TRUE
```

El **Grupo K** del evaluador (8 casos de seguridad) verifica que el bot cliente nunca responda con datos internos.

El `SYSTEM_PROMPT_CLIENTE` enviado al LLM incluye prohibiciones explícitas:
```
"Nunca reveles precios de costo, datos de otros clientes, movimientos de caja,
ni información operativa interna de la empresa."
```

---

## 6. Autenticación del portal de administración

El portal admin (`admin.localhost`) no usa JWT de usuario. Usa una **clave maestra** (`ADMIN_MASTER_KEY` en `.env`):

```python
# apps/tenants/admin_auth.py
@admin_required  # decorador que verifica el token admin
def post(self, request): ...
```

```python
# apps/tenants/views.py — AdminLoginView
if key == master:
    return Response({"token": create_admin_token()})
```

El token admin es un JWT firmado con `ADMIN_MASTER_KEY`, independiente del sistema de usuarios de los tenants.

---

## 7. Configuración de seguridad en settings.py

```python
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-me-in-production')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*']  # ← debe restringirse en producción
ADMIN_MASTER_KEY = os.getenv("ADMIN_MASTER_KEY", "change-me-in-production")
```

**Validadores de contraseña** activos:
- `UserAttributeSimilarityValidator`
- `MinimumLengthValidator`
- `CommonPasswordValidator`
- `NumericPasswordValidator`

---

## 8. Riesgos de seguridad identificados (ver también doc 11)

| Riesgo | Estado actual |
|--------|---------------|
| `ALLOWED_HOSTS = ['*']` | Solo seguro en desarrollo; producción requiere restricción |
| `DEBUG = True` por defecto | Expone tracebacks en producción si no se configura `.env` |
| SQL raw en handlers del chatbot | Parámetros siempre escapados via `cursor.execute(q, [params])` |
| Tokens JWT en localStorage | Susceptible a XSS; alternativa: httpOnly cookies |
| `ADMIN_MASTER_KEY` sin rotación | La clave maestra no tiene expiración automática |
