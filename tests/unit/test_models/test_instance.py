"""
Unit tests for instance models validation fixes.

Tests to ensure that:
1. InstanceStatus enum accepts "connecting" status
2. qrcode field accepts Dict with mixed types (not just strings)
3. Real API responses are parsed correctly
"""

from pyevolutionapi.models.instance import (
    ConnectionState,
    Instance,
    InstanceResponse,
    InstanceStatus,
)


class TestInstanceStatus:
    """Test InstanceStatus enum."""

    def test_connecting_status_is_valid(self):
        """Test that CONNECTING status exists and is valid."""
        # Check that CONNECTING exists in the enum
        assert hasattr(InstanceStatus, "CONNECTING")
        assert InstanceStatus.CONNECTING == "connecting"

        # Test that we can use it
        status = InstanceStatus.CONNECTING
        assert status.value == "connecting"

    def test_all_statuses(self):
        """Test all instance statuses."""
        expected_statuses = {
            "CREATED": "created",
            "CONNECTING": "connecting",
            "CONNECTED": "connected",
            "DISCONNECTED": "disconnected",
            "DELETED": "deleted",
        }

        for attr_name, value in expected_statuses.items():
            assert hasattr(InstanceStatus, attr_name)
            assert getattr(InstanceStatus, attr_name).value == value


class TestInstanceModel:
    """Test Instance model with real API responses."""

    def test_instance_with_connecting_status(self):
        """Test parsing instance with 'connecting' status."""
        # Simulate real API response
        data = {
            "instanceName": "test-bot",
            "instanceId": "123456",
            "status": "connecting",  # This should now work
            "state": "connecting",
            "integration": "WHATSAPP-BAILEYS",
        }

        # This should not raise ValidationError
        instance = Instance(**data)
        assert instance.instance_name == "test-bot"
        assert instance.status == InstanceStatus.CONNECTING
        assert instance.state == ConnectionState.CONNECTING

    def test_instance_with_qrcode_count(self):
        """Test parsing instance with qrcode containing count as integer."""
        # Simulate real API response with count as integer
        data = {
            "instanceName": "test-bot",
            "qrcode": {
                "count": 0,  # Integer, not string
                "base64": "data:image/png;base64,iVBORw0KG...",
                "code": "2@xyz...",
            },
        }

        # This should not raise ValidationError
        instance = Instance(**data)
        assert instance.instance_name == "test-bot"
        assert instance.qrcode is not None
        assert instance.qrcode["count"] == 0
        assert isinstance(instance.qrcode["count"], int)

    def test_instance_with_empty_qrcode(self):
        """Test parsing instance with empty qrcode."""
        data = {"instanceName": "test-bot", "qrcode": None}

        instance = Instance(**data)
        assert instance.qrcode is None
        assert instance.qr_code_base64 is None


class TestInstanceResponse:
    """Test InstanceResponse model with real API responses."""

    def test_response_with_connecting_instance(self):
        """Test response containing instance with connecting status."""
        data = {
            "status": "success",
            "instance": {
                "instanceName": "new-bot",
                "status": "connecting",
                "state": "connecting",
            },
            "hash": "abc123",
            "qrcode": {"count": 0, "base64": "data:image/png;base64,..."},  # Integer field
        }

        # This should not raise ValidationError
        response = InstanceResponse(**data)
        assert response.status == "success"
        assert response.instance.status == InstanceStatus.CONNECTING
        assert response.qrcode["count"] == 0

    def test_response_qrcode_with_mixed_types(self):
        """Test response with qrcode containing mixed types."""
        data = {
            "status": "success",
            "qrcode": {
                "count": 5,  # Integer
                "base64": "data:image/png;base64,abc123",  # String
                "code": "2@DEF456",  # String
                "expires": 1234567890,  # Integer timestamp
                "valid": True,  # Boolean
            },
        }

        # This should not raise ValidationError with Dict[str, Any]
        response = InstanceResponse(**data)
        assert response.qrcode["count"] == 5
        assert response.qrcode["valid"] is True
        assert isinstance(response.qrcode["expires"], int)

    def test_response_list_instances(self):
        """Test response with list of instances."""
        data = {
            "status": "success",
            "instances": [
                {
                    "instanceName": "bot1",
                    "status": "connected",
                },
                {
                    "instanceName": "bot2",
                    "status": "connecting",  # Should work now
                },
                {
                    "instanceName": "bot3",
                    "status": "disconnected",
                },
            ],
        }

        response = InstanceResponse(**data)
        assert len(response.instances) == 3
        assert response.instances[1].status == InstanceStatus.CONNECTING


class TestRealAPIScenarios:
    """Test real-world API response scenarios."""

    def test_create_instance_response(self):
        """Test typical response when creating a new instance."""
        # Real response from Evolution API when creating instance
        api_response = {
            "status": "success",
            "instance": {
                "instanceName": "my-whatsapp",
                "instanceId": "d4e5f6",
                "status": "connecting",  # Instance is connecting, waiting for QR
                "state": "connecting",
                "integration": "WHATSAPP-BAILEYS",
                "createdAt": "2024-01-01T10:00:00Z",
                "updatedAt": "2024-01-01T10:00:00Z",
            },
            "hash": "xyz789",
            "qrcode": {
                "count": 0,  # No QR codes scanned yet
                "base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgA...",
                "code": "2@MLRiHFBqFtFp2L9VHzZqDMLRiHFBqFtFp2L9VHzZq...",
            },
        }

        # Should parse without errors
        response = InstanceResponse(**api_response)

        # Validate the response
        assert response.status == "success"
        assert response.instance.status == InstanceStatus.CONNECTING
        assert response.instance.state == ConnectionState.CONNECTING
        assert response.qrcode["count"] == 0
        assert response.qr_code_base64.startswith("data:image/png;base64,")

    def test_connection_state_response(self):
        """Test response from connection_state endpoint."""
        # Real response from /instance/connectionState/{instance}
        api_response = {
            "status": "success",
            "instance": {"instanceName": "my-bot", "state": "connecting"},  # Waiting for QR scan
        }

        response = InstanceResponse(**api_response)
        assert response.instance.state == ConnectionState.CONNECTING
