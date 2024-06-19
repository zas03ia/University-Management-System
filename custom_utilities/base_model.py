from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser


class BaseModel(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 

    class Meta:
        abstract = True
    
    
    def save(self, *args, **kwargs):
        for field in self._meta.fields:
            if isinstance(field, models.CharField) and getattr(self, field.name):
                setattr(self, field.name, getattr(self, field.name).capitalize())

        super().save(*args, **kwargs)
