"""
Unit tests for instance resource.
"""

from unittest.mock import Mock, patch

import pytest

from pyevolutionapi.models.instance import Instance, InstanceResponse, InstanceStatus
from pyevolutionapi.resources.instance import InstanceResource


class TestInstanceResource:
    """Test instance resource functionality."""

    @pytest.fixture
    def mock_client(self):
        """Mock client for testing."""
        client = Mock()
        client.request = Mock()
        return client

    @pytest.fixture
    def instance_resource(self, mock_client):
        """Instance resource with mocked client."""
        return InstanceResource(mock_client)

    def test_create_instance_success(self, instance_resource, mock_client):
        """Test successful instance creation."""
        # Mock response
        mock_response = {
            "status": "success",
            "instance": {
                "instanceName": "test-instance",
                "instanceId": "abc123",
                "status": "connecting",
                "state": "connecting",
            },
            "hash": "xyz789",
        }

        mock_client.request.return_value = mock_response

        # Test
        result = instance_resource.create(instance_name="test-instance", qrcode=True)

        # Assertions
        assert isinstance(result, InstanceResponse)
        assert result.status == "success"
        assert result.instance.instance_name == "test-instance"
        assert result.instance.status == InstanceStatus.CONNECTING
        assert result.hash == "xyz789"

        # Verify API call
        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        assert call_args[0][0] == "POST"  # Method
        assert "/instance/create" in call_args[0][1]  # URL

    def test_fetch_instances(self, instance_resource, mock_client):
        """Test fetching instances list."""
        # Mock response - list format
        mock_response = [
            {
                "id": "instance1",
                "instanceName": "test1",
                "status": "connected",
                "integration": "WHATSAPP-BAILEYS",
            },
            {
                "id": "instance2",
                "instanceName": "test2",
                "status": "connecting",
                "integration": "WHATSAPP-BAILEYS",
            },
        ]

        mock_client.request.return_value = mock_response

        # Test
        result = instance_resource.fetch_instances()

        # Assertions
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(inst, Instance) for inst in result)
        assert result[0].id == "instance1"
        assert result[1].id == "instance2"

    def test_delete_instance(self, instance_resource, mock_client):
        """Test instance deletion."""
        mock_response = {"status": "success", "message": "Instance deleted"}
        mock_client.request.return_value = mock_response

        # Test
        result = instance_resource.delete("test-instance")

        # Assertions
        assert result["status"] == "success"

        # Verify API call
        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        assert call_args[0][0] == "DELETE"  # Method
        assert "test-instance" in call_args[0][1]  # Instance name in URL

    def test_connection_state(self, instance_resource, mock_client):
        """Test getting connection state."""
        mock_response = {"instance": {"instanceName": "test-instance", "state": "open"}}

        mock_client.request.return_value = mock_response

        # Test
        result = instance_resource.connection_state("test-instance")

        # Assertions
        assert result["instance"]["state"] == "open"

    @patch("time.sleep")  # Mock sleep to speed up tests
    def test_connect_instance(self, mock_sleep, instance_resource, mock_client):
        """Test connecting instance."""
        mock_response = {
            "status": "success",
            "qrcode": {"base64": "data:image/png;base64,abc123", "count": 0},
        }

        mock_client.request.return_value = mock_response

        # Test
        result = instance_resource.connect("test-instance")

        # Assertions
        assert isinstance(result, InstanceResponse)
        assert result.qrcode["count"] == 0
        assert "base64" in result.qrcode
