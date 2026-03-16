from rest_framework import serializers
from .models import CashMovement, CashSession


class CashMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashMovement
        fields = [
            'id', 'type', 'category', 'description', 'amount',
            'date', 'notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class CashSessionSerializer(serializers.ModelSerializer):
    opened_by_name = serializers.SerializerMethodField()

    class Meta:
        model = CashSession
        fields = [
            'id', 'date', 'opened_by', 'opened_by_name',
            'opening_amount', 'closed_at', 'closing_amount', 'created_at',
        ]
        read_only_fields = ['opened_by', 'created_at']

    def get_opened_by_name(self, obj):
        if obj.opened_by:
            return obj.opened_by.get_full_name() or obj.opened_by.username
        return None
