from django.contrib import admin
from .models import (
    RecentActivity,
    MathLevels,
    SupportMessage,
    DailyChallenge,
    ChallengeQuestion,
    ActivityLog,
)
from account.models import Badge

admin.site.register(RecentActivity)
admin.site.register(MathLevels)
admin.site.register(SupportMessage)
admin.site.register(DailyChallenge)
admin.site.register(ChallengeQuestion)
admin.site.register(ActivityLog)
admin.site.register(Badge)
