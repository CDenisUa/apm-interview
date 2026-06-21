"""Todo ORM model — mapped onto the shared `todos` table (managed = False)."""
# Core
import uuid
from django.db import models


class Todo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    completed = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, default="medium")  # low|medium|high
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "todos"
