from rest_framework import serializers
from .models import ServiceTicket


class ServiceTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceTicket
        fields = [
            'id', 'client_name', 'client_phone', 'client_email',
            'device', 'serial_number', 'accessories',
            'problem', 'diagnosis', 'solution',
            'estimated_cost', 'final_cost',
            'status', 'priority',
            'received_at', 'promised_at', 'completed_at',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['received_at', 'created_at', 'updated_at']
