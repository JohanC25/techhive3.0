import unicodedata
import re
import time
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


def _normalizar(texto: str) -> str:
    """Convierte texto a minúsculas sin tildes ni caracteres especiales."""
    nfkd = unicodedata.normalize('NFKD', texto)
    sin_tildes = ''.join(c for c in nfkd if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]', '', sin_tildes.lower())


def generar_username(first_name: str, last_name: str, cedula: str) -> str:
    """Genera username: primera letra nombre + apellido + últimos 3 dígitos cédula.
    Si no hay cédula usa los últimos 4 dígitos del timestamp."""
    inicial = _normalizar(first_name[:1]) if first_name else 'u'
    apellido = _normalizar(last_name.split()[0]) if last_name else 'user'
    if len(cedula) >= 3:
        sufijo = cedula[-3:]
    elif cedula:
        sufijo = cedula
    else:
        sufijo = str(int(time.time()))[-4:]
    return f"{inicial}{apellido}{sufijo}"


def username_disponible(base: str, excluir_id: int | None = None) -> str:
    """Retorna el username base si está libre, o base+número si ya existe."""
    qs = User.objects.filter(username=base)
    if excluir_id:
        qs = qs.exclude(pk=excluir_id)
    if not qs.exists():
        return base
    i = 1
    while True:
        candidato = f"{base}{i}"
        qs2 = User.objects.filter(username=candidato)
        if excluir_id:
            qs2 = qs2.exclude(pk=excluir_id)
        if not qs2.exists():
            return candidato
        i += 1


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'role', 'phone', 'cedula', 'is_active', 'date_joined',
        ]
        read_only_fields = ['date_joined']


class UserCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False, allow_blank=True, default='')
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=False, allow_blank=True, default='')

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'role', 'phone', 'cedula', 'password', 'password2',
        ]

    def validate(self, attrs):
        password = attrs.get('password', '')
        password2 = attrs.pop('password2', '')
        # Solo validar coincidencia si se envió password2
        if password2 and password != password2:
            raise serializers.ValidationError({'password': 'Las contraseñas no coinciden.'})

        # Teléfono obligatorio para clientes
        if attrs.get('role') == 'client' and not attrs.get('phone', '').strip():
            raise serializers.ValidationError({'phone': 'El teléfono es obligatorio para clientes.'})

        # Auto-generar username si se tienen nombre y apellido (cedula opcional)
        first_name = attrs.get('first_name', '').strip()
        last_name = attrs.get('last_name', '').strip()
        cedula = attrs.get('cedula', '').strip()
        if first_name and last_name:
            base = generar_username(first_name, last_name, cedula)
            attrs['username'] = username_disponible(base)
        elif not attrs.get('username', '').strip():
            raise serializers.ValidationError({'username': 'El nombre de usuario es requerido.'})

        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('La contraseña actual es incorrecta.')
        return value

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
