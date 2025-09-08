"""
Unit tests for message models.
"""

from pyevolutionapi.models.message import MediaMessage, MessageResponse, MessageType, TextMessage


class TestMessageModels:
    """Test message model validation and functionality."""

    def test_text_message_creation(self):
        """Test creating a text message."""
        message = TextMessage(number="5511999999999", text="Hello World!")

        assert message.number == "5511999999999"
        assert message.text == "Hello World!"
        assert message.delay is None

    def test_text_message_with_delay(self):
        """Test text message with delay."""
        message = TextMessage(number="5511999999999", text="Delayed message", delay=5000)

        assert message.delay == 5000

    def test_media_message_creation(self):
        """Test creating a media message."""
        message = MediaMessage(
            number="5511999999999",
            mediatype=MessageType.IMAGE,
            media="https://example.com/image.jpg",
        )

        assert message.number == "5511999999999"
        assert message.mediatype == MessageType.IMAGE
        assert str(message.media) == "https://example.com/image.jpg"

    def test_message_response_parsing(self):
        """Test message response parsing."""
        response_data = {
            "status": "success",
            "key": {
                "remoteJid": "5511999999999@s.whatsapp.net",
                "fromMe": True,
                "id": "3EB0F4A1F841F02958FB74",
            },
            "message": {
                "key": {
                    "remoteJid": "5511999999999@s.whatsapp.net",
                    "fromMe": True,
                    "id": "3EB0F4A1F841F02958FB74",
                },
                "message": {"conversation": "Hello World!"},
            },
        }

        response = MessageResponse(**response_data)

        assert response.status == "success"
        assert response.key is not None
        assert response.key.remote_jid == "5511999999999@s.whatsapp.net"
        assert response.key.from_me is True
        assert response.message is not None
        assert response.message.message["conversation"] == "Hello World!"
