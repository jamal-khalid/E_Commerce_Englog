import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'e_commerce.settings')
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import shop.routing

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'e_commerce.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(
        shop.routing.websocket_urlpatterns
    ),
})
