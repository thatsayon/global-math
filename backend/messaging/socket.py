from asgiref.sync import sync_to_async

from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

import socketio
import logging
import json
import jwt

logger = logging.getLogger(__name__)

User = get_user_model()


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

@sio.event
async def connect(sid, environ, auth):
    token = auth.get("token") if auth else None
    user = None
    print(token)

    if token:
        token = token.replace("Bearer ", "")
        user = await get_user_from_token(token)
        print(user)

    if not user:
        print(f"❌ Unauthorized connection attempt: {sid}")
        return False  # Disconnect client

    # Join a room named after user ID
    await sio.save_session(sid, {"user_id": str(user.id)})
    await sio.enter_room(sid, str(user.id))

    print(f"✅ Connected: {sid} (User ID: {user.id})")
    logger.info(f"Client connected: {sid}, User: {user.username}")

@sio.event
async def send_message(sid, data):
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from {sid}: {data}")
            return


    message = data.get("message")
    print(message)

    if not message:
        await sio.emit("error", {"error": "message is required"}, to=sio)
        return

    payload = {
        "sid": sid,
        "message": message
    }

    await sio.emit("receive_message", payload)
    print(message)

@sio.event
async def receive_message(sid, data):
    print(f"Received message: {data}")

@sio.event
async def disconnect(sid):
    print(f"❌ Client disconnected: {sid}")
    logger.info(f"Client disconnected: {sid}")
