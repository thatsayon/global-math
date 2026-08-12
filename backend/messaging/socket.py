from asgiref.sync import sync_to_async

from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from django.db import transaction
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.utils import timezone

from .models import (
    Conversation,
    ConversationParticipant,
    Message,
    BlockUser,
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

    is_blocked = BlockUser.objects.filter(
        Q(blocker=sender, blocked_user=receiver) | 
        Q(blocker=receiver, blocked_user=sender)
    ).exists()

    if is_blocked:
        return {"error": "Cannot send message. User is blocked."}

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

    try:
        from core.utils import send_push_notification
        sender_name = f"{sender.first_name} {sender.last_name}".strip() or sender.username
        send_push_notification(
            user=receiver,
            title=f"New message from {sender_name}",
            body=content,
            data={
                "type": "message",
                "sender_id": str(sender.id),
                "message_id": str(message.id)
            }
        )
    except Exception as e:
        logger.error(f"Error sending push notification for message: {e}")

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
        return {"status": "error", "message": "Invalid payload"}

    sender_id = connected_users.get(sid)
    if not sender_id:
        return {"status": "error", "message": "Unauthorized"}

    message_text = data.get("message")
    to_user = data.get("to_user")

    if not message_text or not to_user:
        return {"status": "error", "message": "Message and target user are required"}

    # Save message in DB
    saved_message = await save_message_to_db(sender_id, to_user, message_text)

    if isinstance(saved_message, dict) and "error" in saved_message:
        return {"status": "error", "message": saved_message["error"]}

    # Get sender details
    sender_name = f"{saved_message.sender.first_name} {saved_message.sender.last_name}".strip() or saved_message.sender.username
    sender_avatar = saved_message.sender.profile_pic.url if saved_message.sender.profile_pic else None

    # Prepare payload
    payload = {
        "id": str(saved_message.id),
        "conversation": str(saved_message.conversation.id),
        "sender": sender_id,
        "sender_name": sender_name,
        "sender_avatar": sender_avatar,
        "receiver": to_user,
        "message": saved_message.content,
        "timestamp": saved_message.created_at.isoformat()
    }

    # Deliver if online
    recipient_sid = user_sid_map.get(to_user)
    if recipient_sid:
        await sio.emit("receive_message", payload, to=recipient_sid)

    print(f"📨 Message saved and sent from {sender_id} to {to_user}")
    
    # Return acknowledgment
    return {"status": "ok", "data": payload}

@sync_to_async
def delete_message_from_db(message_id: str, sender_id: str):
    try:
        sender = User.objects.get(id=sender_id)
        msg = Message.objects.get(id=message_id, sender=sender)
        msg.delete()
        return True
    except (Message.DoesNotExist, User.DoesNotExist):
        return False

@sio.event
async def delete_message(sid, data):
    if not isinstance(data, dict):
        return {"status": "error", "message": "Invalid payload"}

    sender_id = connected_users.get(sid)
    if not sender_id:
        return {"status": "error", "message": "Unauthorized"}

    message_id = data.get("message_id")
    to_user = data.get("to_user")

    if not message_id or not to_user:
        return {"status": "error", "message": "message_id and to_user are required"}

    deleted = await delete_message_from_db(message_id, sender_id)
    if not deleted:
        return {"status": "error", "message": "Message not found or unauthorized"}

    recipient_sid = user_sid_map.get(to_user)
    if recipient_sid:
        await sio.emit("message_deleted", {"message_id": message_id}, to=recipient_sid)

    print(f"🗑️ Message {message_id} deleted by {sender_id}")
    return {"status": "ok", "message_id": message_id}

@sync_to_async
def edit_message_in_db(message_id: str, sender_id: str, new_content: str):
    try:
        sender = User.objects.get(id=sender_id)
        msg = Message.objects.get(id=message_id, sender=sender)
        msg.content = new_content
        msg.is_edited = True
        msg.save(update_fields=['content', 'is_edited'])
        return True
    except (Message.DoesNotExist, User.DoesNotExist):
        return False

@sio.event
async def edit_message(sid, data):
    if not isinstance(data, dict):
        return {"status": "error", "message": "Invalid payload"}

    sender_id = connected_users.get(sid)
    if not sender_id:
        return {"status": "error", "message": "Unauthorized"}

    message_id = data.get("message_id")
    to_user = data.get("to_user")
    new_content = data.get("new_content")

    if not message_id or not to_user or not new_content:
        return {"status": "error", "message": "message_id, to_user, and new_content are required"}

    edited = await edit_message_in_db(message_id, sender_id, new_content)
    if not edited:
        return {"status": "error", "message": "Message not found or unauthorized"}

    recipient_sid = user_sid_map.get(to_user)
    if recipient_sid:
        await sio.emit("message_edited", {"message_id": message_id, "new_content": new_content}, to=recipient_sid)

    print(f"✏️ Message {message_id} edited by {sender_id}")
    return {"status": "ok", "message_id": message_id, "new_content": new_content}

@sio.event
async def update_token(sid, data):
    if not isinstance(data, dict):
        return
    token = data.get("token")
    if token:
        token = token.replace("Bearer ", "")
        user = await get_user_from_token(token)
        if user:
            user_id = str(user.id)
            connected_users[sid] = user_id
            user_sid_map[user_id] = sid
            print(f"🔄 Token updated for SID={sid}, USER={user.username}")

@sio.event
async def disconnect(sid):
    user_id = connected_users.pop(sid, None)

    if user_id and user_sid_map.get(user_id) == sid:
        user_sid_map.pop(user_id, None)

    print(f"❌ Disconnected: SID={sid}, USER={user_id}")

