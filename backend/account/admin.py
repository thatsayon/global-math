from django.contrib import admin
from .models import StudentProfile, UserAccount, StudentProgress, EarnedBadge

admin.site.register(StudentProfile)
admin.site.register(UserAccount)
admin.site.register(StudentProgress)
admin.site.register(EarnedBadge)
