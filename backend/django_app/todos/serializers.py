# Core
from rest_framework import serializers
# Local
from .models import Todo


PRIORITY_CHOICES = ["low", "medium", "high"]


class TodoSerializer(serializers.ModelSerializer):
    priority = serializers.ChoiceField(choices=PRIORITY_CHOICES, default="medium")
    dueDate = serializers.DateTimeField(
        source="due_date", allow_null=True, required=False
    )
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = Todo
        fields = [
            "id",
            "title",
            "description",
            "completed",
            "priority",
            "dueDate",
            "createdAt",
            "updatedAt",
        ]
        read_only_fields = ["id"]
