from rest_framework import serializers
from .models import CashMovement


class CashMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashMovement
        fields = [
            'id', 'type', 'category', 'description', 'amount',
            'date', 'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
