from django.contrib import admin
from .models import PostModel, PostTranslation, CommentModel

admin.site.register(PostModel)
admin.site.register(PostTranslation)
admin.site.register(CommentModel)
