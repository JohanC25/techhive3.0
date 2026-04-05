# 09 — Cómo Ejecutar el Sistema

## Requisitos previos

| Herramienta | Versión mínima | Verificar |
|------------|----------------|-----------|
| Python | 3.11+ | `python --version` |
| PostgreSQL | 14+ | `psql --version` |
| Node.js | 20.19+ o 22.12+ | `node --version` |
| npm | 10+ | `npm --version` |

---

## 1. Clonar y preparar

```bash
git clone <repo>
cd techhive3.0
```

---

## 2. Backend — Django

### 2.1 Entorno virtual

```bash
cd backend
python -m venv venv

# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 2.2 Instalar dependencias

```bash
pip install -r requirements.txt
```

> **Nota**: `catboost` y `meteostat` son pesados (~500MB). La primera instalación puede tardar varios minutos.

### 2.3 Variables de entorno

Crear `backend/.env` a partir de `.env.example`:

```bash
cp .env.example .env
```

Editar `.env`:

```dotenv
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True

DB_NAME=techhive_db
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432

OPENAI_API_KEY=sk-...              # para chatbot LLM fallback
ADMIN_MASTER_KEY=clave-admin-segura
```

### 2.4 Crear base de datos PostgreSQL

```bash
createdb techhive_db
# o desde psql:
# CREATE DATABASE techhive_db;
```

### 2.5 Migraciones y setup inicial

```bash
# 1. Migraciones del schema público (tablas compartidas: tenants, core)
python manage.py migrate_schemas --shared

# 2. Migraciones de todos los tenants existentes
python manage.py migrate_schemas

# 3. Crear el tenant 'public' (requerido por django-tenants)
python manage.py setup_public_tenant

# 4. Poblar tabla core_module con los módulos disponibles
python manage.py seed_modules
```

### 2.6 Crear un tenant de ejemplo

Usando el portal admin o directamente en Django shell:

```python
# python manage.py shell
from apps.tenants.models import Company, Domain
from django_tenants.utils import schema_context

# Crear empresa
c = Company(schema_name='mi_empresa', name='Mi Empresa')
c.save()  # auto-crea schema PostgreSQL

# Crear dominio
Domain.objects.create(domain='mi_empresa.localhost', tenant=c, is_primary=True)

# Asignar módulos
from apps.core.models import Module
c.modules.set(Module.objects.all())

# Migrar schema
from django.core.management import call_command
call_command('migrate_schemas', schema_name='mi_empresa', verbosity=1)

# Crear usuario admin en el tenant
with schema_context('mi_empresa'):
    from apps.users.models import User
    User.objects.create_superuser('admin', '', 'password123', role='admin')
```

### 2.7 (Opcional) Cargar datos demo

```bash
# Cargar datos de demostración en tenant 'demo'
python manage.py seed_demo
```

### 2.8 Arrancar el servidor

```bash
python manage.py runserver
```

> El backend estará disponible en `http://localhost:8000`

---

## 3. Frontend — Vue 3

```bash
cd frontend

# Instalar dependencias
npm install

# Servidor de desarrollo (con proxy a :8000)
npm run dev
```

> El frontend estará disponible en `http://localhost:5173`

---

## 4. Configuración del proxy (Vite)

El archivo `vite.config.ts` debe tener el proxy configurado para redirigir llamadas API al backend:

```typescript
// vite.config.ts (si no existe esta config, agregarla)
server: {
  proxy: {
    '/api': 'http://localhost:8000',
  }
}
```

---

## 5. Acceder al sistema

### Portal de empresa (tenant)

Editar `/etc/hosts` (Linux/Mac) o `C:\Windows\System32\drivers\etc\hosts` (Windows):

```
127.0.0.1  magic_world.localhost
127.0.0.1  papeleria.localhost
127.0.0.1  demo.localhost
```

Abrir: `http://magic_world.localhost:5173`

### Portal de administración maestro

Editar hosts:
```
127.0.0.1  admin.localhost
```

Abrir: `http://admin.localhost:5173`

Credenciales: la `ADMIN_MASTER_KEY` del `.env`.

---

## 6. Evaluación del chatbot

```bash
cd backend

# Evaluar router staff (67 casos)
python apps/chatbot/evaluar_chatbot.py

# Evaluar router cliente (56 casos)
python apps/chatbot/evaluar_chatbot.py --modo cliente
```

---

## 7. Comandos útiles de gestión

```bash
# Ver todos los tenants registrados
python manage.py shell -c "from apps.tenants.models import Company; print(list(Company.objects.values('name','schema_name')))"

# Ejecutar migraciones solo para un tenant específico
python manage.py migrate_schemas --schema=magic_world

# Crear superusuario en un tenant
python manage.py createsuperuser --schema=magic_world

# Cargar ventas desde CSV en un tenant
python manage.py cargar_ventas --schema=magic_world --archivo=ventas.csv
```

---

## 8. Build de producción

```bash
# Frontend
cd frontend
npm run build          # genera dist/
npm run type-check     # verifica tipos TypeScript

# Backend (con gunicorn)
cd backend
gunicorn config.wsgi:application --workers 4 --bind 0.0.0.0:8000
```

> **Para producción**: cambiar `DEBUG=False`, `ALLOWED_HOSTS=[tu-dominio.com]`, usar HTTPS, configurar `STATIC_ROOT` y servir estáticos con nginx.
