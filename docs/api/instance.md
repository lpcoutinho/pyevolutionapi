# Instance Management

## Overview

The InstanceResource provides methods for managing WhatsApp instances.

## Creating an Instance

```python
# Create a new instance with QR code
instance = client.instance.create(
    instance_name="my-bot",
    qrcode=True
)

print(f"QR Code: {instance.qrcode}")
```

## Instance Operations

```python
# Get connection status
status = client.instance.connection_state("my-bot")

# Connect to WhatsApp (get new QR code)
qr_data = client.instance.connect("my-bot")

# Restart instance
client.instance.restart("my-bot")

# Logout from WhatsApp
client.instance.logout("my-bot")

# Delete instance
client.instance.delete("my-bot")
```

## Available Methods

- `create()` - Create new instance
- `fetch_instances()` - List all instances
- `connect()` - Connect and get QR code
- `restart()` - Restart instance
- `connection_state()` - Check connection status
- `set_presence()` - Set online status
- `logout()` - Disconnect from WhatsApp
- `delete()` - Remove instance
