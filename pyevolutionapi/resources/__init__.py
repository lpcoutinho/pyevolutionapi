"""
API resources for Evolution API.
"""

from .instance import InstanceResource
from .message import MessageResource
from .chat import ChatResource
from .group import GroupResource
from .profile import ProfileResource
from .webhook import WebhookResource

__all__ = [
    "InstanceResource",
    "MessageResource",
    "ChatResource",
    "GroupResource",
    "ProfileResource",
    "WebhookResource",
]