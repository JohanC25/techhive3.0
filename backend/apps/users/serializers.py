# apps/users/serializers.py

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CedulaTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'cedula_ruc'