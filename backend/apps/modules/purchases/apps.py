from django.apps import AppConfig


class PurchasesConfig(AppConfig):
    name = 'apps.modules.purchases'

    def ready(self):
        import apps.modules.purchases.signals  # noqa: F401
