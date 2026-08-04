import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from asgiref.sync import async_to_sync
from messaging.socket import sio

def test():
    try:
        async_to_sync(sio.emit)("test", {"hello": "world"})
        print("Success!")
    except Exception as e:
        print("Error:", e)

test()
