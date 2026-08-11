import requests

LIBRETRANSLATE_URL = "https://host.mathos.cloud/translate"  # Or public API

import re

def translate_text(text, target_lang, source_lang='en'):
    if not text or target_lang == source_lang:
        return text

    # Extract math blocks to prevent them from being translated or broken
    math_pattern = re.compile(r'(\\\(.*?\\\)|\\\[.*?\\\]|\$\$.*?\$\$)', re.DOTALL)
    math_blocks = []
    
    def replacer(match):
        math_blocks.append(match.group(0))
        return f" MTHBLK{len(math_blocks)-1} "
        
    text_to_translate = math_pattern.sub(replacer, text)

    payload = {
        "q": text_to_translate,
        "source": source_lang,
        "target": target_lang,
        "format": "text"
    }

    try:
        # Send as form data instead of JSON
        response = requests.post(LIBRETRANSLATE_URL, data=payload, timeout=10)
        response.raise_for_status()
        translated_text = response.json().get('translatedText', text_to_translate)
        
        # Restore math blocks
        for i, block in enumerate(math_blocks):
            placeholder_pattern = re.compile(r'mthblk\s*' + str(i), re.IGNORECASE)
            translated_text = placeholder_pattern.sub(lambda m: block, translated_text)
            
        return translated_text
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
        # Messages: no rate limit — every message must push
        if notif_type in ["like", "comment", "reply"]:
            post_id = data.get("post_id", "unknown_post")
            cache_key = f"push_ratelimit_{user.id}_{notif_type}_{post_id}"
            timeout = 1800  # 30 minutes
        else:
            # No rate limit for messages and other types
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
        # send_multicast was removed in firebase-admin v6+; use send_each_for_multicast
        response = messaging.send_each_for_multicast(message)
        print(f"Successfully sent {response.success_count} messages")

        # Clean up any invalid/expired tokens from the database
        if response.failure_count > 0:
            invalid_tokens = []
            for idx, resp in enumerate(response.responses):
                if not resp.success:
                    error_code = resp.exception.code if resp.exception else None
                    if error_code in ('registration-token-not-registered', 'invalid-registration-token'):
                        invalid_tokens.append(tokens[idx])
            if invalid_tokens:
                FCMDevice.objects.filter(token__in=invalid_tokens).delete()
                print(f"Removed {len(invalid_tokens)} invalid FCM tokens")

    except Exception as e:
        print("Failed to send push notification:", e)


def translate_texts_batch(texts, target_lang, source_lang='en'):
    if target_lang == source_lang:
        return texts

    math_pattern = re.compile(r'(\\\(.*?\\\)|\\\[.*?\\\]|\$\$.*?\$\$)', re.DOTALL)
    
    texts_to_translate = []
    all_math_blocks = []
    
    for text in texts:
        if not text:
            texts_to_translate.append(text)
            all_math_blocks.append([])
            continue
            
        math_blocks = []
        def replacer(match):
            math_blocks.append(match.group(0))
            return f" MTHBLK{len(math_blocks)-1} "
            
        text_to_translate = math_pattern.sub(replacer, text)
        texts_to_translate.append(text_to_translate)
        all_math_blocks.append(math_blocks)

    payload = {
        "q": texts_to_translate,
        "source": source_lang,
        "target": target_lang,
        "format": "text"
    }

    try:
        response = requests.post(LIBRETRANSLATE_URL, json=payload, timeout=20)
        response.raise_for_status()
        translated_texts = response.json().get('translatedText', texts_to_translate)
        
        if not isinstance(translated_texts, list):
            return texts
            
        final_translated = []
        for i, translated_text in enumerate(translated_texts):
            if not translated_text:
                final_translated.append(translated_text)
                continue
                
            math_blocks = all_math_blocks[i]
            for j, block in enumerate(math_blocks):
                placeholder_pattern = re.compile(r'mthblk\s*' + str(j), re.IGNORECASE)
                translated_text = placeholder_pattern.sub(lambda m: block, translated_text)
            final_translated.append(translated_text)
            
        return final_translated
    except Exception as e:
        print("Batch translation error:", e)
        return texts
