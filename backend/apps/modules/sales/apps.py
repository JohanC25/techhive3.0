from django.apps import AppConfig


class SalesConfig(AppConfig):
    name = 'apps.modules.sales'

    def ready(self):
        import apps.modules.sales.signals  # noqa: F401
