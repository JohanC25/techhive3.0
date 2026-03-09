"""
JWT ligero para el portal admin (sin User model en el schema público).
"""
import datetime
from functools import wraps

import jwt
from django.conf import settings
from rest_framework.response import Response

_ALG = "HS256"
_DURATION = datetime.timedelta(hours=10)


def create_admin_token() -> str:
    payload = {
        "admin": True,
        "exp": datetime.datetime.utcnow() + _DURATION,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=_ALG)


def verify_admin_token(token: str) -> bool:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[_ALG])
        return payload.get("admin") is True
    except jwt.InvalidTokenError:
        return False


def admin_required(func):
    """Decorator para métodos de APIView que exige admin JWT."""
    @wraps(func)
    def wrapper(self, request, *args, **kwargs):
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth.startswith("Bearer "):
            return Response({"detail": "Admin token requerido."}, status=401)
        if not verify_admin_token(auth[7:]):
            return Response({"detail": "Token inválido o expirado."}, status=401)
        return func(self, request, *args, **kwargs)
    return wrapper
