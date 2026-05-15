# apps/tenants/api.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db import transaction, connection
from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context, get_public_schema_name
import re

from .models import Company, Domain


class CompanyView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        if connection.schema_name != get_public_schema_name():
            return Response({"error": "Not allowed"}, status=403)
        companies = Company.objects.all()
        return Response([
            {
                "id": c.id,
                "name": c.name,
                "schema": c.schema_name,
                "on_trial": c.on_trial,
            }
            for c in companies
        ])

    @transaction.atomic
    def post(self, request):
        name = request.data.get("name")
        schema_name = request.data.get("schema_name")
        if not re.match(r'^[a-z0-9_]+$', schema_name):
            return Response({"error": "Invalid schema name"}, status=400)
        domain_name = request.data.get("domain")
        admin_email = request.data.get("admin_email")
        admin_password = request.data.get("admin_password")

        if not all([name, schema_name, domain_name, admin_email, admin_password]):
            return Response({"error": "All fields required"}, status=400)

        company = Company.objects.create(
            name=name,
            schema_name=schema_name,
        )

        Domain.objects.create(
            domain=domain_name,
            tenant=company,
            is_primary=True,
        )

        with schema_context(schema_name):
            User = get_user_model()
            User.objects.create_superuser(
                username=admin_email,
                email=admin_email,
                password=admin_password
            )

        return Response({"message": "Company created successfully"})