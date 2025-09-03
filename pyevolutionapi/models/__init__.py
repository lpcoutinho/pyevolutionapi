"""
Data models for Evolution API resources.
"""

from .base import BaseModel, BaseResponse
from .instance import Instance, InstanceCreate, InstanceResponse, ConnectionState
from .message import (
    TextMessage,
    MediaMessage,
    LocationMessage,
    ContactMessage,
    ReactionMessage,
    AudioMessage,
    StickerMessage,
    MessageResponse,
    MessageStatus,
)
from .group import (
    Group,
    GroupCreate,
    GroupUpdate,
    GroupParticipant,
    GroupResponse,
)
from .chat import (
    Chat,
    Contact,
    ProfilePicture,
    PrivacySettings,
)
from .webhook import (
    WebhookConfig,
    WebhookEvent,
    WebhookResponse,
)

__all__ = [
    # Base
    "BaseModel",
    "BaseResponse",
    # Instance
    "Instance",
    "InstanceCreate",
    "InstanceResponse",
    "ConnectionState",
    # Messages
    "TextMessage",
    "MediaMessage",
    "LocationMessage",
    "ContactMessage",
    "ReactionMessage",
    "AudioMessage",
    "StickerMessage",
    "MessageResponse",
    "MessageStatus",
    # Groups
    "Group",
    "GroupCreate",
    "GroupUpdate",
    "GroupParticipant",
    "GroupResponse",
    # Chat
    "Chat",
    "Contact",
    "ProfilePicture",
    "PrivacySettings",
    # Webhook
    "WebhookConfig",
    "WebhookEvent",
    "WebhookResponse",
]