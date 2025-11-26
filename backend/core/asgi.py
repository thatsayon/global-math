from django.core.asgi import get_asgi_application

import os
import django
import socketio


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

django.setup()

from messaging.socket import sio

django_asgi_app = get_asgi_application()
application = socketio.ASGIApp(sio, django_asgi_app)
