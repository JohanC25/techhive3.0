from rest_framework.views import APIView
from rest_framework.response import Response
from apps.core.models import Module

class ModuleListView(APIView):
    def get(self, request):
        modules = Module.objects.all()
        return Response([
            {
                "id": m.id,
                "code": m.code,
                "name": m.name
            }
            for m in modules
        ])