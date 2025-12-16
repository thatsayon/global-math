from django.contrib import admin
from .models import (
    RecentActivity,
    MathLevels,
    SupportMessage,
    DailyChallenge,
    ChallengeQuestion,
)

admin.site.register(RecentActivity)
admin.site.register(MathLevels)
admin.site.register(SupportMessage)
admin.site.register(DailyChallenge)
admin.site.register(ChallengeQuestion)
