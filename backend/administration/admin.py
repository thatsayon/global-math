from django.contrib import admin
from .models import (
    RecentActivity,
    MathLevels,
    SupportMessage,
)

admin.site.register(RecentActivity)
admin.site.register(MathLevels)
admin.site.register(SupportMessage)
