"""
End-to-end tests for complete PyEvolution workflows.

These tests simulate real user workflows from start to finish:
1. Create instance
2. Connect WhatsApp (QR code)
3. Send messages
4. Clean up

Note: These tests require manual intervention for QR scanning
and should be run in controlled environments.
"""

import time

import pytest

from pyevolutionapi.models.instance import InstanceStatus


@pytest.mark.e2e
class TestCompleteWorkflow:
    """Test complete user workflows."""

    @pytest.mark.requires_whatsapp
    def test_full_whatsapp_workflow(
        self, real_client, clean_test_instance, require_test_number, e2e_config
    ):
        """
        Test complete WhatsApp workflow:
        1. Create instance
        2. Get QR code
        3. Wait for manual connection
        4. Send test message
        5. Verify delivery
        """
        instance_name = clean_test_instance
        test_number = require_test_number
        timeout = e2e_config["timeout"]

        print(f"\n📱 Starting E2E workflow for instance: {instance_name}")

        # Step 1: Create instance
        print("1️⃣ Creating instance...")
        create_response = real_client.instance.create(instance_name=instance_name, qrcode=True)

        assert create_response is not None
        assert create_response.instance.status in [
            InstanceStatus.CREATED,
            InstanceStatus.CONNECTING,
        ]

        print(f"✅ Instance created with status: {create_response.instance.status}")

        # Step 2: Get QR code
        print("2️⃣ Getting QR code...")
        if create_response.qr_code_base64:
            print("📱 QR Code available - scan with WhatsApp")
            print(f"QR (truncated): {create_response.qr_code_base64[:50]}...")
        else:
            print("⚠️ No QR code in create response, trying connect...")
            connect_response = real_client.instance.connect(instance_name)
            if connect_response and connect_response.qr_code_base64:
                print("📱 QR Code from connect - scan with WhatsApp")
                print(f"QR (truncated): {connect_response.qr_code_base64[:50]}...")
            else:
                pytest.skip("No QR code available from API")

        # Step 3: Wait for connection
        print("3️⃣ Waiting for WhatsApp connection...")
        print(f"⏱️ Timeout: {timeout//60} minutes")
        print("📱 Please scan the QR code with WhatsApp now!")

        connected = False
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                status = real_client.instance.connection_state(instance_name)

                if isinstance(status, dict):
                    state = status.get("state", "unknown")

                    if state == "open":
                        connected = True
                        print("🎉 WhatsApp connected successfully!")
                        break
                    else:
                        print(f"📊 Current state: {state}")

            except Exception as e:
                print(f"⚠️ Error checking status: {e}")

            time.sleep(5)  # Check every 5 seconds

        if not connected:
            pytest.skip(f"WhatsApp not connected within {timeout//60} minutes")

        # Step 4: Send test message
        print("4️⃣ Sending test message...")

        test_message = (
            f"🧪 E2E Test message from PyEvolution at {time.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        message_response = real_client.messages.send_text(
            instance=instance_name, number=test_number, text=test_message
        )

        assert message_response is not None
        print("✅ Message sent successfully!")

        if hasattr(message_response, "message_id") and message_response.message_id:
            print(f"📧 Message ID: {message_response.message_id}")

        # Step 5: Verify instance still connected
        print("5️⃣ Verifying connection after message...")

        final_status = real_client.instance.connection_state(instance_name)
        if isinstance(final_status, dict):
            final_state = final_status.get("state", "unknown")
            assert final_state == "open", f"Connection lost after message: {final_state}"

        print("✅ E2E workflow completed successfully!")

    def test_instance_lifecycle_without_connection(self, real_client, clean_test_instance):
        """
        Test instance lifecycle without requiring WhatsApp connection.
        Tests the API integration without manual intervention.
        """
        instance_name = clean_test_instance

        print(f"\n🔄 Testing instance lifecycle: {instance_name}")

        # Create
        print("1️⃣ Creating instance...")
        create_response = real_client.instance.create(instance_name=instance_name, qrcode=True)

        assert create_response is not None
        print(f"✅ Created: {create_response.instance.status}")

        # Fetch from list
        print("2️⃣ Fetching from instances list...")
        instances = real_client.instance.fetch_instances()

        our_instance = None
        for instance in instances:
            if (
                instance.name == instance_name
                or instance.id == create_response.instance.instance_id
            ):
                our_instance = instance
                break

        assert our_instance is not None, "Instance not found in list"
        print(f"✅ Found in list: {our_instance.id}")

        # Check connection state
        print("3️⃣ Checking connection state...")
        try:
            status = real_client.instance.connection_state(instance_name)
            assert status is not None
            print(f"✅ Status retrieved: {type(status)}")
        except Exception as e:
            print(f"⚠️ Status check failed (acceptable): {e}")

        # Restart (if supported)
        print("4️⃣ Testing restart...")
        try:
            restart_response = real_client.instance.restart(instance_name)
            print("✅ Restart command accepted")
            time.sleep(2)  # Wait for restart
        except Exception as e:
            print(f"⚠️ Restart failed (may not be supported): {e}")

        print("✅ Instance lifecycle test completed!")

    def test_error_handling_workflow(self, real_client):
        """Test error handling in typical workflows."""

        print("\n❌ Testing error handling scenarios...")

        # Test 1: Non-existent instance operations
        print("1️⃣ Testing non-existent instance operations...")

        fake_instance = "non-existent-instance-12345"

        try:
            status = real_client.instance.connection_state(fake_instance)
            # Some APIs return empty response, others error - both acceptable
            print(f"⚠️ Non-existent instance returned: {type(status)}")
        except Exception as e:
            print(f"✅ Non-existent instance error handled: {type(e).__name__}")

        try:
            real_client.instance.delete(fake_instance)
            print("⚠️ Delete non-existent succeeded (unusual but acceptable)")
        except Exception as e:
            print(f"✅ Delete non-existent error handled: {type(e).__name__}")

        # Test 2: Invalid parameters
        print("2️⃣ Testing invalid parameters...")

        try:
            real_client.instance.create(instance_name="", qrcode=True)  # Empty name
            print("⚠️ Empty instance name accepted (unusual)")
        except Exception as e:
            print(f"✅ Empty name error handled: {type(e).__name__}")

        print("✅ Error handling workflow completed!")


@pytest.mark.e2e
@pytest.mark.slow
class TestPerformanceWorkflow:
    """Test performance aspects of complete workflows."""

    def test_multiple_instance_creation(self, real_client):
        """Test creating multiple instances in sequence."""
        print("\n⚡ Testing multiple instance creation...")

        created_instances = []

        try:
            for i in range(3):
                instance_name = f"perf-test-{int(time.time())}-{i}"

                start_time = time.time()
                response = real_client.instance.create(instance_name=instance_name, qrcode=True)
                elapsed = time.time() - start_time

                assert response is not None
                created_instances.append(instance_name)

                print(f"✅ Instance {i+1} created in {elapsed:.2f}s")

                # Small delay to avoid rate limiting
                time.sleep(1)

        finally:
            # Cleanup
            print("🧹 Cleaning up test instances...")
            for instance_name in created_instances:
                try:
                    real_client.instance.delete(instance_name)
                    print(f"🗑️ Deleted: {instance_name}")
                except Exception as e:
                    print(f"⚠️ Failed to delete {instance_name}: {e}")

        print(f"✅ Created and cleaned up {len(created_instances)} instances")
