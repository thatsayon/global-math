from django.contrib import admin
from .models import StudentProfile, UserAccount, StudentProgress, EarnedBadge, Badge


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'icon')
    list_filter = ('category',)
    search_fields = ('name', 'code')


admin.site.register(StudentProfile)
admin.site.register(UserAccount)
admin.site.register(StudentProgress)
admin.site.register(EarnedBadge)
