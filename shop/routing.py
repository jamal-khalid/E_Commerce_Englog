from django.urls import re_path
from .consumers import OrderNotificationConsumer
from .middleware import JWTAuthMiddlewareStack

websocket_urlpatterns = [
    re_path(r'ws/notifications/$', JWTAuthMiddlewareStack(OrderNotificationConsumer.as_asgi())),
]

# websocket_urlpatterns = [
#     re_path(r'ws/notifications/$', OrderNotificationConsumer.as_asgi()),
# ]

