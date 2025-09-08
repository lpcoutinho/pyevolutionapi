"""
Unit tests for webhook models.
"""

from pyevolutionapi.models.webhook import (
    RabbitmqConfig,
    SqsConfig,
    WebhookConfig,
    WebhookEvent,
    WebsocketConfig,
)


class TestWebhookModels:
    """Test webhook model validation and functionality."""

    def test_webhook_config_creation(self):
        """Test creating webhook configuration."""
        config = WebhookConfig(
            url="https://api.example.com/webhook",
            events=[WebhookEvent.MESSAGES_UPSERT, WebhookEvent.SEND_MESSAGE],
            webhook_by_events=True,
        )

        assert str(config.url) == "https://api.example.com/webhook"
        assert WebhookEvent.MESSAGES_UPSERT in config.events
        assert WebhookEvent.SEND_MESSAGE in config.events
        assert config.webhook_by_events is True

    def test_webhook_config_with_headers(self):
        """Test webhook config with custom headers."""
        config = WebhookConfig(
            url="https://api.example.com/webhook",
            events=[WebhookEvent.MESSAGES_UPSERT],
            webhook_base64=True,
            headers={"Authorization": "Bearer token123", "Content-Type": "application/json"},
        )

        assert config.webhook_base64 is True
        assert config.headers["Authorization"] == "Bearer token123"
        assert config.headers["Content-Type"] == "application/json"

    def test_websocket_config_creation(self):
        """Test WebSocket configuration."""
        config = WebsocketConfig(enabled=True, events=[WebhookEvent.MESSAGES_UPSERT])

        assert config.enabled is True
        assert WebhookEvent.MESSAGES_UPSERT in config.events

    def test_rabbitmq_config_creation(self):
        """Test RabbitMQ configuration."""
        config = RabbitmqConfig(
            enabled=True,
            events=[WebhookEvent.MESSAGES_UPSERT, WebhookEvent.SEND_MESSAGE],
        )

        assert config.enabled is True

    def test_sqs_config_creation(self):
        """Test AWS SQS configuration."""
        config = SqsConfig(
            enabled=True,
            events=[WebhookEvent.MESSAGES_UPSERT, WebhookEvent.SEND_MESSAGE],
        )

        assert config.enabled is True
