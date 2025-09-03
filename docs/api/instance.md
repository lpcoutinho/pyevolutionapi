# Instance Management API

Comprehensive guide to managing WhatsApp instances with PyEvolution.

## Overview

The `InstanceResource` provides methods for managing WhatsApp instances, including creation, connection, status monitoring, and lifecycle management.

## Creating Instances

### Basic Instance Creation

```python
from pyevolutionapi import EvolutionClient

client = EvolutionClient()

# Simple instance creation
instance = client.instance.create(
    instance_name="my-whatsapp-bot",
    qrcode=True  # Generate QR code immediately
)
```

### Complete Parameter Reference

```python
# All available parameters
instance = client.instance.create(
    instance_name="production-bot",    # Required: Instance identifier
    qrcode=True,                       # Optional: Generate QR code (default: True)
    # Additional Evolution API specific parameters can be added here
    **kwargs                           # Any additional parameters
)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `instance_name` | `str` | ✅ | - | Unique identifier for the instance |
| `qrcode` | `bool` | ❌ | `True` | Whether to generate QR code immediately |

#### Response Model

The `create()` method returns an `InstanceResponse` object:

```python
class InstanceResponse:
    instance_name: str                    # Name of the created instance
    status: str                          # Current status
    qrcode: Optional[Dict[str, str]]     # QR code data if generated

    @property
    def qr_code_base64(self) -> Optional[str]:
        """Get QR code in base64 format."""
        if self.qrcode:
            return self.qrcode.get("base64")
        return None
```

### Instance Creation Examples

```python
# Example 1: Simple bot creation
support_bot = client.instance.create("support-bot", qrcode=True)

if support_bot.qr_code_base64:
    print("📱 QR Code generated for support-bot")
else:
    print("❌ No QR code generated")

# Example 2: Production instance with error handling
try:
    prod_instance = client.instance.create(
        instance_name="production-whatsapp",
        qrcode=True
    )

    print(f"✅ Instance created: {prod_instance.instance_name}")
    print(f"📊 Status: {prod_instance.status}")

    if prod_instance.qrcode:
        print(f"📱 QR Code available: {len(prod_instance.qr_code_base64)} characters")

except Exception as e:
    print(f"❌ Instance creation failed: {e}")
```

## Connection Management

### Getting QR Code

```python
# Method 1: Generate QR code during creation
instance = client.instance.create("my-bot", qrcode=True)

# Method 2: Generate QR code for existing instance
qr_data = client.instance.connect("my-bot")

# Method 3: Force new QR code generation
qr_data = client.instance.connect("my-bot", number=None)
```

### Connection with Phone Number (Direct)

```python
# Connect directly with phone number (if supported)
connection = client.instance.connect(
    instance="my-bot",
    number="5511999999999"  # Optional: direct connection
)
```

### QR Code Handling

```python
def handle_qr_code(instance_response):
    """Process QR code from instance response."""

    if not instance_response.qrcode:
        print("❌ No QR code available")
        return False

    # Get base64 QR code
    qr_base64 = instance_response.qr_code_base64

    if qr_base64:
        # Save as image file
        import base64
        from pathlib import Path

        qr_data = base64.b64decode(qr_base64)
        qr_path = Path(f"{instance_response.instance_name}_qr.png")
        qr_path.write_bytes(qr_data)

        print(f"📱 QR Code saved as: {qr_path}")
        return True

    return False

# Usage
instance = client.instance.create("test-bot", qrcode=True)
success = handle_qr_code(instance)
```

## Connection Status

### Checking Connection State

```python
# Get current connection status
status = client.instance.connection_state("my-bot")

print(f"Status: {status}")
# Example output: {'state': 'open', 'instance': 'my-bot'}
```

### Connection States

| State | Description | Actions Available |
|-------|-------------|-------------------|
| `open` | Connected and ready | Send messages, all operations |
| `close` | Disconnected | Need to reconnect with QR code |
| `connecting` | Connection in progress | Wait for completion |
| `unknown` | Status unclear | Check instance exists |

### Status Monitoring Example

```python
def monitor_connection(instance_name, timeout=300):
    """Monitor instance connection with timeout."""
    import time

    start_time = time.time()

    while time.time() - start_time < timeout:
        status = client.instance.connection_state(instance_name)
        state = status.get('state', 'unknown')

        if state == 'open':
            print(f"✅ {instance_name} connected successfully!")
            return True
        elif state == 'close':
            print(f"❌ {instance_name} connection failed")
            return False
        elif state == 'connecting':
            print(f"⏳ {instance_name} still connecting...")
        else:
            print(f"❓ {instance_name} unknown state: {state}")

        time.sleep(5)  # Check every 5 seconds

    print(f"⏰ {instance_name} connection timeout")
    return False

# Usage
connected = monitor_connection("my-bot", timeout=180)  # 3 minutes
```

## Instance Operations

### Restart Instance

```python
# Restart an instance
try:
    response = client.instance.restart("my-bot")
    print("🔄 Instance restarted")

    # Wait a moment then check status
    import time
    time.sleep(5)

    status = client.instance.connection_state("my-bot")
    print(f"📊 New status: {status.get('state')}")

except Exception as e:
    print(f"❌ Restart failed: {e}")
```

### Set Presence Status

```python
# Set online presence
response = client.instance.set_presence(
    instance="my-bot",
    presence="available"  # available, unavailable, composing, recording, paused
)

print("👤 Presence updated")
```

#### Presence Types

| Presence | Description | Use Case |
|----------|-------------|----------|
| `available` | Online and available | Default active state |
| `unavailable` | Offline/invisible | Privacy mode |
| `composing` | Typing indicator | Before sending messages |
| `recording` | Recording audio | Before sending voice notes |
| `paused` | Stopped typing | After composing |

### Logout Instance

```python
# Logout from WhatsApp
try:
    response = client.instance.logout("my-bot")
    print("👋 Logged out successfully")

    # Verify logout
    status = client.instance.connection_state("my-bot")
    if status.get('state') == 'close':
        print("✅ Logout confirmed")

except Exception as e:
    print(f"❌ Logout failed: {e}")
```

### Delete Instance

```python
# Delete instance (irreversible!)
def safe_delete_instance(instance_name):
    """Safely delete an instance with confirmation."""

    # Get current status first
    try:
        status = client.instance.connection_state(instance_name)
        print(f"📊 Current status: {status.get('state')}")
    except:
        print("⚠️ Cannot get instance status")

    # Confirm deletion
    confirm = input(f"❗ Delete '{instance_name}' permanently? (type 'DELETE' to confirm): ")

    if confirm == 'DELETE':
        try:
            response = client.instance.delete(instance_name)
            print(f"🗑️ Instance '{instance_name}' deleted")
            return True
        except Exception as e:
            print(f"❌ Deletion failed: {e}")
            return False
    else:
        print("❌ Deletion cancelled")
        return False

# Usage (use with caution!)
# success = safe_delete_instance("old-bot")
```

## Listing Instances

### Fetch All Instances

```python
# Get all instances
instances = client.instance.fetch_instances()

print(f"📋 Found {len(instances)} instances:")
for instance in instances:
    print(f"   • {instance.instance_name}")
    print(f"     Status: {getattr(instance, 'status', 'unknown')}")

    # Check connection state
    try:
        state = client.instance.connection_state(instance.instance_name)
        print(f"     Connection: {state.get('state', 'unknown')}")
    except:
        print(f"     Connection: error")

    print()  # Empty line between instances
```

### Instance Filtering and Management

```python
def manage_instances():
    """Advanced instance management."""

    instances = client.instance.fetch_instances()

    # Group by status
    connected = []
    disconnected = []
    unknown = []

    for instance in instances:
        try:
            state = client.instance.connection_state(instance.instance_name)
            connection_state = state.get('state', 'unknown')

            if connection_state == 'open':
                connected.append(instance.instance_name)
            elif connection_state == 'close':
                disconnected.append(instance.instance_name)
            else:
                unknown.append(instance.instance_name)

        except Exception:
            unknown.append(instance.instance_name)

    # Display summary
    print("📊 Instance Summary:")
    print(f"✅ Connected ({len(connected)}): {', '.join(connected)}")
    print(f"❌ Disconnected ({len(disconnected)}): {', '.join(disconnected)}")
    print(f"❓ Unknown ({len(unknown)}): {', '.join(unknown)}")

    return {
        'connected': connected,
        'disconnected': disconnected,
        'unknown': unknown,
        'total': len(instances)
    }

# Usage
summary = manage_instances()
```

## Advanced Instance Management

### Batch Operations

```python
def batch_create_instances(instance_names):
    """Create multiple instances in batch."""
    results = []

    for name in instance_names:
        try:
            print(f"🔧 Creating instance: {name}")
            instance = client.instance.create(name, qrcode=True)

            results.append({
                'name': name,
                'status': 'success',
                'has_qr': bool(instance.qrcode)
            })

            print(f"✅ Created: {name}")

        except Exception as e:
            results.append({
                'name': name,
                'status': 'failed',
                'error': str(e)
            })

            print(f"❌ Failed: {name} - {e}")

        # Small delay between creations
        import time
        time.sleep(2)

    return results

# Example usage
bot_names = ["support-bot", "sales-bot", "notifications-bot"]
results = batch_create_instances(bot_names)

# Summary
successful = [r for r in results if r['status'] == 'success']
print(f"\n📊 Batch Results: {len(successful)}/{len(bot_names)} successful")
```

### Instance Health Check

```python
def instance_health_check(instance_name):
    """Comprehensive health check for an instance."""

    health_report = {
        'instance_name': instance_name,
        'exists': False,
        'connection_state': None,
        'can_connect': False,
        'issues': []
    }

    try:
        # Check if instance exists
        instances = client.instance.fetch_instances()
        instance_names = [i.instance_name for i in instances]

        if instance_name not in instance_names:
            health_report['issues'].append("Instance does not exist")
            return health_report

        health_report['exists'] = True

        # Check connection state
        try:
            status = client.instance.connection_state(instance_name)
            state = status.get('state', 'unknown')
            health_report['connection_state'] = state

            if state == 'open':
                health_report['can_connect'] = True
            elif state == 'close':
                health_report['issues'].append("Instance disconnected")
            elif state == 'connecting':
                health_report['issues'].append("Connection in progress")
            else:
                health_report['issues'].append(f"Unknown state: {state}")

        except Exception as e:
            health_report['issues'].append(f"Cannot get connection state: {e}")

        # Try to get QR code if disconnected
        if health_report['connection_state'] == 'close':
            try:
                qr_data = client.instance.connect(instance_name)
                if qr_data.qrcode:
                    health_report['issues'].append("QR code available for reconnection")
                else:
                    health_report['issues'].append("Cannot generate QR code")
            except Exception as e:
                health_report['issues'].append(f"Cannot generate QR code: {e}")

    except Exception as e:
        health_report['issues'].append(f"Health check failed: {e}")

    return health_report

# Usage
health = instance_health_check("my-bot")

print(f"🏥 Health Check: {health['instance_name']}")
print(f"📊 Exists: {health['exists']}")
print(f"🔗 State: {health['connection_state']}")
print(f"✅ Ready: {health['can_connect']}")

if health['issues']:
    print("⚠️ Issues:")
    for issue in health['issues']:
        print(f"   • {issue}")
```

## Error Handling

### Common Instance Errors

```python
from pyevolutionapi.exceptions import (
    EvolutionAPIError,
    NotFoundError,
    ValidationError,
    AuthenticationError
)

def robust_instance_operation(operation, instance_name, **kwargs):
    """Perform instance operations with proper error handling."""

    try:
        if operation == 'create':
            return client.instance.create(instance_name, **kwargs)
        elif operation == 'connect':
            return client.instance.connect(instance_name, **kwargs)
        elif operation == 'status':
            return client.instance.connection_state(instance_name)
        elif operation == 'restart':
            return client.instance.restart(instance_name)
        elif operation == 'logout':
            return client.instance.logout(instance_name)
        elif operation == 'delete':
            return client.instance.delete(instance_name)
        else:
            raise ValueError(f"Unknown operation: {operation}")

    except NotFoundError:
        print(f"❌ Instance '{instance_name}' not found")
        print("💡 Tip: Create the instance first or check the name")
        return None

    except ValidationError as e:
        print(f"📝 Validation error: {e}")
        print("💡 Tip: Check instance name format (alphanumeric + hyphens)")
        return None

    except AuthenticationError:
        print(f"🔐 Authentication failed for '{instance_name}'")
        print("💡 Tip: Check API key and permissions")
        return None

    except EvolutionAPIError as e:
        print(f"🚫 API error: {e}")
        return None

    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return None

# Usage examples
result = robust_instance_operation('create', 'test-bot', qrcode=True)
result = robust_instance_operation('status', 'test-bot')
result = robust_instance_operation('restart', 'test-bot')
```

## Complete API Reference

### Method Signatures

```python
class InstanceResource:
    def create(
        self,
        instance_name: str,
        qrcode: bool = True,
        **kwargs: Any
    ) -> InstanceResponse:
        """Create a new WhatsApp instance."""

    def fetch_instances(
        self,
        instance_name: Optional[str] = None
    ) -> List[Instance]:
        """List all instances or get specific instance."""

    def connect(
        self,
        instance: str,
        number: Optional[str] = None
    ) -> InstanceResponse:
        """Connect instance and get QR code."""

    def restart(
        self,
        instance: str
    ) -> InstanceResponse:
        """Restart an instance."""

    def connection_state(
        self,
        instance: str
    ) -> Dict[str, Any]:
        """Get connection state of instance."""

    def set_presence(
        self,
        instance: str,
        presence: str
    ) -> Dict[str, Any]:
        """Set presence status."""

    def logout(
        self,
        instance: str
    ) -> InstanceResponse:
        """Logout from WhatsApp."""

    def delete(
        self,
        instance: str
    ) -> Dict[str, Any]:
        """Delete an instance permanently."""
```

### Data Models

```python
class Instance:
    """Instance information model."""
    instance_name: str
    status: str
    # Additional fields based on Evolution API response

class InstanceResponse:
    """Instance operation response model."""
    instance_name: str
    status: str
    qrcode: Optional[Dict[str, str]] = None

    @property
    def qr_code_base64(self) -> Optional[str]:
        """Get QR code in base64 format."""

class InstanceCreate:
    """Instance creation request model."""
    instance_name: str
    qrcode: bool = True
```

## Best Practices

### Instance Naming

```python
# ✅ Good instance names
"customer-support-bot"      # Descriptive, kebab-case
"sales-team-whatsapp"       # Clear purpose
"notification-service"      # Service-oriented
"user-12345-personal"       # User-specific with ID

# ❌ Avoid these patterns
"instance1"                 # Not descriptive
"My Bot"                    # Spaces
"PROD-BOT!!!"              # Special characters
"test test test"            # Repetition
```

### Production Considerations

```python
def production_instance_setup(instance_name):
    """Production-ready instance setup."""

    # 1. Create with error handling
    try:
        instance = client.instance.create(instance_name, qrcode=True)
        print(f"✅ Instance created: {instance_name}")
    except Exception as e:
        print(f"❌ Creation failed: {e}")
        return False

    # 2. Save QR code securely
    if instance.qr_code_base64:
        # Save to secure location, not public directory
        import base64
        from pathlib import Path

        secure_dir = Path("/secure/qr-codes")
        secure_dir.mkdir(exist_ok=True, mode=0o700)  # Restricted permissions

        qr_path = secure_dir / f"{instance_name}.png"
        qr_data = base64.b64decode(instance.qr_code_base64)
        qr_path.write_bytes(qr_data)
        qr_path.chmod(0o600)  # Read/write for owner only

        print(f"🔒 QR code saved securely: {qr_path}")

    # 3. Monitor connection with timeout
    connected = monitor_connection(instance_name, timeout=300)

    if connected:
        print(f"🎉 {instance_name} ready for production")
        return True
    else:
        print(f"❌ {instance_name} connection failed")
        return False

# Usage
success = production_instance_setup("production-whatsapp-bot")
```

### Monitoring and Alerts

```python
def setup_instance_monitoring(instance_names, check_interval=60):
    """Set up monitoring for multiple instances."""
    import time
    import threading

    def monitor_instance(instance_name):
        """Monitor single instance continuously."""

        while True:
            try:
                status = client.instance.connection_state(instance_name)
                state = status.get('state', 'unknown')

                if state != 'open':
                    print(f"🚨 ALERT: {instance_name} is {state}")

                    # Attempt reconnection
                    try:
                        client.instance.restart(instance_name)
                        print(f"🔄 Restarted {instance_name}")
                    except Exception as e:
                        print(f"❌ Restart failed for {instance_name}: {e}")

                else:
                    print(f"✅ {instance_name}: OK")

            except Exception as e:
                print(f"❌ Monitor error for {instance_name}: {e}")

            time.sleep(check_interval)

    # Start monitoring threads
    threads = []
    for instance_name in instance_names:
        thread = threading.Thread(target=monitor_instance, args=(instance_name,))
        thread.daemon = True  # Dies when main program exits
        thread.start()
        threads.append(thread)
        print(f"📊 Started monitoring: {instance_name}")

    return threads

# Usage (run in background)
# monitored_instances = ["bot1", "bot2", "bot3"]
# monitor_threads = setup_instance_monitoring(monitored_instances, check_interval=30)
```

## Next Steps

- **[Connecting Instances Guide](../getting-started/connecting.md)** - Detailed connection process
- **[Quick Start](../getting-started/quickstart.md)** - Get started quickly
- **[Message API](messages.md)** - Send messages once connected
- **[Examples](../examples/basic.md)** - Practical usage examples
