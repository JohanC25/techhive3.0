"""
Script de reparación: crea users_user en cada schema y marca la migración
como aplicada para que migrate_schemas pueda continuar.

Uso:  python manage.py shell < fix_migrations.py
"""
from django.db import connection
from django_tenants.utils import schema_context, get_tenant_model

TenantModel = get_tenant_model()

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS "users_user" (
    "id"            bigserial    NOT NULL PRIMARY KEY,
    "password"      varchar(128) NOT NULL,
    "last_login"    timestamptz  NULL,
    "is_superuser"  boolean      NOT NULL DEFAULT false,
    "username"      varchar(150) NOT NULL UNIQUE,
    "first_name"    varchar(150) NOT NULL DEFAULT '',
    "last_name"     varchar(150) NOT NULL DEFAULT '',
    "email"         varchar(254) NOT NULL DEFAULT '',
    "is_staff"      boolean      NOT NULL DEFAULT false,
    "is_active"     boolean      NOT NULL DEFAULT true,
    "date_joined"   timestamptz  NOT NULL DEFAULT NOW(),
    "role"          varchar(20)  NOT NULL DEFAULT 'employee',
    "phone"         varchar(20)  NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS "users_user_groups" (
    "id"       bigserial NOT NULL PRIMARY KEY,
    "user_id"  bigint    NOT NULL REFERENCES "users_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "group_id" integer   NOT NULL REFERENCES "auth_group"  ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("user_id", "group_id")
);

CREATE TABLE IF NOT EXISTS "users_user_user_permissions" (
    "id"            bigserial NOT NULL PRIMARY KEY,
    "user_id"       bigint    NOT NULL REFERENCES "users_user"      ("id") DEFERRABLE INITIALLY DEFERRED,
    "permission_id" integer   NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("user_id", "permission_id")
);
"""

MARK_SQL = """
INSERT INTO django_migrations (app, name, applied)
SELECT 'users', '0001_initial', NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM django_migrations
    WHERE app = 'users' AND name = '0001_initial'
);
"""

# Fix schema public primero
with schema_context('public'):
    with connection.cursor() as cur:
        cur.execute(CREATE_SQL)
        cur.execute(MARK_SQL)
print("  [OK] public")

# Fix schemas de cada tenant
for tenant in TenantModel.objects.all():
    with schema_context(tenant.schema_name):
        with connection.cursor() as cur:
            cur.execute(CREATE_SQL)
            cur.execute(MARK_SQL)
    print(f"  [OK] {tenant.schema_name}")

print("\nListo. Ahora ejecuta:  python manage.py migrate_schemas")
