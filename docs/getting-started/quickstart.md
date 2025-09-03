# Quick Start

Get up and running with PyEvolution in minutes.

## Installation

```bash
pip install pyevolutionapi
```

## Basic Setup

### 1. Initialize Client

```python
from pyevolutionapi import EvolutionClient

# Option 1: Direct configuration
client = EvolutionClient(
    base_url="http://localhost:8080",
    api_key="your-api-key"
)

# Option 2: Using environment variables (recommended)
client = EvolutionClient()  # Reads from .env automatically
```

### 2. Create and Connect Instance

```python
# Create instance with QR code
print("🔧 Creating WhatsApp instance...")
instance = client.instance.create("my-bot", qrcode=True)

# Display QR code information
if instance.qrcode:
    print("📱 QR Code generated! Scan with WhatsApp:")
    print("   1. Open WhatsApp → Settings → Connected Devices")
    print("   2. Tap 'Connect a device' and scan this code")

    # Save QR code as image file
    import base64
    from pathlib import Path
    qr_data = base64.b64decode(instance.qr_code_base64)
    Path("whatsapp_qr.png").write_bytes(qr_data)
    print("💾 QR code saved as 'whatsapp_qr.png'")
else:
    print("❌ No QR code generated")
```

### 3. Wait for Connection

```python
import time

print("⏳ Waiting for connection...")
for i in range(60):  # Wait up to 5 minutes
    status = client.instance.connection_state("my-bot")

    if status.get('state') == 'open':
        print("✅ Connected successfully!")
        break
    elif status.get('state') == 'close':
        print("❌ Connection failed")
        break

    time.sleep(5)  # Check every 5 seconds
    if i % 12 == 0:  # Print status every minute
        print(f"⏳ Still waiting... ({i//12} min)")
else:
    print("⏰ Connection timeout")
```

### 4. Send Your First Message

```python
# Send a text message
try:
    response = client.messages.send_text(
        instance="my-bot",
        number="5511999999999",  # Replace with actual number
        text="🎉 Hello from PyEvolution! My first automated message."
    )

    if response.key:
        print(f"✅ Message sent! ID: {response.key.id}")
    else:
        print("❌ Message failed")

except Exception as e:
    print(f"❌ Error sending message: {e}")
```

## Complete Example

```python
#!/usr/bin/env python3
"""Complete PyEvolution setup example."""

import time
import base64
from pathlib import Path
from pyevolutionapi import EvolutionClient

def setup_whatsapp_bot():
    """Set up a WhatsApp bot from scratch."""

    # 1. Initialize client
    client = EvolutionClient(
        base_url="http://localhost:8080",
        api_key="your-api-key"
    )

    instance_name = "quickstart-bot"

    try:
        # 2. Create instance
        print(f"🔧 Creating instance '{instance_name}'...")
        instance = client.instance.create(instance_name, qrcode=True)

        # 3. Handle QR code
        if instance.qr_code_base64:
            # Save QR code
            qr_data = base64.b64decode(instance.qr_code_base64)
            qr_path = Path(f"{instance_name}_qr.png")
            qr_path.write_bytes(qr_data)

            print("📱 QR Code ready! Please scan:")
            print(f"   📁 Saved as: {qr_path}")
            print("   📱 Open WhatsApp → Settings → Connected Devices")
            print("   📱 Tap 'Connect a device' and scan the QR code")

        else:
            print("❌ No QR code generated")
            return False

        # 4. Wait for connection
        print("⏳ Waiting for WhatsApp connection...")
        max_wait = 60  # 5 minutes

        for attempt in range(max_wait):
            status = client.instance.connection_state(instance_name)
            state = status.get('state', 'unknown')

            if state == 'open':
                print("✅ Successfully connected to WhatsApp!")
                break
            elif state == 'close':
                print("❌ Connection failed or QR code expired")
                return False

            time.sleep(5)

            if attempt % 12 == 0 and attempt > 0:
                print(f"⏳ Still waiting... ({attempt//12} min)")
        else:
            print("⏰ Connection timeout")
            return False

        # 5. Send test message (replace with your number)
        test_number = "5511999999999"  # Change this!

        print(f"📤 Sending test message to {test_number}...")
        response = client.messages.send_text(
            instance=instance_name,
            number=test_number,
            text="🎉 PyEvolution is working! This is an automated test message."
        )

        if response.key:
            print(f"✅ Test message sent! Message ID: {response.key.id}")
        else:
            print("❌ Test message failed")

        print("🎉 Setup complete! Your WhatsApp bot is ready.")
        return True

    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

if __name__ == "__main__":
    success = setup_whatsapp_bot()

    if success:
        print("\n🚀 Next steps:")
        print("   - Check out the examples: docs/examples/")
        print("   - Read API docs: docs/api/")
        print("   - Set up webhooks: docs/examples/webhooks.md")
    else:
        print("\n❌ Setup failed. Please check:")
        print("   - Evolution API server is running")
        print("   - API key is correct")
        print("   - Network connection is stable")
```

## Environment Variables

Create a `.env` file in your project root:

```bash
# Required
EVOLUTION_BASE_URL=http://localhost:8080
EVOLUTION_API_KEY=your-api-key-here

# Optional
EVOLUTION_INSTANCE_NAME=my-bot
EVOLUTION_DEBUG=false
EVOLUTION_REQUEST_TIMEOUT=30
```

## Common Issues

### QR Code Problems
```python
# If QR code doesn't appear, try reconnecting
qr_data = client.instance.connect("my-bot")
if qr_data.qr_code_base64:
    print("🆕 New QR code generated")
```

### Connection Timeout
```python
# Check connection status
status = client.instance.connection_state("my-bot")
print(f"Status: {status.get('state', 'unknown')}")

# Restart if needed
if status.get('state') != 'open':
    client.instance.restart("my-bot")
```

### Authentication Errors
```python
# Verify your API key and server
try:
    instances = client.instance.fetch_instances()
    print(f"✅ API working - Found {len(instances)} instances")
except Exception as e:
    print(f"❌ API Error: {e}")
```

## Next Steps

Now that you have PyEvolution working:

- **📚 [Connecting Instances](connecting.md)** - Detailed connection guide
- **💬 [Send Messages](../examples/messages.md)** - All message types
- **👥 [Manage Groups](../examples/groups.md)** - Group operations
- **🔗 [Webhooks](../examples/webhooks.md)** - Real-time notifications
- **📖 [API Reference](../api/)** - Complete API documentation
