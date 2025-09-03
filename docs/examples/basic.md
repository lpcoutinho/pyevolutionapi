# Basic Examples

Practical examples to get you started with PyEvolution quickly.

## Simple Bot Setup

```python
#!/usr/bin/env python3
"""Simple WhatsApp bot with PyEvolution."""

import time
import base64
from pathlib import Path
from pyevolutionapi import EvolutionClient
from pyevolutionapi.exceptions import EvolutionAPIError

# Initialize client
client = EvolutionClient(
    base_url="http://localhost:8080",
    api_key="your-api-key"
)

def create_and_connect():
    """Create instance and handle QR code connection."""

    instance_name = "basic-bot"

    try:
        # Create instance
        print("🔧 Creating WhatsApp instance...")
        instance = client.instance.create(instance_name, qrcode=True)

        if instance.qr_code_base64:
            # Save QR code
            qr_data = base64.b64decode(instance.qr_code_base64)
            Path("basic_bot_qr.png").write_bytes(qr_data)
            print("📱 QR code saved as 'basic_bot_qr.png'")
            print("📱 Scan with WhatsApp → Settings → Connected Devices")

        # Wait for connection
        print("⏳ Waiting for connection...")
        for i in range(60):  # 5 minutes max
            status = client.instance.connection_state(instance_name)

            if status.get('state') == 'open':
                print("✅ Connected to WhatsApp!")
                return instance_name

            time.sleep(5)

        print("❌ Connection timeout")
        return None

    except EvolutionAPIError as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    bot_instance = create_and_connect()

    if bot_instance:
        print(f"🎉 Bot '{bot_instance}' is ready!")
```

## Send Different Message Types

```python
#!/usr/bin/env python3
"""Examples of different message types."""

from pyevolutionapi import EvolutionClient

client = EvolutionClient()
instance = "my-bot"
phone = "5511999999999"  # Replace with actual number

def send_text_message():
    """Send simple text message."""
    response = client.messages.send_text(
        instance=instance,
        number=phone,
        text="Hello! This is a text message from PyEvolution 📱"
    )

    if response.key:
        print(f"✅ Text message sent: {response.key.id}")
    return response

def send_media_message():
    """Send image with caption."""
    try:
        response = client.messages.send_media(
            instance=instance,
            number=phone,
            media_type="image",
            media="https://picsum.photos/300/200",  # Sample image
            caption="🖼️ Here's a random image!"
        )

        if response.key:
            print(f"✅ Image sent: {response.key.id}")
        return response

    except Exception as e:
        print(f"❌ Media error: {e}")
        return None

def send_document():
    """Send a document file."""
    try:
        response = client.messages.send_media(
            instance=instance,
            number=phone,
            media_type="document",
            media="/path/to/document.pdf",  # Local file path
            filename="my_document.pdf"
        )

        if response.key:
            print(f"✅ Document sent: {response.key.id}")
        return response

    except Exception as e:
        print(f"❌ Document error: {e}")
        return None

def send_location():
    """Send location coordinates."""
    try:
        response = client.messages.send_location(
            instance=instance,
            number=phone,
            latitude=-23.5505,    # São Paulo coordinates
            longitude=-46.6333,
            name="São Paulo",
            address="São Paulo, SP, Brazil"
        )

        if response.key:
            print(f"✅ Location sent: {response.key.id}")
        return response

    except Exception as e:
        print(f"❌ Location error: {e}")
        return None

# Send all message types
if __name__ == "__main__":
    print("📤 Sending different message types...")

    send_text_message()
    time.sleep(1)

    send_media_message()
    time.sleep(1)

    send_location()
    print("✅ All messages sent!")
```

## Instance Management

```python
#!/usr/bin/env python3
"""Manage multiple WhatsApp instances."""

from pyevolutionapi import EvolutionClient
import time

client = EvolutionClient()

def list_all_instances():
    """List all existing instances."""
    try:
        instances = client.instance.fetch_instances()

        print(f"📋 Found {len(instances)} instances:")
        for instance in instances:
            print(f"   • {instance.instance_name} - {instance.status}")

        return instances

    except Exception as e:
        print(f"❌ Error listing instances: {e}")
        return []

def check_instance_status(instance_name):
    """Check connection status of specific instance."""
    try:
        status = client.instance.connection_state(instance_name)
        state = status.get('state', 'unknown')

        status_emoji = {
            'open': '✅',
            'close': '❌',
            'connecting': '⏳',
            'unknown': '❓'
        }

        print(f"{status_emoji.get(state, '❓')} {instance_name}: {state}")
        return state

    except Exception as e:
        print(f"❌ Error checking {instance_name}: {e}")
        return None

def restart_instance(instance_name):
    """Restart an instance if it's having issues."""
    try:
        print(f"🔄 Restarting {instance_name}...")

        # Restart the instance
        response = client.instance.restart(instance_name)
        time.sleep(5)  # Wait for restart

        # Check new status
        new_status = check_instance_status(instance_name)

        if new_status == 'open':
            print(f"✅ {instance_name} restarted successfully")
        else:
            print(f"⚠️ {instance_name} restart completed but not connected")

        return response

    except Exception as e:
        print(f"❌ Restart error: {e}")
        return None

def delete_instance(instance_name):
    """Delete an instance (use with caution!)."""
    try:
        confirmation = input(f"⚠️ Delete '{instance_name}'? (yes/no): ")

        if confirmation.lower() == 'yes':
            response = client.instance.delete(instance_name)
            print(f"🗑️ Instance '{instance_name}' deleted")
            return response
        else:
            print("❌ Deletion cancelled")
            return None

    except Exception as e:
        print(f"❌ Delete error: {e}")
        return None

# Example usage
if __name__ == "__main__":
    print("🔧 Instance Management Example\n")

    # List all instances
    instances = list_all_instances()

    # Check status of each instance
    print("\n📊 Instance Status:")
    for instance in instances:
        check_instance_status(instance.instance_name)

    # Example: restart first instance if needed
    if instances:
        first_instance = instances[0].instance_name
        status = check_instance_status(first_instance)

        if status != 'open':
            print(f"\n🔄 Instance {first_instance} is not connected")
            restart_choice = input("Restart it? (y/n): ")
            if restart_choice.lower() == 'y':
                restart_instance(first_instance)
```

## Contact and Chat Operations

```python
#!/usr/bin/env python3
"""Work with contacts and chats."""

from pyevolutionapi import EvolutionClient

client = EvolutionClient()
instance = "my-bot"

def check_whatsapp_number(number):
    """Check if a number is on WhatsApp."""
    try:
        result = client.chat.whatsapp_numbers(
            instance=instance,
            numbers=[number]
        )

        for check in result:
            if check.get('exists'):
                print(f"✅ {check['jid']} is on WhatsApp")
                return True
            else:
                print(f"❌ {number} is not on WhatsApp")
                return False

    except Exception as e:
        print(f"❌ Error checking number: {e}")
        return False

def get_profile_picture(number):
    """Get profile picture of a contact."""
    try:
        profile_pic = client.chat.fetch_profile_picture(
            instance=instance,
            number=number
        )

        if profile_pic.get('profilePicUrl'):
            print(f"📸 Profile pic URL: {profile_pic['profilePicUrl']}")
            return profile_pic['profilePicUrl']
        else:
            print(f"📸 No profile picture for {number}")
            return None

    except Exception as e:
        print(f"❌ Error getting profile pic: {e}")
        return None

def find_recent_chats():
    """Find recent chat conversations."""
    try:
        chats = client.chat.find_chats(instance=instance)

        print(f"💬 Found {len(chats)} recent chats:")
        for chat in chats[:5]:  # Show first 5
            name = chat.get('name', 'Unknown')
            jid = chat.get('id', 'No ID')
            print(f"   • {name} ({jid})")

        return chats

    except Exception as e:
        print(f"❌ Error finding chats: {e}")
        return []

def mark_chat_as_read(number):
    """Mark all messages from a contact as read."""
    try:
        response = client.chat.mark_as_read(
            instance=instance,
            read_messages=[{"id": f"{number}@s.whatsapp.net"}]
        )

        print(f"✅ Marked chat with {number} as read")
        return response

    except Exception as e:
        print(f"❌ Error marking as read: {e}")
        return None

def send_typing_indicator(number):
    """Send typing indicator to a contact."""
    try:
        response = client.chat.send_presence(
            instance=instance,
            number=number,
            presence="composing"  # composing, paused, recording
        )

        print(f"⌨️ Sent typing indicator to {number}")
        return response

    except Exception as e:
        print(f"❌ Error sending presence: {e}")
        return None

# Example usage
if __name__ == "__main__":
    print("👤 Contact and Chat Examples\n")

    test_number = "5511999999999"  # Replace with real number

    # Check if number is on WhatsApp
    is_on_whatsapp = check_whatsapp_number(test_number)

    if is_on_whatsapp:
        # Get profile picture
        get_profile_picture(test_number)

        # Send typing indicator
        send_typing_indicator(test_number)

        # Mark as read
        mark_chat_as_read(test_number)

    # Find recent chats
    print("\n💬 Recent Chats:")
    find_recent_chats()
```

## Error Handling Examples

```python
#!/usr/bin/env python3
"""Proper error handling with PyEvolution."""

from pyevolutionapi import EvolutionClient
from pyevolutionapi.exceptions import (
    EvolutionAPIError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    ConnectionError
)
import time

client = EvolutionClient()

def safe_send_message(instance, number, text):
    """Send message with comprehensive error handling."""
    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            response = client.messages.send_text(
                instance=instance,
                number=number,
                text=text
            )

            if response.key:
                print(f"✅ Message sent successfully: {response.key.id}")
                return response
            else:
                print("⚠️ Message sent but no key returned")
                return response

        except AuthenticationError as e:
            print(f"🔐 Authentication failed: {e}")
            print("💡 Check your API key and permissions")
            return None

        except NotFoundError as e:
            print(f"🔍 Resource not found: {e}")
            print("💡 Check if instance exists and is connected")
            return None

        except ValidationError as e:
            print(f"📝 Validation error: {e}")
            print("💡 Check your parameters (number format, etc.)")
            return None

        except RateLimitError as e:
            print(f"🚦 Rate limit exceeded: {e}")
            retry_after = getattr(e, 'retry_after', 60)
            print(f"⏳ Waiting {retry_after} seconds before retry...")
            time.sleep(retry_after)
            continue

        except ConnectionError as e:
            print(f"🌐 Connection error: {e}")
            if attempt < max_retries - 1:
                print(f"🔄 Retrying in {retry_delay}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
                continue
            else:
                print("❌ Max retries reached")
                return None

        except EvolutionAPIError as e:
            print(f"🚫 API error: {e}")
            return None

        except Exception as e:
            print(f"💥 Unexpected error: {e}")
            return None

    return None

def safe_instance_operation(instance_name, operation="status"):
    """Safely perform instance operations."""
    try:
        if operation == "status":
            return client.instance.connection_state(instance_name)

        elif operation == "connect":
            return client.instance.connect(instance_name)

        elif operation == "restart":
            return client.instance.restart(instance_name)

        else:
            print(f"❌ Unknown operation: {operation}")
            return None

    except NotFoundError:
        print(f"❌ Instance '{instance_name}' not found")
        print("💡 Create the instance first or check the name")
        return None

    except AuthenticationError:
        print(f"🔐 Authentication failed for '{instance_name}'")
        print("💡 Check API key and instance permissions")
        return None

    except Exception as e:
        print(f"❌ Error with instance '{instance_name}': {e}")
        return None

def health_check():
    """Perform a comprehensive health check."""
    print("🏥 PyEvolution Health Check\n")

    try:
        # Test API connection
        instances = client.instance.fetch_instances()
        print(f"✅ API Connection: OK ({len(instances)} instances)")

        # Check each instance
        for instance in instances:
            name = instance.instance_name
            status = safe_instance_operation(name, "status")

            if status:
                state = status.get('state', 'unknown')
                print(f"📱 Instance '{name}': {state}")
            else:
                print(f"❌ Instance '{name}': Error getting status")

        print("\n✅ Health check completed")

    except Exception as e:
        print(f"❌ Health check failed: {e}")

# Example usage
if __name__ == "__main__":
    print("🛡️ Error Handling Examples\n")

    # Health check first
    health_check()

    # Safe message sending
    print("\n📤 Testing safe message sending:")
    result = safe_send_message(
        instance="test-bot",
        number="5511999999999",
        text="Test message with error handling"
    )

    if result:
        print("✅ Message handling successful")
    else:
        print("❌ Message handling failed")
```

## Batch Operations

```python
#!/usr/bin/env python3
"""Batch operations for multiple contacts."""

from pyevolutionapi import EvolutionClient
import time
import asyncio
from typing import List, Dict

client = EvolutionClient()

def send_bulk_messages(instance: str, contacts: List[str], message: str):
    """Send same message to multiple contacts."""
    results = []

    print(f"📤 Sending message to {len(contacts)} contacts...")

    for i, contact in enumerate(contacts):
        try:
            print(f"📱 Sending to {contact} ({i+1}/{len(contacts)})")

            response = client.messages.send_text(
                instance=instance,
                number=contact,
                text=message
            )

            if response.key:
                results.append({
                    'contact': contact,
                    'status': 'success',
                    'message_id': response.key.id
                })
                print(f"✅ Sent to {contact}")
            else:
                results.append({
                    'contact': contact,
                    'status': 'failed',
                    'error': 'No message key'
                })
                print(f"❌ Failed to {contact}")

            # Rate limiting - wait between messages
            time.sleep(2)

        except Exception as e:
            results.append({
                'contact': contact,
                'status': 'error',
                'error': str(e)
            })
            print(f"❌ Error sending to {contact}: {e}")

    # Summary
    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] != 'success']

    print(f"\n📊 Bulk Send Results:")
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")

    return results

def send_personalized_messages(instance: str, messages: Dict[str, str]):
    """Send personalized messages to different contacts."""
    results = []

    print(f"📤 Sending personalized messages to {len(messages)} contacts...")

    for contact, message in messages.items():
        try:
            print(f"📱 Sending personalized message to {contact}")

            response = client.messages.send_text(
                instance=instance,
                number=contact,
                text=message
            )

            if response.key:
                results.append({
                    'contact': contact,
                    'status': 'success',
                    'message_id': response.key.id
                })
                print(f"✅ Sent to {contact}")
            else:
                results.append({
                    'contact': contact,
                    'status': 'failed'
                })
                print(f"❌ Failed to {contact}")

            time.sleep(2)  # Rate limiting

        except Exception as e:
            results.append({
                'contact': contact,
                'status': 'error',
                'error': str(e)
            })
            print(f"❌ Error: {e}")

    return results

def validate_numbers(instance: str, numbers: List[str]):
    """Validate which numbers are on WhatsApp."""
    try:
        print(f"🔍 Validating {len(numbers)} numbers...")

        # Check in batches of 10 (API limitation)
        batch_size = 10
        all_results = []

        for i in range(0, len(numbers), batch_size):
            batch = numbers[i:i+batch_size]

            results = client.chat.whatsapp_numbers(
                instance=instance,
                numbers=batch
            )

            all_results.extend(results)
            time.sleep(1)  # Small delay between batches

        # Process results
        valid_numbers = []
        invalid_numbers = []

        for result in all_results:
            if result.get('exists'):
                valid_numbers.append(result['jid'])
                print(f"✅ {result['jid']} - Valid")
            else:
                invalid_numbers.append(result.get('number', 'Unknown'))
                print(f"❌ {result.get('number', 'Unknown')} - Invalid")

        print(f"\n📊 Validation Results:")
        print(f"✅ Valid: {len(valid_numbers)}")
        print(f"❌ Invalid: {len(invalid_numbers)}")

        return {
            'valid': valid_numbers,
            'invalid': invalid_numbers,
            'total_checked': len(numbers)
        }

    except Exception as e:
        print(f"❌ Validation error: {e}")
        return None

# Example usage
if __name__ == "__main__":
    instance_name = "batch-bot"

    # Example contact list
    contact_list = [
        "5511999999999",
        "5511888888888",
        "5511777777777"
    ]

    # Example 1: Validate numbers first
    print("🔍 Step 1: Validating numbers...")
    validation_results = validate_numbers(instance_name, contact_list)

    if validation_results and validation_results['valid']:
        valid_contacts = validation_results['valid']

        # Example 2: Send same message to all
        print("\n📤 Step 2: Bulk messaging...")
        bulk_message = "Hello! This is a bulk message from PyEvolution 🚀"
        bulk_results = send_bulk_messages(instance_name, valid_contacts[:2], bulk_message)

        # Example 3: Send personalized messages
        print("\n📤 Step 3: Personalized messaging...")
        personalized = {
            valid_contacts[0]: f"Hi there! Welcome to our service! 👋",
            valid_contacts[1]: f"Thanks for joining us! Here's your welcome message 🎉"
        }

        personal_results = send_personalized_messages(instance_name, personalized)

        print("\n✅ All batch operations completed!")
    else:
        print("❌ No valid numbers found for messaging")
```

## Integration with Web Framework (Flask)

```python
#!/usr/bin/env python3
"""Flask web integration example."""

from flask import Flask, request, jsonify
from pyevolutionapi import EvolutionClient
import os

app = Flask(__name__)

# Initialize PyEvolution client
client = EvolutionClient()
DEFAULT_INSTANCE = os.getenv('EVOLUTION_INSTANCE_NAME', 'web-bot')

@app.route('/send-message', methods=['POST'])
def send_message_endpoint():
    """API endpoint to send WhatsApp messages."""
    try:
        data = request.get_json()

        # Validate required fields
        if not data or 'number' not in data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: number, text'
            }), 400

        # Send message
        response = client.messages.send_text(
            instance=data.get('instance', DEFAULT_INSTANCE),
            number=data['number'],
            text=data['text']
        )

        if response.key:
            return jsonify({
                'success': True,
                'message_id': response.key.id,
                'status': 'sent'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send message'
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/instance-status', methods=['GET'])
def instance_status():
    """Check instance connection status."""
    try:
        instance_name = request.args.get('instance', DEFAULT_INSTANCE)

        status = client.instance.connection_state(instance_name)

        return jsonify({
            'instance': instance_name,
            'status': status.get('state', 'unknown'),
            'connected': status.get('state') == 'open'
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'connected': False
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        instances = client.instance.fetch_instances()

        return jsonify({
            'status': 'healthy',
            'instances_count': len(instances),
            'api_connected': True
        })

    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'api_connected': False
        }), 500

if __name__ == '__main__':
    print("🌐 Starting Flask + PyEvolution integration...")
    print(f"📱 Default instance: {DEFAULT_INSTANCE}")
    print("🔗 Endpoints:")
    print("   POST /send-message - Send WhatsApp messages")
    print("   GET  /instance-status - Check connection status")
    print("   GET  /health - API health check")

    app.run(debug=True, host='0.0.0.0', port=5000)
```

## Conclusion

These examples show various ways to use PyEvolution:

- 🔧 **Basic Setup**: Create instances and handle QR codes
- 💬 **Messaging**: Send different message types
- 👤 **Contacts**: Manage contacts and chats
- 🛡️ **Error Handling**: Robust error handling patterns
- 📊 **Batch Operations**: Handle multiple contacts efficiently
- 🌐 **Web Integration**: Use with Flask/web frameworks

## Next Steps

- [Advanced Message Types](messages.md) - Images, documents, audio
- [Group Management](groups.md) - Create and manage WhatsApp groups
- [Webhook Integration](webhooks.md) - Real-time event handling
- [API Reference](../api/) - Complete API documentation
