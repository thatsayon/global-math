from django.core.exceptions import ObjectDoesNotExist
from celery import shared_task
from nudenet import NudeDetector
import requests
import tempfile
import logging

from core.utils import translate_text
from .models import PostModel, PostTranslation

logger = logging.getLogger(__name__)

# Initialize detector once
detector = NudeDetector()

# Labels considered unsafe
UNSAFE_LABELS = [
    "FEMALE_BREAST_EXPOSED",
    "MALE_BREAST_EXPOSED",
    "FEMALE_GENITALIA_EXPOSED",
    "MALE_GENITALIA_EXPOSED",
    "ANUS_EXPOSED",
    "BUTTOCKS_EXPOSED",
]

# Threshold above which a detection counts as NSFW
NSFW_THRESHOLD = 0.3


@shared_task
def run_nudity_check(post_id):
    """
    Celery task to check if a post's image contains nudity.
    Deletes the post if NSFW content is detected.
    """
    try:
        post = PostModel.objects.get(id=post_id)

        if not post.image:
            # No image, mark as verified
            post.is_verified = True
            post.save(update_fields=["is_verified"])
            return {"status": "no_image", "post_id": post_id}

        # Download image to temp file
        image_url = post.image.url
        with tempfile.NamedTemporaryFile(suffix=".jpg") as tmp:
            r = requests.get(image_url, stream=True, timeout=10)
            r.raise_for_status()
            for chunk in r.iter_content(1024):
                tmp.write(chunk)
            tmp.flush()

            # Run detection
            detections = detector.detect(tmp.name)

            # Check if any unsafe label exceeds threshold
            is_nsfw = any(
                d["class"] in UNSAFE_LABELS and d["score"] >= NSFW_THRESHOLD
                for d in detections
            )

            if is_nsfw:
                post.delete()
                return {"status": "deleted", "post_id": post_id}
            else:
                post.is_verified = True
                post.save(update_fields=["is_verified"])
                return {"status": "safe", "post_id": post_id}

    except ObjectDoesNotExist:
        logger.warning(f"Post {post_id} does not exist.")
        return {"status": "not_found", "post_id": post_id}
    except requests.RequestException as e:
        logger.error(f"Failed to download image for post {post_id}: {str(e)}")
        return {"status": "download_error", "post_id": post_id, "error": str(e)}
    except Exception as e:
        logger.exception(f"Error processing post {post_id}: {str(e)}")
        return {"status": "error", "post_id": post_id, "error": str(e)}


@shared_task
def translate_post_task(post_id):
    post = PostModel.objects.get(id=post_id)
    source_lang = post.language or 'en'
    target_languages = ['en','es','fr','de','zh','ja','he']

    for lang in target_languages:
        if lang == source_lang:
            continue
        translated = translate_text(post.text, target_lang=lang, source_lang=source_lang)
        PostTranslation.objects.update_or_create(
            post=post,
            language=lang,
            defaults={'translated_text': translated}
        )

