import requests

LIBRETRANSLATE_URL = "http://localhost:8080/translate"  # Or public API

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

