import os
import io
import sys
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY environment variable is not set.")
    print("Please create a .env file with your API key:")
    print("GEMINI_API_KEY=your_api_key_here")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)

# Base models
text_model = genai.GenerativeModel('gemini-2.5-pro')

# Deterministic config for classification
classification_generation_config = genai.types.GenerationConfig(
    temperature=0.1,
    max_output_tokens=500,
)

classification_model = genai.GenerativeModel(
    'gemini-2.5-pro',
    generation_config=classification_generation_config
)

def process_math_problem(prompt: str, image_data=None) -> str:
    """Process a math problem using Gemini API.
    image_data can be PIL.Image.Image or bytes. When bytes are given, convert to PIL.Image.
    Returns model text.
    """
    try:
        if image_data:
            if isinstance(image_data, (bytes, bytearray)):
                img = Image.open(io.BytesIO(image_data))
            elif isinstance(image_data, Image.Image):
                img = image_data
            else:
                img = image_data  # attempt to pass-through (SDK may handle)
            vision_model = genai.GenerativeModel('gemini-2.5-pro')
            response = vision_model.generate_content([prompt, img])
        else:
            response = text_model.generate_content(prompt)
        # Prefer response.text
        return getattr(response, "text", "").strip() or str(response)
    except Exception as e:
        # re-raise; views will map to HTTP responses
        raise

def extract_text_from_genai_response(res) -> str:
    """Robust extraction for google.generativeai responses."""
    if isinstance(res, str):
        return res
    try:
        txt = getattr(res, "text", None)
        if isinstance(txt, str) and txt.strip():
            return txt
    except Exception:
        pass

    result = getattr(res, "result", None)
    if result is not None:
        parts = getattr(result, "parts", None)
        if parts:
            out = []
            for p in parts:
                t = getattr(p, "text", None)
                if t:
                    out.append(t)
            if out:
                return "".join(out)
        candidates = getattr(result, "candidates", None)
        if candidates:
            for cand in candidates:
                content = getattr(cand, "content", None)
                if content:
                    parts = getattr(content, "parts", None)
                    if parts:
                        out = [getattr(p, "text", "") for p in parts if getattr(p, "text", None)]
                        if any(out):
                            return "".join(out)
                if getattr(cand, "text", None):
                    return cand.text

    candidates = getattr(res, "candidates", None) or getattr(res, "outputs", None) or getattr(res, "choices", None)
    if candidates:
        for cand in candidates:
            content = getattr(cand, "content", None)
            if content:
                parts = getattr(content, "parts", None)
                if parts:
                    out = [getattr(p, "text", "") for p in parts if getattr(p, "text", None)]
                    if any(out):
                        return "".join(out)
            if getattr(cand, "text", None):
                return cand.text
            if getattr(cand, "output_text", None):
                return cand.output_text

    parts = getattr(res, "parts", None)
    if parts:
        out = [getattr(p, "text", "") for p in parts if getattr(p, "text", None)]
        if any(out):
            return "".join(out)

    try:
        import logging
        logging.info("Unrecognized GenAI response shape; repr(response)=%s", repr(res))
    except Exception:
        pass
    return str(res)
