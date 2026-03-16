from rest_framework import serializers
from .models import ServiceTicket


class ServiceTicketSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()
    client_phone = serializers.SerializerMethodField()
    client_email = serializers.SerializerMethodField()

    class Meta:
        model = ServiceTicket
        fields = [
            'id', 'client',
            'client_name', 'client_phone', 'client_email',
            'device', 'serial_number', 'accessories',
            'problem', 'diagnosis', 'solution',
            'estimated_cost', 'final_cost',
            'status', 'priority',
            'received_at', 'promised_at', 'completed_at',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['received_at', 'created_at', 'updated_at',
                            'client_name', 'client_phone', 'client_email']

    def get_client_name(self, obj):
        if obj.client:
            name = f"{obj.client.first_name} {obj.client.last_name}".strip()
            return name or obj.client.username
        return obj.client_name

    def get_client_phone(self, obj):
        if obj.client:
            return obj.client.phone or ''
        return obj.client_phone

    def get_client_email(self, obj):
        if obj.client:
            return obj.client.email or ''
        return obj.client_email

    def validate(self, data):
        if not data.get('client'):
            raise serializers.ValidationError({'client': 'Debe seleccionar un cliente.'})
        return data

    def _sync_client_fields(self, validated_data):
        client = validated_data.get('client')
        if client:
            name = f"{client.first_name} {client.last_name}".strip()
            validated_data['client_name'] = name or client.username
            validated_data['client_phone'] = client.phone or ''
            validated_data['client_email'] = client.email or ''
        return validated_data

    def create(self, validated_data):
        self._sync_client_fields(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        self._sync_client_fields(validated_data)
        return super().update(instance, validated_data)
