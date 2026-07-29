from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone 
from datetime import timedelta

import logging

import os
from email.mime.image import MIMEImage

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_password_reset_email_task(self, user_email, full_name, otp):
    try:
        subject = "Password Reset Request"
        body = render_to_string(
            "password_reset_email.html",
            {"otp": otp, "full_name": full_name}
        )

        email = EmailMultiAlternatives(subject, "", to=[user_email])
        email.attach_alternative(body, "text/html")
        email.mixed_subtype = 'related'

        # Attach the logo inline
        logo_path = "/Users/thatsayon/Codes/mathos/app/assets/icons/app_title_icon_light.png"
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                logo_image = MIMEImage(f.read())
                logo_image.add_header('Content-ID', '<logo>')
                logo_image.add_header('Content-Disposition', 'inline', filename='app_title_icon_light.png')
                email.attach(logo_image)

        email.send()

        logger.info(f"Password reset OTP email sent successfully to {user_email}")

    except Exception as exc:
        logger.error(f"Failed to send password reset OTP email to {user_email}: {exc}")
        raise self.retry(exc=exc, countdown=10)  # retry after 10s

