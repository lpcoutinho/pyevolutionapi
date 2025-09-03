# Quick Start

Get up and running with PyEvolution in minutes.

## Basic Setup

```python
from pyevolutionapi import EvolutionClient

# Create client
client = EvolutionClient(
    base_url="http://localhost:8080",
    api_key="your-api-key"
)

# Create instance
instance = client.instance.create("my-bot", qrcode=True)
print(f"QR Code: {instance.qrcode}")

# Send message
response = client.messages.send_text(
    instance="my-bot",
    number="5511999999999", 
    text="Hello World!"
)
```

## Environment Variables

Create a `.env` file:

```bash
EVOLUTION_BASE_URL=http://localhost:8080
EVOLUTION_API_KEY=your-api-key
EVOLUTION_INSTANCE_NAME=my-bot
```