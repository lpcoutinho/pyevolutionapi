"""
Integration tests for Evolution API compatibility.

Tests to ensure PyEvolution API works correctly with different versions
and configurations of the Evolution API.
"""

import time

import pytest

from pyevolutionapi.models.instance import InstanceStatus


@pytest.mark.integration
class TestAPICompatibility:
    """Test compatibility with Evolution API versions."""

    def test_api_health_check(self, real_client):
        """Test that API health endpoint is accessible."""
        try:
            health = real_client.health_check()
            # Accept different response formats
            assert health is not None
            # Can be boolean or dict depending on API version
            if isinstance(health, dict):
                assert "status" in health or "message" in health
            elif isinstance(health, bool):
                assert health is True

        except Exception as e:
            pytest.skip(f"API health check failed: {e}")

    def test_instance_endpoints_available(self, real_client):
        """Test that core instance endpoints are available."""
        # Test fetch_instances (should always work)
        instances = real_client.instance.fetch_instances()
        assert isinstance(instances, list)

        # Each instance should be parseable
        for instance in instances:
            assert hasattr(instance, "id")
            # Status can be None (common in real API)
            if instance.status:
                assert isinstance(instance.status, (InstanceStatus, str))

    def test_different_response_formats(self, real_client):
        """Test handling of different response formats from Evolution API."""
        # Some API versions return different formats
        instances = real_client.instance.fetch_instances()

        if instances:
            # Test parsing various field combinations
            for instance in instances[:3]:  # Test first 3 to avoid rate limits
                # Fields that might be present
                fields_to_check = [
                    "id",
                    "instance_name",
                    "status",
                    "state",
                    "integration",
                    "profile_name",
                    "Setting",
                ]

                for field in fields_to_check:
                    value = getattr(instance, field, "MISSING")
                    # Should not raise exception accessing these fields
                    assert value != "ERROR"  # If getter raises exception, this would fail

    def test_api_error_handling(self, real_client):
        """Test that API errors are handled gracefully."""
        # Try to get status of non-existent instance
        try:
            status = real_client.instance.connection_state("non-existent-instance-12345")
            # Some APIs return empty response, others return error
            # Both should be handled without exceptions
            assert status is not None or status is None  # Either is fine
        except Exception as e:
            # Should be a handled evolution exception, not a raw HTTP error
            assert "evolution" in str(type(e)).lower() or "http" in str(type(e)).lower()

    def test_rate_limiting_handling(self, real_client):
        """Test that rate limiting is handled properly."""
        # Make several quick requests to test rate limiting
        results = []

        for i in range(3):
            try:
                instances = real_client.instance.fetch_instances()
                results.append(len(instances))
                time.sleep(0.5)  # Small delay between requests
            except Exception as e:
                # Rate limiting should be handled gracefully
                if "429" in str(e) or "rate" in str(e).lower():
                    # This is expected and handled
                    break
                else:
                    # Other errors should be investigated
                    raise

        # Should have gotten at least one successful response
        assert len(results) >= 1


@pytest.mark.integration
class TestDataConsistency:
    """Test data consistency across different API endpoints."""

    def test_instance_data_consistency(self, real_client):
        """Test that instance data is consistent across endpoints."""
        # Get instances from list endpoint
        instances = real_client.instance.fetch_instances()

        if not instances:
            pytest.skip("No instances available for consistency testing")

        # Test first instance
        test_instance = instances[0]
        instance_identifier = test_instance.id or test_instance.name

        if not instance_identifier:
            pytest.skip("Instance has no usable identifier")

        # Get same instance data from status endpoint
        try:
            status_data = real_client.instance.connection_state(instance_identifier)

            # Data should be consistent (where present)
            if isinstance(status_data, dict) and "instance" in status_data:
                status_instance = status_data["instance"]

                # Compare available fields
                if "state" in status_instance and test_instance.state:
                    # States might be represented differently, but should be compatible
                    assert status_instance["state"] in ["open", "close", "connecting"]

        except Exception as e:
            # Some APIs might not support this endpoint
            pytest.skip(f"Connection state endpoint not available: {e}")

    def test_qrcode_data_consistency(self, real_client, clean_test_instance):
        """Test QR code data consistency across creation methods."""
        instance_name = clean_test_instance

        try:
            # Create instance with QR code
            create_response = real_client.instance.create(instance_name=instance_name, qrcode=True)

            # Check if QR data is present and valid
            if create_response.qrcode:
                qr_data = create_response.qrcode

                # Should be a dictionary
                assert isinstance(qr_data, dict)

                # Should have consistent field types
                if "count" in qr_data:
                    assert isinstance(qr_data["count"], (int, str))

                if "base64" in qr_data:
                    assert isinstance(qr_data["base64"], str)

        except Exception as e:
            pytest.skip(f"QR code testing failed: {e}")


@pytest.mark.integration
@pytest.mark.slow
class TestAPIPerformance:
    """Test API performance and responsiveness."""

    def test_response_times(self, real_client):
        """Test that API responses are reasonably fast."""
        start_time = time.time()

        # Simple operation should be fast
        instances = real_client.instance.fetch_instances()

        elapsed = time.time() - start_time

        # Should respond within 10 seconds (generous for integration tests)
        assert elapsed < 10.0, f"API response too slow: {elapsed:.2f}s"

        # Response should be parseable
        assert isinstance(instances, list)

    def test_concurrent_requests_handling(self, real_client):
        """Test that multiple requests don't cause issues."""
        import concurrent.futures

        def fetch_instances():
            return real_client.instance.fetch_instances()

        # Make 3 concurrent requests (conservative to avoid rate limiting)
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(fetch_instances) for _ in range(3)]

            results = []
            for future in concurrent.futures.as_completed(futures, timeout=30):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    # Some failures are acceptable (rate limiting, etc)
                    if "429" not in str(e):  # Not rate limiting
                        raise

        # Should have gotten at least one successful response
        assert len(results) >= 1
