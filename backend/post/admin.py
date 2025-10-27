from django.contrib import admin
from .models import PostModel, PostTranslation

admin.site.register(PostModel)
admin.site.register(PostTranslation)
