"""
ASGI config for lensweb project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import fileshare.routing
import notification.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lensweb.settings")

application = get_asgi_application()

# application = get_asgi_application()
application = ProtocolTypeRouter(
    {
        # "http": AsgiHandler(),
        "websocket": AuthMiddlewareStack(
            URLRouter(notification.routing.websocket_urlpatterns)
        ),
    }
)
