# Core
from rest_framework import serializers
# Local
from .models import BusinessItem


class BusinessItemSerializer(serializers.ModelSerializer):
    # Expose camelCase `updatedAt` (read-only, set on the server) and emit
    # revenue as a JSON number rather than a string so the shape matches
    # FastAPI exactly.
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)
    revenue = serializers.FloatField()

    class Meta:
        model = BusinessItem
        fields = ["id", "name", "country", "status", "revenue", "updatedAt", "owner"]
        read_only_fields = ["id"]
