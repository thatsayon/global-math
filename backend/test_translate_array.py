import requests

LIBRETRANSLATE_URL = "https://host.mathos.cloud/translate"

payload = {
    "q": ["Hello world", "Calculate the sum"],
    "source": "en",
    "target": "ja",
    "format": "text"
}

try:
    # Use json= instead of data= for array of strings
    response = requests.post(LIBRETRANSLATE_URL, json=payload, timeout=10)
    response.raise_for_status()
    print(response.json())
except Exception as e:
    print(f"ERROR: {e}")
