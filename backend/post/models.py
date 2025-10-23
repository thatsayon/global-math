from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class PostModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        editable=False,
        unique=True
    )
    user = models.ForeignKey()

