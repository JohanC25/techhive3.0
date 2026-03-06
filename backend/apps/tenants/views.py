from django.conf import settings
from django.core.management import call_command
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .admin_auth import admin_required, create_admin_token
from .models import Company, Domain


# ── Auth ──────────────────────────────────────────────────────────────────────

class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        key = request.data.get("key", "")
        master = getattr(settings, "ADMIN_MASTER_KEY", "")
        if not master:
            return Response({"detail": "Admin no configurado."}, status=503)
        if key == master:
            return Response({"token": create_admin_token()})
        return Response({"detail": "Clave incorrecta."}, status=401)


# ── Módulos disponibles ────────────────────────────────────────────────────────

class ModuleListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        from apps.core.models import Module
        modules = Module.objects.all().order_by("name")
        return Response([{"code": m.code, "name": m.name} for m in modules])


# ── Empresas (tenants) ────────────────────────────────────────────────────────

class CompanyListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        companies = Company.objects.prefetch_related("domains", "modules").all()
        data = []
        for c in companies:
            primary = c.domains.filter(is_primary=True).first()
            data.append({
                "id": c.id,
                "name": c.name,
                "schema_name": c.schema_name,
                "domain": primary.domain if primary else None,
                "on_trial": c.on_trial,
                "created_on": str(c.created_on),
                "modules": list(c.modules.values("code", "name")),
            })
        return Response(data)

    @admin_required
    def post(self, request):
        name           = request.data.get("name", "").strip()
        schema_name    = request.data.get("schema_name", "").strip().lower()
        domain         = request.data.get("domain", "").strip().lower()
        admin_username = request.data.get("admin_username", "").strip()
        admin_password = request.data.get("admin_password", "")
        module_codes   = request.data.get("modules", [])

        if not all([name, schema_name, domain, admin_username, admin_password]):
            return Response({"detail": "Todos los campos son requeridos."}, status=400)

        # Validar caracteres en schema_name
        import re
        if not re.match(r"^[a-z0-9_]+$", schema_name):
            return Response({"detail": "El schema solo puede tener letras minúsculas, números y guiones bajos."}, status=400)

        if Company.objects.filter(schema_name=schema_name).exists():
            return Response({"detail": f'El schema "{schema_name}" ya existe.'}, status=400)
        if Domain.objects.filter(domain=domain).exists():
            return Response({"detail": f'El dominio "{domain}" ya está en uso.'}, status=400)

        # Crear tenant (auto-crea schema en PostgreSQL)
        company = Company(schema_name=schema_name, name=name)
        try:
            company.save()
        except Exception as e:
            return Response({"detail": f"Error al crear empresa: {e}"}, status=500)

        Domain.objects.create(domain=domain, tenant=company, is_primary=True)

        # Asignar módulos
        if module_codes:
            from apps.core.models import Module
            modules = Module.objects.filter(code__in=module_codes)
            company.modules.set(modules)

        # Migrar el nuevo schema
        try:
            call_command("migrate_schemas", schema_name=schema_name, verbosity=0)
        except Exception as e:
            return Response({"detail": f"Empresa creada pero error en migraciones: {e}"}, status=201)

        # Crear usuario admin en el nuevo schema
        try:
            from django_tenants.utils import schema_context
            with schema_context(schema_name):
                from apps.users.models import User
                User.objects.create_superuser(
                    username=admin_username,
                    email="",
                    password=admin_password,
                    role="admin",
                )
        except Exception as e:
            return Response({"detail": f"Empresa creada pero error al crear usuario: {e}"}, status=201)

        return Response({
            "id": company.id,
            "name": name,
            "schema_name": schema_name,
            "domain": domain,
        }, status=201)


class CompanyDetailView(APIView):
    permission_classes = [AllowAny]

    @admin_required
    def delete(self, request, pk):
        try:
            company = Company.objects.get(pk=pk)
        except Company.DoesNotExist:
            return Response({"detail": "No encontrado."}, status=404)
        company.delete()
        return Response(status=204)


class CompanyModulesView(APIView):
    """PUT /api/admin/companies/{pk}/modules/ — reemplaza los módulos activos."""
    permission_classes = [AllowAny]

    @admin_required
    def put(self, request, pk):
        try:
            company = Company.objects.get(pk=pk)
        except Company.DoesNotExist:
            return Response({"detail": "No encontrado."}, status=404)

        module_codes = request.data.get("modules", [])
        from apps.core.models import Module
        modules = Module.objects.filter(code__in=module_codes)
        company.modules.set(modules)

        return Response({
            "id": company.id,
            "modules": list(company.modules.values("code", "name")),
        })
