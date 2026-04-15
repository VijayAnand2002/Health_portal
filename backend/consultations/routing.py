"""
WebSocket URL routing for consultations
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/consultation/(?P<room_name>\w+)/$', consumers.ConsultationConsumer.as_asgi()),
]
