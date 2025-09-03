"""
Pytest configuration and fixtures.
"""

from unittest.mock import Mock

import httpx
import pytest

from pyevolutionapi import EvolutionClient


@pytest.fixture
def mock_api_key():
    """Mock API key for testing."""
    return "test-api-key-12345"


@pytest.fixture
def mock_base_url():
    """Mock base URL for testing."""
    return "http://localhost:8080"


@pytest.fixture
def client(mock_base_url, mock_api_key):
    """Create a test client."""
    return EvolutionClient(
        base_url=mock_base_url, api_key=mock_api_key, default_instance="test-instance"
    )


@pytest.fixture
def mock_response():
    """Create a mock HTTP response."""
    response = Mock(spec=httpx.Response)
    response.status_code = 200
    response.is_success = True
    response.json.return_value = {"status": "success"}
    response.text = '{"status": "success"}'
    response.headers = {}
    return response


@pytest.fixture
def mock_instance_response():
    """Mock instance creation response."""
    return {
        "status": "success",
        "instance": {"instanceName": "test-instance", "status": "created", "state": "close"},
        "hash": "test-hash-123",
        "qrcode": {
            "base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
            "code": "test-qr-code",
        },
    }


@pytest.fixture
def mock_message_response():
    """Mock message send response."""
    return {
        "status": "success",
        "key": {
            "remoteJid": "5511999999999@s.whatsapp.net",
            "fromMe": True,
            "id": "3EB0F4A1F841F02958FB74",
        },
        "message": {"conversation": "Hello World!"},
    }


# Environment setup for testing
@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    """Set up environment variables for testing."""
    monkeypatch.setenv("EVOLUTION_DEBUG", "false")
    monkeypatch.setenv("EVOLUTION_LOG_LEVEL", "WARNING")
