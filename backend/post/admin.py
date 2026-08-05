from django.contrib import admin
from .models import PostModel, PostTranslation, CommentModel, FCMDevice, Notification


@admin.register(FCMDevice)
class FCMDeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'short_token', 'created_at')
    search_fields = ('user__username', 'user__email', 'token')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    def short_token(self, obj):
        return obj.token[:30] + '...' if len(obj.token) > 30 else obj.token
    short_token.short_description = 'Token (preview)'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'type', 'is_read', 'created_at')
    search_fields = ('user__username', 'user__email', 'title', 'description')
    list_filter = ('type', 'is_read', 'created_at')
    readonly_fields = ('created_at',)
    ordering = ('-created_at')

admin.site.register(PostModel)
admin.site.register(PostTranslation)
admin.site.register(CommentModel)
