from django.http import HttpResponseForbidden, JsonResponse


class ModuleAccessMiddleware:
    """
    Bloquea acceso a módulos desactivados para el tenant.
    Usa process_view (post-URL resolution) para leer el namespace.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not (hasattr(request, "tenant") and request.tenant):
            return None

        resolver = getattr(request, "resolver_match", None)
        if not resolver or not resolver.namespace:
            return None

        module_code = resolver.namespace
        # Namespaces excluidos del control de acceso
        EXCLUDED = {"users", "chatbot"}
        if module_code in EXCLUDED:
            return None

        if not request.tenant.modules.filter(code=module_code).exists():
            return JsonResponse(
                {"detail": f"El módulo '{module_code}' no está habilitado para esta empresa."},
                status=403,
            )

        return None
