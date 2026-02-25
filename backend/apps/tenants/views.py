from rest_framework.permissions import IsAdminUser
from apps.tenants.models import Company
from rest_framework.response import Response
from rest_framework.views import APIView

class CompanyListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        companies = Company.objects.all()

        return Response([
            {
                "id": c.id,
                "name": c.name,
                "schema": c.schema_name,
                "modules": list(c.modules.values_list("code", flat=True)),
                "on_trial": c.on_trial,
            }
            for c in companies
        ]) 
    
class UpdateCompanyModulesView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, company_id):
        module_ids = request.data.get("modules", [])

        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({"error": "Company not found"}, status=404)

        company.modules.set(module_ids)

        return Response({"message": "Modules updated"})