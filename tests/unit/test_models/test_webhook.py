"""
Unit tests for webhook models.
"""

from pyevolutionapi.models.webhook import RabbitMQConfig, SQSConfig, WebhookConfig, WebSocketConfig


class TestWebhookModels:
    """Test webhook model validation and functionality."""

    def test_webhook_config_creation(self):
        """Test creating webhook configuration."""
        config = WebhookConfig(
            url="https://api.example.com/webhook",
            events=["MESSAGE_RECEIVED", "MESSAGE_SENT"],
            webhook_by_events=True,
        )

        assert config.url == "https://api.example.com/webhook"
        assert "MESSAGE_RECEIVED" in config.events
        assert "MESSAGE_SENT" in config.events
        assert config.webhook_by_events is True

    def test_webhook_config_with_headers(self):
        """Test webhook config with custom headers."""
        config = WebhookConfig(
            url="https://api.example.com/webhook",
            events=["MESSAGE_RECEIVED"],
            webhook_base64=True,
            headers={"Authorization": "Bearer token123", "Content-Type": "application/json"},
        )

        assert config.webhook_base64 is True
        assert config.headers["Authorization"] == "Bearer token123"
        assert config.headers["Content-Type"] == "application/json"

    def test_websocket_config_creation(self):
        """Test WebSocket configuration."""
        config = WebSocketConfig(enabled=True, events=["MESSAGE_RECEIVED"])

        assert config.enabled is True
        assert "MESSAGE_RECEIVED" in config.events

    def test_rabbitmq_config_creation(self):
        """Test RabbitMQ configuration."""
        config = RabbitMQConfig(
            enabled=True,
            events=["MESSAGE_RECEIVED", "MESSAGE_SENT"],
            uri="amqp://user:pass@rabbitmq:5672",
            exchange_name="evolution_exchange",
        )

        assert config.enabled is True
        assert config.uri == "amqp://user:pass@rabbitmq:5672"
        assert config.exchange_name == "evolution_exchange"

    def test_sqs_config_creation(self):
        """Test AWS SQS configuration."""
        config = SQSConfig(
            enabled=True,
            access_key_id="AKIAIOSFODNN7EXAMPLE",
            secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
            queue_url="https://sqs.us-east-1.amazonaws.com/123456789/MyQueue",
            region="us-east-1",
        )

        assert config.enabled is True
        assert config.access_key_id == "AKIAIOSFODNN7EXAMPLE"
        assert config.region == "us-east-1"
        assert "MyQueue" in config.queue_url
