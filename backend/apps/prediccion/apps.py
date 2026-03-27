from django.apps import AppConfig


class PrediccionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.prediccion"
    verbose_name = "Predicción de Ventas"

    def ready(self):
        """Pre-carga el predictor ML al arrancar el servidor para evitar cold start."""
        import threading

        def _warmup():
            try:
                from apps.prediccion.predictor import get_predictor
                get_predictor()
            except Exception:
                pass  # No bloquear el arranque si falla

        threading.Thread(target=_warmup, daemon=True).start()
