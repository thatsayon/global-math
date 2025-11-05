from django.contrib import admin
from .models import (
    RecentActivity,
    MathLevels,
)

admin.site.register(RecentActivity)
admin.site.register(MathLevels)
