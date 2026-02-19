from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

class Company(TenantMixin):
    name = models.CharField(max_length=255)
    paid_until = models.DateField(null=True, blank=True)
    on_trial = models.BooleanField(default=True)

    modules = models.ManyToManyField(
        "core.Module",
        blank=True,
        related_name="companies"
    )

    auto_create_schema = True

    def __str__(self):
        return self.name


class Domain(DomainMixin):
    pass
