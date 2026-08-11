import requests
import re

LIBRETRANSLATE_URL = "https://host.mathos.cloud/translate"

def translate_text(text, target_lang, source_lang='en'):
    if not text or target_lang == source_lang:
        return text

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
        response = requests.post(LIBRETRANSLATE_URL, data=payload, timeout=10)
        response.raise_for_status()
        translated_text = response.json().get('translatedText', text_to_translate)
        
        for i, block in enumerate(math_blocks):
            placeholder_pattern = re.compile(r'mthblk\s*' + str(i), re.IGNORECASE)
            translated_text = placeholder_pattern.sub(lambda m: block, translated_text)
            
        return translated_text
    except Exception as e:
        return f"ERROR: {e}"

langs = ['es', 'fr', 'de', 'zh', 'ja', 'he']
for l in langs:
    res = translate_text("1. Calculate the sum: \\(5.67 + 3.8\\)", l)
    print(f"[{l}] {res}")
