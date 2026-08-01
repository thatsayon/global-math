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

