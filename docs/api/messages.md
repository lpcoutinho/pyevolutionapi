# Messages

## Overview

The MessageResource provides methods for sending different types of messages through the Evolution API.

## Basic Text Messages

```python
# Send a simple text message
response = client.messages.send_text(
    instance="my-bot",
    number="5511999999999",
    text="Hello, World!"
)
```

## Media Messages

```python
# Send an image
response = client.messages.send_media(
    instance="my-bot",
    number="5511999999999",
    mediatype="image",
    media="https://example.com/image.jpg",
    caption="Check out this image!"
)
```

## Available Methods

- `send_text()` - Send text messages
- `send_media()` - Send images, videos, documents
- `send_audio()` - Send audio messages
- `send_location()` - Send location coordinates
- `send_contact()` - Send contact information
- `send_reaction()` - React to messages
- `send_sticker()` - Send stickers
- `send_poll()` - Create polls
- `send_status()` - Post to status/story
