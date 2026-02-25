from django.contrib import admin
from django_tenants.admin import TenantAdminMixin
from .models import Company, Domain

@admin.register(Company)
class CompanyAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ("name", "paid_until", "on_trial")
    filter_horizontal = ("modules",)

@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ("domain", "tenant", "is_primary")