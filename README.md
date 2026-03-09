# TechHive 3.0

ERP multi-tenant para pequeñas y medianas empresas. Cada empresa (tenant) corre en su propio esquema de PostgreSQL con módulos activables de forma independiente.

## Arquitectura

```
techhive3.0/
├── backend/        Django 6 + DRF + django-tenants
└── frontend/       Vue 3 + Vite + TypeScript + Pinia
```

**Multi-tenancy**: La URL determina el tenant (`empresa.localhost`). Django-tenants aísla los datos de cada empresa en un esquema PostgreSQL independiente. El schema `public` alberga los datos de administración global (tenants, dominios, módulos).

**Módulos disponibles por tenant:**

| Código              | Descripción                        |
|---------------------|------------------------------------|
| `inventory`         | Catálogo de productos e inventario |
| `sales`             | Registro y consulta de ventas      |
| `purchases`         | Compras y proveedores              |
| `cash_management`   | Caja y movimientos de efectivo     |
| `reports`           | Reportes y métricas                |
| `technical_service` | Órdenes de servicio técnico        |

## Inicio rápido

### Requisitos

- Python 3.11+
- Node.js 20+ o 22+
- PostgreSQL 14+

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env              # editar con tus credenciales

# Crear base de datos PostgreSQL
createdb techhive_db

# Migraciones y setup inicial
python manage.py migrate_schemas --shared
python manage.py migrate_schemas
python manage.py setup_public_tenant
python manage.py seed_modules

# Servidor de desarrollo
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

El frontend estará disponible en `http://localhost:5173`.

## Portales

| Portal              | URL de acceso                   | Descripción                                |
|---------------------|---------------------------------|--------------------------------------------|
| Admin maestro       | `http://localhost:5173/admin`   | Gestión de empresas, dominios y módulos    |
| Tenant (empresa)    | `http://<dominio>:5173`         | ERP completo para el equipo de la empresa  |

## Roles de usuario (por tenant)

| Rol       | Acceso                                                      |
|-----------|-------------------------------------------------------------|
| `admin`   | Acceso total al ERP del tenant                             |
| `staff`   | Acceso a módulos habilitados, sin gestión de usuarios       |
| `client`  | Solo catálogo público de productos y chatbot de compras     |

## Chatbot

El chatbot está integrado en el ERP y adapta su comportamiento según el rol:

- **Staff/Admin**: consultas de ventas, tendencias, comparaciones por período
- **Cliente**: búsqueda en catálogo, precios y disponibilidad de productos

Incluye fallback con Claude Haiku API (opcional) para mensajes fuera del alcance del router regex. Requiere configurar `ANTHROPIC_API_KEY` en el `.env`.

## Documentación detallada

- [Backend](./backend/README.md) — configuración Django, endpoints API, comandos de gestión
- [Frontend](./frontend/README.md) — configuración Vue/Vite, rutas, stores
