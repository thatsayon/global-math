from django.db import models
import uuid

class UserDailyStats(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    user = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    date = models.DateField()
    points_earned = models.IntegerField(default=0)

    class Meta:
        unique_together = ("user", "date")

