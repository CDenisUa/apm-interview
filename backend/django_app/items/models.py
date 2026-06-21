"""
BusinessItem ORM model.

`managed = False` is the key line: Django will NEVER create, alter, or drop
this table. The schema lives in db/init.sql and is shared with the FastAPI
service. Django only reads and writes rows.
"""
# Core
import uuid
from django.db import models


class BusinessItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=2)       # AT | DE | US | UA
    status = models.CharField(max_length=20)       # active | inactive | pending
    revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    owner = models.CharField(max_length=255)
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "business_items"
