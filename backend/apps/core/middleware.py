from django.http import HttpResponseForbidden


class ModuleAccessMiddleware:
    """
    Prevent access to disabled modules per tenant.
    Uses URL namespace as module code.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if hasattr(request, "tenant") and request.tenant:
            resolver = request.resolver_match

            if resolver and resolver.namespace:
                module_code = resolver.namespace

                if not request.tenant.modules.filter(code=module_code).exists():
                    return HttpResponseForbidden("Module not enabled for this tenant.")

        return self.get_response(request)
