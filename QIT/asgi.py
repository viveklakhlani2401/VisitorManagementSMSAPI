"""
ASGI config for QIT project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QIT.settings')

# application = get_asgi_application()

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from django.urls import path
from QIT.consumer import SocketConsumer
from django.urls import re_path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QIT.settings')

# websocket_urlpatterns = [
#     path('ws/path/', ChatConsumer.as_asgi()),
# ]
websocket_urlpatterns = [
   re_path(r'^ws/path/$',SocketConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
