import requests

LIBRETRANSLATE_URL = "https://host.mathos.cloud/translate"  # Or public API

def translate_text(text, target_lang, source_lang='en'):
    if not text or target_lang == source_lang:
        return text

    payload = {
        "q": text,
        "source": source_lang,
        "target": target_lang,
        "format": "text"
    }

    try:
        # Send as form data instead of JSON
        response = requests.post(LIBRETRANSLATE_URL, data=payload, timeout=10)
        response.raise_for_status()
        return response.json().get('translatedText', text)
    except Exception as e:
        print("Translation error:", e)
        return text

from django.core.cache import cache

def get_translated_level_name(level_name, target_lang):
    if not target_lang or target_lang == 'en':
        return level_name
    
    cache_key = f"translated_level_{level_name}_{target_lang}".replace(" ", "_")
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    translated = translate_text(level_name, target_lang, 'en')
    cache.set(cache_key, translated, timeout=86400) # cache for 1 day
    return translated

def send_push_notification(user, title, body, data=None):
    """
    Sends a push notification to all devices registered by the user.
    Uses rate-limiting via Django's cache to prevent spamming notifications.
    """
    try:
        if not data:
            data = {}

        notif_type = data.get("type", "generic")

        # Rate-limiting logic
        # For likes/comments/replies: limit 1 push per user per post/action per 30 mins
        # For messages: limit 1 push per receiver per sender per 5 mins
        if notif_type in ["like", "comment", "reply"]:
            post_id = data.get("post_id", "unknown_post")
            cache_key = f"push_ratelimit_{user.id}_{notif_type}_{post_id}"
            timeout = 1800  # 30 minutes
        elif notif_type == "message":
            sender_id = data.get("sender_id", "unknown_sender")
            cache_key = f"push_ratelimit_{user.id}_{notif_type}_{sender_id}"
            timeout = 300  # 5 minutes
        else:
            cache_key = None
            timeout = 0

        # If cache key exists, skip sending push (debounce)
        if cache_key:
            if cache.get(cache_key):
                print(f"Push skipped due to rate limit: {cache_key}")
                return
            cache.set(cache_key, True, timeout=timeout)

        # Send push
        from post.models import FCMDevice
        from firebase_admin import messaging

        devices = FCMDevice.objects.filter(user=user)
        tokens = [device.token for device in devices]
        
        if not tokens:
            return

        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data,
            tokens=tokens,
        )
        response = messaging.send_multicast(message)
        print(f"Successfully sent {response.success_count} messages")
    except Exception as e:
        print("Failed to send push notification:", e)

