from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Conversation, Message

UserAccount = get_user_model()

class ConversationSerializer(serializers.ModelSerializer):
    conversation_name = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    last_message_sender = serializers.SerializerMethodField()
    last_message_is_me = serializers.SerializerMethodField()
    last_message_time = serializers.SerializerMethodField()
    other_user_avatar = serializers.SerializerMethodField()
    unread_count = serializers.IntegerField()

    class Meta:
        model = Conversation
        fields = [
            'id',
            'conversation_name',
            'other_user_avatar',
            'last_message',
            'last_message_sender',
            'last_message_is_me',
            'last_message_time',
            'unread_count'
        ]

    def get_conversation_name(self, obj):
        user = self.context['request'].user
        other_participant = obj.participants.exclude(user=user).select_related('user').first()
        if other_participant:
            other_user = other_participant.user
            full_name = f"{other_user.first_name} {other_user.last_name}".strip()
            return full_name or other_user.username
        return "Unknown"

    def get_other_user_avatar(self, obj):
        user = self.context['request'].user
        other_participant = obj.participants.exclude(user=user).select_related('user').first()
        if other_participant:
            avatar = getattr(other_participant.user, "profile_pic", None)
            if avatar and hasattr(avatar, 'url'):
                return avatar.url
        return None

    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        return last_msg.content if last_msg else ""

    def get_last_message_sender(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        if not last_msg:
            return ""
        user = self.context['request'].user
        return "Me" if last_msg.sender == user else f"{last_msg.sender.first_name} {last_msg.sender.last_name}".strip() or last_msg.sender.username

    def get_last_message_is_me(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        if not last_msg:
            return None
        return last_msg.sender == self.context['request'].user

    def get_last_message_time(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        return last_msg.created_at if last_msg else None

