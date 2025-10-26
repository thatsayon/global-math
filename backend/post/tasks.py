from celery import shared_task
from .models import PostModel
import requests

@shared_task
def verify_post_ai(post_id):
    try:
        post = PostModel.objects.get(id=post_id)
    except PostModel.DoesNotExist:
        return f"Post {post_id} does not exist."

    data = {
        "text": post.text,
        # if your AI needs image URL, send post.image.url
        "image_url": post.image.url if post.image else None
    }

    # Call your AI service (replace with actual API)
    response = requests.post("https://your-ai-service.com/verify", json=data)

    if response.status_code == 200:
        result = response.json()
        post.is_verified = result.get("is_verified", False)
        post.save()
        return f"Post {post_id} verification completed."
    else:
        return f"AI verification failed for post {post_id}."

