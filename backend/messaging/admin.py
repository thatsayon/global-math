from django.contrib import admin
from messaging.ai_chat.models import ChatSession
from .models import (
    Conversation,
    ConversationParticipant,
    Message
)

admin.site.register(Conversation)
admin.site.register(ConversationParticipant)
admin.site.register(Message)
admin.site.register(ChatSession)

