# stream/routing.py
from django.urls import re_path
from . import consumers,hello

websocket_urlpatterns = [
    re_path(r'ws/stream/(?P<slug>[^/]+)/$', consumers.StreamConsumer.as_asgi()),
    re_path(r'ws/hellostream/', hello.SimpleConsumer.as_asgi()),
]