from rest_framework import serializers

from .models import Supplier


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            "id", "nit", "person_type", "legal_name", "trade_name", "phone",
            "email", "address", "city", "delivery_days", "is_active",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "is_active", "created_at", "updated_at"]
        # El NIT repetido se responde como 409 DUPLICADO desde la vista, no como 400
        extra_kwargs = {"nit": {"validators": []}}