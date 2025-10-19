from django.urls import re_path
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from .consumers import OrderNotificationConsumer

websocket_urlpatterns = [
    re_path(r'ws/notifications/$', AuthMiddlewareStack(OrderNotificationConsumer.as_asgi())),
]
