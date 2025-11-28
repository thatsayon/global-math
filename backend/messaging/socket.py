from asgiref.sync import sync_to_async

from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.utils import timezone

from .models import (
    Conversation,
    ConversationParticipant,
    Message,
)

import socketio
import logging
import json
import jwt

logger = logging.getLogger(__name__)

User = get_user_model()

connected_users = {}  # sid -> user_id
user_sid_map = {}     # user_id -> sid


sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*"
)

@sync_to_async
def get_user_from_token(token: str):
    try:
        token = token.replace("Bearer ", "")
        untoken = UntypedToken(token)  
        user_id = untoken["user_id"]
        return User.objects.get(id=user_id)
    except (InvalidToken, TokenError) as e:
        logger.error(f"Token decode error: {e}")
        return None


@sync_to_async
def save_message_to_db(sender_id: str, receiver_id: str, content: str):
    sender = User.objects.get(id=sender_id)
    receiver = User.objects.get(id=receiver_id)

    # Find or create 1-on-1 conversation
    conversation = Conversation.objects.filter(
        is_group=False,
        participants__user=sender
    ).filter(
        participants__user=receiver
    ).first()

    if not conversation:
        conversation = Conversation.objects.create(is_group=False)
        ConversationParticipant.objects.bulk_create([
            ConversationParticipant(user=sender, conversation=conversation),
            ConversationParticipant(user=receiver, conversation=conversation)
        ])

    # Save message
    message = Message.objects.create(
        conversation=conversation,
        sender=sender,
        content=content,
        created_at=timezone.now()
    )

    return message

@sio.event
async def connect(sid, environ, auth):
    token = auth.get("token") if auth else None
    print(token)
    user = None

    if token:
        token = token.replace("Bearer ", "")
        user = await get_user_from_token(token)

    if not user:
        print(f"❌ Unauthorized connection attempt: {sid}")
        return False

    user_id = str(user.id)

    connected_users[sid] = user_id
    user_sid_map[user_id] = sid

    await sio.save_session(sid, {"user_id": user_id})
    await sio.enter_room(sid, user_id)

    print(f"🔥 Connected: SID={sid}, USER={user.username}")


@sio.event
async def send_message(sid, data):
    if not isinstance(data, dict):
        await sio.emit("error", {"error": "Invalid payload"}, to=sid)
        return

    sender_id = connected_users.get(sid)
    if not sender_id:
        await sio.emit("error", {"error": "Unauthorized"}, to=sid)
        return

    message_text = data.get("message")
    to_user = data.get("to_user")

    if not message_text or not to_user:
        await sio.emit("error", {"error": "Message and target user are required"}, to=sid)
        return

    # Save message in DB
    saved_message = await save_message_to_db(sender_id, to_user, message_text)

    # Prepare payload
    payload = {
        "id": str(saved_message.id),
        "conversation": str(saved_message.conversation.id),
        "sender": sender_id,
        "receiver": to_user,
        "message": saved_message.content,
        "timestamp": saved_message.created_at.isoformat()
    }

    # Deliver if online
    recipient_sid = user_sid_map.get(to_user)
    if recipient_sid:
        await sio.emit("receive_message", payload, to=recipient_sid)

    # Confirm to sender
    await sio.emit("message_sent", payload, to=sid)

    print(f"📨 Message saved and sent from {sender_id} to {to_user}")

@sio.event
async def receive_message(sid, data):
    if not isinstance(data, dict):
        await sio.emit("error", {"error": "Invalid payload format"}, to=sid)
        return

    sender_id = connected_users.get(sid)
    if not sender_id:
        await sio.emit("error", {"error": "Unauthorized"}, to=sid)
        return

    message = data.get("message")
    to_user = data.get("to_user")

    if not message:
        await sio.emit("error", {"error": "Message content is required"}, to=sid)
        return

    if not to_user:
        await sio.emit("error", {"error": "Target user is required"}, to=sid)
        return

    # Save to DB (placeholder)
    saved_message = await save_message_to_db(sender_id, to_user, message)

    # Find recipient session
    recipient_sid = user_sid_map.get(to_user)

    # Prepare payload
    payload = {
        "id": saved_message.id,
        "sender": sender_id,
        "receiver": to_user,
        "message": message,
        "timestamp": saved_message.timestamp.isoformat()
    }

    # Deliver message
    if recipient_sid:
        await sio.emit("receive_message", payload, to=recipient_sid)

    # Acknowledge to sender
    await sio.emit("message_sent", payload, to=sid)

    print(f"Message from {sender_id} to {to_user}: {message}")

@sio.event
async def disconnect(sid):
    user_id = connected_users.pop(sid, None)

    if user_id and user_sid_map.get(user_id) == sid:
        user_sid_map.pop(user_id, None)

    print(f"❌ Disconnected: SID={sid}, USER={user_id}")

