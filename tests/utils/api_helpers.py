"""
API-specific test helpers for Evolution API integration.

This module contains helpers specifically for testing with real Evolution API,
including connection monitoring, QR code handling, and API state management.
"""

import base64
import time
from typing import Any, Callable, Dict, List, Optional

from pyevolutionapi import EvolutionClient
from pyevolutionapi.models.instance import ConnectionState, InstanceStatus


class IntegrationHelper:
    """
    Helper class for Evolution API integration tests.

    Provides utilities for managing real API interactions, monitoring
    connection states, and handling test lifecycle.
    """

    def __init__(self, client: EvolutionClient):
        self.client = client
        self.created_instances: List[str] = []

    def wait_for_status(
        self,
        client: EvolutionClient,
        instance_name: str,
        expected_status: InstanceStatus,
        timeout: float = 30.0,
        interval: float = 2.0,
    ) -> bool:
        """
        Wait for instance to reach expected status.

        Args:
            client: Evolution client
            instance_name: Name of instance to monitor
            expected_status: Status to wait for
            timeout: Maximum wait time in seconds
            interval: Check interval in seconds

        Returns:
            True if status reached, False if timeout
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                instances = client.instance.fetch_instances()

                for instance in instances:
                    if instance.name == instance_name or instance.id == instance_name:
                        if instance.status == expected_status:
                            return True
                        break

            except Exception:
                pass  # Ignore temporary API errors

            time.sleep(interval)

        return False

    def wait_for_connection(
        self, instance_name: str, timeout: float = 60.0, interval: float = 3.0
    ) -> bool:
        """
        Wait for WhatsApp connection to be established.

        Args:
            instance_name: Name of instance
            timeout: Maximum wait time in seconds
            interval: Check interval in seconds

        Returns:
            True if connected, False if timeout
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                # Check via connection_state
                status = self.client.instance.connection_state(instance_name)

                if isinstance(status, dict):
                    state = status.get("state", "").lower()
                    if state == "open":
                        return True

                # Also check via fetch_instances
                instances = self.client.instance.fetch_instances()
                for instance in instances:
                    if instance.name == instance_name or instance.id == instance_name:

                        if hasattr(instance, "state") and instance.state == ConnectionState.OPEN:
                            return True

                        if (
                            hasattr(instance, "status")
                            and instance.status == InstanceStatus.CONNECTED
                        ):
                            return True
                        break

            except Exception:
                pass  # Ignore API errors

            time.sleep(interval)

        return False

    def create_test_instance(
        self, instance_name: str = None, qrcode: bool = True, auto_cleanup: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Create a test instance with proper cleanup tracking.

        Args:
            instance_name: Name for the instance
            qrcode: Whether to request QR code
            auto_cleanup: Whether to track for automatic cleanup

        Returns:
            Creation response or None if failed
        """
        if not instance_name:
            instance_name = f"test-{int(time.time())}"

        try:
            # Try to delete if exists
            try:
                self.client.instance.delete(instance_name)
                time.sleep(1)
            except Exception:
                pass

            # Create new instance
            response = self.client.instance.create(instance_name=instance_name, qrcode=qrcode)

            if auto_cleanup:
                self.created_instances.append(instance_name)

            return {"instance_name": instance_name, "response": response, "success": True}

        except Exception as e:
            return {"instance_name": instance_name, "error": str(e), "success": False}

    def cleanup_instances(self, instance_names: List[str] = None):
        """
        Clean up test instances.

        Args:
            instance_names: Specific instances to clean up, or None for all tracked
        """
        names_to_clean = instance_names or self.created_instances.copy()

        for name in names_to_clean:
            try:
                self.client.instance.delete(name)
                if name in self.created_instances:
                    self.created_instances.remove(name)
            except Exception:
                pass  # Ignore cleanup errors

    def get_instance_by_name(self, instance_name: str) -> Optional[Dict[str, Any]]:
        """
        Find instance by name in the instances list.

        Args:
            instance_name: Name to search for

        Returns:
            Instance data or None if not found
        """
        try:
            instances = self.client.instance.fetch_instances()

            for instance in instances:
                if (
                    instance.name == instance_name
                    or instance.id == instance_name
                    or (hasattr(instance, "instance_id") and instance.instance_id == instance_name)
                ):
                    return {"instance": instance, "found": True}

            return {"found": False}

        except Exception as e:
            return {"error": str(e), "found": False}

    def is_api_available(self) -> bool:
        """
        Check if Evolution API is available and responsive.

        Returns:
            True if API is available
        """
        try:
            self.client.instance.fetch_instances()
            return True
        except Exception:
            return False

    def get_api_info(self) -> Dict[str, Any]:
        """
        Get API information and status.

        Returns:
            Dictionary with API information
        """
        info = {"available": False, "instances_count": 0, "version": "unknown"}

        try:
            # Check if API responds
            instances = self.client.instance.fetch_instances()
            info["available"] = True
            info["instances_count"] = len(instances) if instances else 0

            # Try to get version/health info
            try:
                health = self.client.health_check()
                if isinstance(health, dict):
                    info.update(health)
                else:
                    info["health"] = health
            except Exception:
                pass

        except Exception as e:
            info["error"] = str(e)

        return info


class QRDisplayHelper:
    """
    Helper for handling QR codes in tests.

    Provides utilities for extracting, validating, and displaying
    QR codes from Evolution API responses.
    """

    @staticmethod
    def extract_qr_from_response(response: Any) -> Optional[str]:
        """
        Extract QR code data from API response.

        Args:
            response: API response object

        Returns:
            Base64 QR code data or None
        """
        # Check different possible QR fields
        qr_fields = ["qr_code_base64", "qrCodeBase64", "base64"]

        for field in qr_fields:
            if hasattr(response, field):
                value = getattr(response, field)
                if value:
                    return value

        # Check qrcode dict
        if hasattr(response, "qrcode") and response.qrcode:
            qr_data = response.qrcode

            if isinstance(qr_data, dict):
                for field in qr_fields:
                    if field in qr_data and qr_data[field]:
                        return qr_data[field]

                # Also try 'base64' key specifically
                if "base64" in qr_data:
                    return qr_data["base64"]

        return None

    @staticmethod
    def validate_qr_base64(qr_data: str) -> Dict[str, Any]:
        """
        Validate QR code base64 data.

        Args:
            qr_data: Base64 QR code data

        Returns:
            Validation result dictionary
        """
        result = {"valid": False, "format": "unknown", "size": 0, "has_prefix": False}

        if not qr_data:
            result["error"] = "Empty QR data"
            return result

        try:
            # Check for data URL prefix
            if qr_data.startswith("data:image/"):
                result["has_prefix"] = True
                result["format"] = qr_data.split(";")[0].split("/")[-1]

                # Extract base64 part
                base64_part = qr_data.split(",", 1)[-1]
            else:
                base64_part = qr_data
                result["format"] = "raw_base64"

            # Try to decode
            decoded = base64.b64decode(base64_part)
            result["size"] = len(decoded)
            result["valid"] = True

            # Basic image format detection
            if decoded.startswith(b"\x89PNG"):
                result["image_format"] = "PNG"
            elif decoded.startswith(b"\xff\xd8\xff"):
                result["image_format"] = "JPEG"
            else:
                result["image_format"] = "unknown"

        except Exception as e:
            result["error"] = str(e)

        return result

    @staticmethod
    def save_qr_to_file(qr_data: str, filename: str) -> bool:
        """
        Save QR code to file for manual inspection.

        Args:
            qr_data: Base64 QR code data
            filename: Output filename

        Returns:
            True if saved successfully
        """
        try:
            # Extract base64 part
            if qr_data.startswith("data:image/"):
                base64_part = qr_data.split(",", 1)[-1]
            else:
                base64_part = qr_data

            # Decode and save
            decoded = base64.b64decode(base64_part)

            with open(filename, "wb") as f:
                f.write(decoded)

            return True

        except Exception:
            return False

    @staticmethod
    def display_qr_info(qr_data: str) -> str:
        """
        Get displayable information about QR code.

        Args:
            qr_data: Base64 QR code data

        Returns:
            Formatted information string
        """
        validation = QRDisplayHelper.validate_qr_base64(qr_data)

        info_lines = []
        info_lines.append("📱 QR Code Information:")
        info_lines.append(f"   Valid: {'✅' if validation['valid'] else '❌'}")

        if validation["valid"]:
            info_lines.append(f"   Format: {validation['format']}")
            info_lines.append(f"   Size: {validation['size']:,} bytes")

            if "image_format" in validation:
                info_lines.append(f"   Image: {validation['image_format']}")

            info_lines.append(f"   Has prefix: {'Yes' if validation['has_prefix'] else 'No'}")

            # Show truncated data
            display_data = qr_data[:100] + "..." if len(qr_data) > 100 else qr_data
            info_lines.append(f"   Data: {display_data}")
        else:
            info_lines.append(f"   Error: {validation.get('error', 'Unknown')}")

        return "\n".join(info_lines)


class RateLimitHelper:
    """
    Helper for managing API rate limits during tests.
    """

    def __init__(self, default_delay: float = 1.0):
        self.default_delay = default_delay
        self.last_request_time = 0.0

    def wait_if_needed(self, min_delay: float = None):
        """
        Wait if necessary to respect rate limits.

        Args:
            min_delay: Minimum delay between requests
        """
        delay = min_delay or self.default_delay
        elapsed = time.time() - self.last_request_time

        if elapsed < delay:
            time.sleep(delay - elapsed)

        self.last_request_time = time.time()

    def with_rate_limit(self, func: Callable, *args, **kwargs):
        """
        Execute function with automatic rate limiting.

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result
        """
        self.wait_if_needed()
        return func(*args, **kwargs)


class TestInstanceManager:
    """
    Manager for test instances with automatic cleanup and lifecycle management.
    """

    def __init__(self, client: EvolutionClient, prefix: str = "test"):
        self.client = client
        self.prefix = prefix
        self.active_instances: Dict[str, Dict[str, Any]] = {}

    def create_instance(self, name: str = None, qrcode: bool = True, **kwargs) -> Dict[str, Any]:
        """
        Create and track a test instance.

        Args:
            name: Instance name (auto-generated if None)
            qrcode: Whether to request QR code
            **kwargs: Additional creation parameters

        Returns:
            Creation result dictionary
        """
        if not name:
            name = f"{self.prefix}-{int(time.time())}"

        try:
            # Clean up if exists
            try:
                self.client.instance.delete(name)
                time.sleep(1)
            except Exception:
                pass

            # Create instance
            response = self.client.instance.create(instance_name=name, qrcode=qrcode, **kwargs)

            # Track instance
            self.active_instances[name] = {
                "name": name,
                "created_at": time.time(),
                "response": response,
                "status": "created",
            }

            return {"name": name, "response": response, "success": True}

        except Exception as e:
            return {"name": name, "error": str(e), "success": False}

    def get_instance_status(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get current status of managed instance.

        Args:
            name: Instance name

        Returns:
            Status dictionary or None
        """
        if name not in self.active_instances:
            return None

        try:
            # Get latest status from API
            instances = self.client.instance.fetch_instances()

            for instance in instances:
                if instance.name == name or instance.id == name:
                    self.active_instances[name]["current_status"] = instance.status
                    self.active_instances[name]["current_state"] = getattr(instance, "state", None)
                    break

            return self.active_instances[name]

        except Exception as e:
            self.active_instances[name]["error"] = str(e)
            return self.active_instances[name]

    def cleanup_all(self):
        """Clean up all managed instances."""
        for name in list(self.active_instances.keys()):
            try:
                self.client.instance.delete(name)
                del self.active_instances[name]
            except Exception:
                pass  # Ignore cleanup errors

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.cleanup_all()
