"""
Endpoint de predicción de ventas — TechHive v3.
GET /api/prediccion/?dias=7
"""

import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class PrediccionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        GET /api/prediccion/?dias=7

        Query params:
          dias (int, default=7): número de días a predecir (1-90)

        Responses:
          200: {"predicciones": [...], "tenant": str, "horizonte_dias": int}
          400: {"error": str}  — historial insuficiente o tenant sin modelo
          500: {"error": str}  — error interno
        """
        try:
            horizon = int(request.query_params.get("dias", 7))
        except (ValueError, TypeError):
            horizon = 7
        horizon = max(1, min(horizon, 90))

        # django-tenants pone el tenant activo en request.tenant
        tenant_slug = getattr(request.tenant, "schema_name", "demo")

        try:
            from .predictor import get_predictor
            predictor = get_predictor()
            resultado = predictor.forecast(tenant_slug=tenant_slug, horizon=horizon)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            logger.exception("Error en PrediccionView para tenant=%s: %s", tenant_slug, exc)
            return Response(
                {"error": "Error interno al generar la predicción. Revisa los logs del servidor."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response({
            "predicciones": resultado,
            "tenant": tenant_slug,
            "horizonte_dias": horizon,
        })
