import uuid

from django.db import models


class BaseModel(models.Model):
    id = models.UUIDField(verbose_name="id", primary_key=True, default=uuid.uuid4, editable=False)
    is_active = models.BooleanField(verbose_name="is_active", default=True)
    created_at = models.DateTimeField(verbose_name="created_at", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="updated_at", auto_now=True)

    class Meta:
        abstract = True
