"""
General test helper functions and utilities.

This module contains common test utilities that can be used across
different test modules for mocking, assertions, and test data generation.
"""

import time
import uuid
from typing import Any, Callable, Dict, Optional
from unittest.mock import Mock

import pytest

from pyevolutionapi import EvolutionClient
from pyevolutionapi.models.instance import Instance, InstanceResponse, InstanceStatus
from pyevolutionapi.models.message import MessageResponse


def generate_test_instance_name(prefix: str = "test") -> str:
    """
    Generate a unique test instance name.

    Args:
        prefix: Prefix for the instance name

    Returns:
        Unique instance name with timestamp
    """
    timestamp = int(time.time())
    unique_id = str(uuid.uuid4())[:8]
    return f"{prefix}-{timestamp}-{unique_id}"


def mock_evolution_response(
    status: str = "success", data: Optional[Dict[str, Any]] = None, status_code: int = 200
) -> Mock:
    """
    Create a mock HTTP response for Evolution API.

    Args:
        status: Response status
        data: Response data
        status_code: HTTP status code

    Returns:
        Mock response object
    """
    response = Mock()
    response.status_code = status_code
    response.is_success = status_code < 400

    response_data = {"status": status}
    if data:
        response_data.update(data)

    response.json.return_value = response_data
    response.text = str(response_data)

    return response


def mock_instance_data(
    instance_name: str = "test-instance",
    status: InstanceStatus = InstanceStatus.CONNECTING,
    instance_id: str = None,
    **extra_fields,
) -> Dict[str, Any]:
    """
    Create mock instance data.

    Args:
        instance_name: Name of the instance
        status: Instance status
        instance_id: Instance ID
        **extra_fields: Additional fields

    Returns:
        Dictionary with instance data
    """
    data = {
        "instanceName": instance_name,
        "instanceId": instance_id or f"id_{instance_name}",
        "status": status.value if isinstance(status, InstanceStatus) else status,
        "integration": "WHATSAPP-BAILEYS",
        **extra_fields,
    }

    return data


def mock_instance_response(
    instance_name: str = "test-instance",
    status: str = "success",
    instance_status: InstanceStatus = InstanceStatus.CONNECTING,
    include_qr: bool = False,
    **extra_fields,
) -> Dict[str, Any]:
    """
    Create mock instance creation response.

    Args:
        instance_name: Name of the instance
        status: Response status
        instance_status: Instance status
        include_qr: Whether to include QR code data
        **extra_fields: Additional fields

    Returns:
        Dictionary with response data
    """
    response = {
        "status": status,
        "instance": mock_instance_data(instance_name=instance_name, status=instance_status),
        "hash": f"hash_{instance_name}",
        **extra_fields,
    }

    if include_qr:
        response["qrcode"] = {
            "base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMgAAADI...",
            "count": 0,
            "url": "https://web.whatsapp.com/qr/123456",
        }

    return response


def assert_evolution_response(
    response: Any,
    expected_status: Optional[str] = None,
    should_have_instance: bool = False,
    should_have_qr: bool = False,
):
    """
    Assert Evolution API response structure.

    Args:
        response: Response object to validate
        expected_status: Expected status value
        should_have_instance: Whether response should have instance
        should_have_qr: Whether response should have QR code
    """
    # Basic response validation
    assert response is not None, "Response should not be None"

    if hasattr(response, "status") and expected_status:
        assert response.status == expected_status

    if should_have_instance:
        assert hasattr(response, "instance"), "Response should have instance"
        assert response.instance is not None, "Instance should not be None"

        if hasattr(response.instance, "status"):
            assert response.instance.status in [
                InstanceStatus.CREATED,
                InstanceStatus.CONNECTING,
                InstanceStatus.CONNECTED,
                InstanceStatus.DISCONNECTED,
            ], f"Invalid instance status: {response.instance.status}"

    if should_have_qr:
        qr_found = False

        # Check different QR field variations
        if hasattr(response, "qr_code_base64") and response.qr_code_base64:
            qr_found = True
        elif hasattr(response, "qrcode") and response.qrcode:
            qr_found = True
        elif hasattr(response, "qr") and response.qr:
            qr_found = True

        assert qr_found, "Response should contain QR code data"


def wait_for_condition(
    condition_func: Callable[[], bool],
    timeout: float = 30.0,
    interval: float = 1.0,
    error_message: str = "Condition not met within timeout",
) -> bool:
    """
    Wait for a condition to become true.

    Args:
        condition_func: Function that returns True when condition is met
        timeout: Maximum time to wait in seconds
        interval: Check interval in seconds
        error_message: Error message if timeout

    Returns:
        True if condition met, False if timeout

    Raises:
        TimeoutError: If condition not met within timeout
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            if condition_func():
                return True
        except Exception:
            pass  # Ignore exceptions in condition function

        time.sleep(interval)

    raise TimeoutError(error_message)


def cleanup_test_instances(client: EvolutionClient, pattern: str = "test-"):
    """
    Clean up test instances that match a pattern.

    Args:
        client: Evolution client
        pattern: Pattern to match in instance names
    """
    try:
        instances = client.instance.fetch_instances()

        for instance in instances:
            instance_name = instance.name or instance.id
            if instance_name and pattern in instance_name:
                try:
                    client.instance.delete(instance_name)
                except Exception:
                    pass  # Ignore cleanup errors

    except Exception:
        pass  # Ignore if fetch fails


class MockEvolutionClient:
    """
    Mock Evolution API client for testing.
    """

    def __init__(self):
        self.instance = Mock()
        self.messages = Mock()
        self.chat = Mock()
        self.group = Mock()
        self.profile = Mock()
        self.webhook = Mock()

        # Setup default responses
        self._setup_default_responses()

    def _setup_default_responses(self):
        """Setup default mock responses."""

        # Instance operations
        self.instance.create.return_value = InstanceResponse(
            status="success",
            instance=Instance(
                instance_name="test-instance",
                instance_id="test-id",
                status=InstanceStatus.CONNECTING,
            ),
            hash="test-hash",
        )

        self.instance.fetch_instances.return_value = [
            Instance(
                id="test-id",
                name="test-instance",
                status=InstanceStatus.CONNECTED,
                integration="WHATSAPP-BAILEYS",
            )
        ]

        self.instance.connection_state.return_value = {
            "state": "open",
            "instance": {"instanceName": "test-instance", "state": "open"},
        }

        # Message operations
        self.messages.send_text.return_value = MessageResponse(
            status="success", message_id="msg_123"
        )


class TestDataFactory:
    """
    Factory for creating test data objects.
    """

    @staticmethod
    def create_instance(
        name: str = None, status: InstanceStatus = InstanceStatus.CONNECTING, **kwargs
    ) -> Instance:
        """Create a test Instance object."""
        return Instance(
            id=kwargs.get("id", f"id_{name or 'test'}"),
            name=name or "test-instance",
            instance_id=kwargs.get("instance_id", f"inst_{name or 'test'}"),
            status=status,
            integration=kwargs.get("integration", "WHATSAPP-BAILEYS"),
            **{k: v for k, v in kwargs.items() if k not in ["id", "instance_id", "integration"]},
        )

    @staticmethod
    def create_instance_response(
        status: str = "success",
        instance_name: str = "test-instance",
        instance_status: InstanceStatus = InstanceStatus.CONNECTING,
        include_qr: bool = False,
        **kwargs,
    ) -> InstanceResponse:
        """Create a test InstanceResponse object."""

        response_data = {
            "status": status,
            "instance": TestDataFactory.create_instance(name=instance_name, status=instance_status),
            "hash": f"hash_{instance_name}",
            **kwargs,
        }

        if include_qr:
            response_data["qrcode"] = {"base64": "data:image/png;base64,mock_qr_data", "count": 0}

        return InstanceResponse(**response_data)

    @staticmethod
    def create_message_response(
        status: str = "success", message_id: str = None, **kwargs
    ) -> MessageResponse:
        """Create a test MessageResponse object."""
        return MessageResponse(
            status=status, message_id=message_id or f"msg_{int(time.time())}", **kwargs
        )


# Pytest fixtures that can be used across tests
@pytest.fixture
def mock_client():
    """Fixture providing a mock Evolution client."""
    return MockEvolutionClient()


@pytest.fixture
def test_instance_name():
    """Fixture providing a unique test instance name."""
    return generate_test_instance_name()


@pytest.fixture
def test_data_factory():
    """Fixture providing the test data factory."""
    return TestDataFactory


# Markers for better test categorization
def slow_test(func):
    """Mark test as slow (for tests that take longer)."""
    return pytest.mark.slow(func)


def integration_test(func):
    """Mark test as integration test."""
    return pytest.mark.integration(func)


def requires_api(func):
    """Mark test as requiring real API."""
    return pytest.mark.requires_api(func)


def requires_whatsapp(func):
    """Mark test as requiring WhatsApp connection."""
    return pytest.mark.requires_whatsapp(func)
