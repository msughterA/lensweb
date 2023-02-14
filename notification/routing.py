from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/notifications/(?P<userId>[0-9]+)/", consumers.NotifiacationConsumer)
]
