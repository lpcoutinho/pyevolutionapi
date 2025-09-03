# Connecting WhatsApp Instances

Learn how to create and connect WhatsApp instances using QR codes with PyEvolution.

## Overview

To use WhatsApp with PyEvolution, you need to:
1. **Create an instance** - Set up a new WhatsApp connection
2. **Generate QR Code** - Get the QR code for WhatsApp authentication
3. **Scan QR Code** - Use WhatsApp mobile app to scan and connect
4. **Verify connection** - Ensure the instance is properly connected

## Creating a New Instance

### Basic Instance Creation

```python
from pyevolutionapi import EvolutionClient

# Initialize client
client = EvolutionClient(
    base_url="http://localhost:8080",
    api_key="your-api-key"
)

# Create instance with QR code
instance = client.instance.create(
    instance_name="my-whatsapp-bot",
    qrcode=True  # Generate QR code immediately
)

# Access QR code data
if instance.qrcode:
    print("QR Code Base64:", instance.qr_code_base64)
    print("Raw QR Code:", instance.qrcode)
```

### Instance Creation Parameters

```python
# Complete parameter example
instance = client.instance.create(
    instance_name="production-bot",
    qrcode=True,                    # Generate QR code
    # Additional optional parameters based on Evolution API
)
```

### Instance Naming Best Practices

```python
# ✅ Good instance names
"customer-support-bot"
"sales-team-whatsapp"
"notifications-service"
"user-123-personal"

# ❌ Avoid these patterns
"instance1"           # Not descriptive
"test test test"      # Spaces and repetition
"PROD-BOT!!!"        # Special characters
```

## Getting QR Code

### Method 1: Create with QR Code

```python
# QR code generated during creation
instance = client.instance.create("my-bot", qrcode=True)

if instance.qrcode:
    qr_base64 = instance.qr_code_base64
    print(f"QR Code ready: {len(qr_base64)} characters")
else:
    print("No QR code generated")
```

### Method 2: Connect Existing Instance

```python
# For existing instances, use connect() to get new QR code
qr_data = client.instance.connect("my-bot")

if qr_data.qrcode:
    print("New QR Code:", qr_data.qr_code_base64)
```

## Displaying QR Code

### Option 1: Base64 Data URL (Web)

```python
qr_base64 = instance.qr_code_base64
if qr_base64:
    # Create data URL for HTML img tag
    data_url = f"data:image/png;base64,{qr_base64}"
    print(f"Use this in HTML: <img src='{data_url}' />")
```

### Option 2: Save as Image File

```python
import base64
from pathlib import Path

qr_base64 = instance.qr_code_base64
if qr_base64:
    # Decode and save as PNG file
    qr_data = base64.b64decode(qr_base64)
    Path("qr_code.png").write_bytes(qr_data)
    print("QR code saved as qr_code.png")
```

### Option 3: Terminal Display (with qrcode library)

```python
# First install: pip install qrcode[pil]
import qrcode
import io
from PIL import Image
import base64

qr_base64 = instance.qr_code_base64
if qr_base64:
    # Decode base64 image
    img_data = base64.b64decode(qr_base64)
    img = Image.open(io.BytesIO(img_data))

    # Display in terminal (requires compatible terminal)
    img.show()  # Opens system image viewer
```

## Connection Status

### Check Connection State

```python
# Check if instance is connected
status = client.instance.connection_state("my-bot")

print("Connection Status:", status)
# Possible states: 'open', 'close', 'connecting'
```

### Connection State Examples

```python
def check_connection_status(client, instance_name):
    """Check and display connection status."""
    try:
        status = client.instance.connection_state(instance_name)

        state = status.get('state', 'unknown')

        if state == 'open':
            print(f"✅ {instance_name} is connected and ready")
            return True
        elif state == 'close':
            print(f"❌ {instance_name} is disconnected")
            return False
        elif state == 'connecting':
            print(f"⏳ {instance_name} is connecting...")
            return False
        else:
            print(f"❓ {instance_name} status unknown: {state}")
            return False

    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return False

# Usage
is_connected = check_connection_status(client, "my-bot")
```

## Complete Connection Flow

### Full Example with Error Handling

```python
import time
from pyevolutionapi import EvolutionClient
from pyevolutionapi.exceptions import EvolutionAPIError

def setup_whatsapp_instance(instance_name: str):
    """Complete setup flow for WhatsApp instance."""

    client = EvolutionClient()

    try:
        # Step 1: Create instance
        print(f"🔧 Creating instance '{instance_name}'...")
        instance = client.instance.create(instance_name, qrcode=True)

        if not instance.qrcode:
            print("❌ No QR code generated. Trying to connect...")
            instance = client.instance.connect(instance_name)

        # Step 2: Display QR code
        if instance.qr_code_base64:
            print("📱 QR Code generated successfully!")
            print("👀 Scan this QR code with WhatsApp:")
            print("   1. Open WhatsApp on your phone")
            print("   2. Go to Settings > Connected Devices")
            print("   3. Tap 'Connect a device'")
            print("   4. Point your phone at this QR code")

            # Save QR code to file
            import base64
            from pathlib import Path
            qr_data = base64.b64decode(instance.qr_code_base64)
            Path(f"{instance_name}_qr.png").write_bytes(qr_data)
            print(f"💾 QR code saved as {instance_name}_qr.png")

        # Step 3: Wait for connection
        print("⏳ Waiting for WhatsApp connection...")
        max_attempts = 60  # 5 minutes
        attempt = 0

        while attempt < max_attempts:
            status = client.instance.connection_state(instance_name)
            state = status.get('state')

            if state == 'open':
                print("✅ Successfully connected to WhatsApp!")
                return True
            elif state == 'close':
                print("❌ Connection failed or QR code expired")
                break

            time.sleep(5)  # Check every 5 seconds
            attempt += 1

            if attempt % 12 == 0:  # Every minute
                print(f"⏳ Still waiting... ({attempt//12} min)")

        print("⏰ Connection timeout. Please try again.")
        return False

    except EvolutionAPIError as e:
        print(f"❌ API Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

# Usage
if __name__ == "__main__":
    success = setup_whatsapp_instance("my-production-bot")

    if success:
        print("🎉 Instance ready for use!")
    else:
        print("❌ Setup failed. Please check your configuration.")
```

## Advanced Connection Management

### Multiple Instances

```python
def create_multiple_instances():
    """Create and manage multiple WhatsApp instances."""
    client = EvolutionClient()

    instances = ["support-bot", "sales-bot", "notifications"]

    for instance_name in instances:
        print(f"\n🔧 Setting up {instance_name}...")

        # Create instance
        instance = client.instance.create(instance_name, qrcode=True)

        if instance.qr_code_base64:
            # Save each QR code separately
            import base64
            from pathlib import Path
            qr_data = base64.b64decode(instance.qr_code_base64)
            Path(f"qr_codes/{instance_name}.png").write_bytes(qr_data)
            print(f"💾 QR code saved for {instance_name}")

        # Small delay between instances
        time.sleep(2)
```

### Reconnection Helper

```python
def ensure_connected(client, instance_name, max_retries=3):
    """Ensure instance is connected, reconnect if necessary."""

    for attempt in range(max_retries):
        status = client.instance.connection_state(instance_name)

        if status.get('state') == 'open':
            return True

        print(f"🔄 Attempt {attempt + 1}: Reconnecting {instance_name}...")

        try:
            # Try to reconnect
            qr_data = client.instance.connect(instance_name)

            if qr_data.qr_code_base64:
                print(f"📱 New QR code generated for {instance_name}")
                # Handle QR code display here

            # Wait a bit before checking again
            time.sleep(10)

        except Exception as e:
            print(f"❌ Reconnection failed: {e}")

        if attempt < max_retries - 1:
            time.sleep(5)  # Wait before retry

    return False
```

## Troubleshooting

### Common Issues

#### QR Code Not Generated
```python
# Check if instance was created successfully
instance = client.instance.create("test", qrcode=True)

if not instance.qrcode:
    print("❌ No QR code in create response")

    # Try connecting to generate QR code
    qr_data = client.instance.connect("test")

    if qr_data.qrcode:
        print("✅ QR code generated via connect method")
    else:
        print("❌ Still no QR code - check Evolution API status")
```

#### QR Code Expired
```python
def handle_expired_qr(client, instance_name):
    """Handle expired QR code scenario."""

    print("🔄 QR Code expired, generating new one...")

    try:
        # Generate new QR code
        new_qr = client.instance.connect(instance_name)

        if new_qr.qr_code_base64:
            print("✅ New QR code generated")
            return new_qr.qr_code_base64
        else:
            print("❌ Failed to generate new QR code")
            return None

    except Exception as e:
        print(f"❌ Error generating new QR code: {e}")
        return None
```

#### Connection Stuck
```python
def reset_instance(client, instance_name):
    """Reset instance if connection is stuck."""

    print(f"🔄 Resetting instance {instance_name}...")

    try:
        # Try logout first
        client.instance.logout(instance_name)
        time.sleep(2)

        # Then restart
        client.instance.restart(instance_name)
        time.sleep(5)

        # Get new QR code
        qr_data = client.instance.connect(instance_name)

        if qr_data.qr_code_base64:
            print("✅ Instance reset successful, new QR code ready")
            return True
        else:
            print("❌ Reset failed")
            return False

    except Exception as e:
        print(f"❌ Reset error: {e}")
        return False
```

### Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "Instance not found" | Instance name doesn't exist | Check spelling, create instance first |
| "QR code expired" | QR code timeout (usually 45s) | Generate new QR code with `connect()` |
| "Connection timeout" | Network issues | Check Evolution API server status |
| "Invalid instance name" | Name contains invalid characters | Use alphanumeric + hyphens only |

## Best Practices

### Security
- ✅ Use descriptive but not sensitive instance names
- ✅ Store QR codes securely (don't commit to git)
- ✅ Implement connection timeouts
- ✅ Handle disconnections gracefully

### Performance
- ✅ Check connection status before sending messages
- ✅ Implement retry logic for failed connections
- ✅ Use connection pooling for multiple instances
- ✅ Cache connection status to avoid excessive API calls

### Monitoring
- ✅ Log connection events
- ✅ Set up alerts for disconnections
- ✅ Monitor QR code generation failures
- ✅ Track connection success rates

## Next Steps

Once your instance is connected:
- [Send Messages](../examples/messages.md) - Learn message sending
- [Manage Groups](../examples/groups.md) - Work with WhatsApp groups
- [Set Up Webhooks](../examples/webhooks.md) - Receive real-time events
- [API Reference](../api/instance.md) - Full instance management API
