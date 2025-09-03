#!/usr/bin/env python3
"""
Message sending examples for PyEvolution.

This example demonstrates different types of messages:
1. Text messages
2. Media messages (image, video, document)
3. Audio messages
4. Location messages
5. Contact messages
6. Stickers and reactions
"""

import os
from pyevolutionapi import EvolutionClient


def text_messages_example(client: EvolutionClient, instance: str, number: str):
    """Examples of sending text messages."""
    print("📝 Text Messages:")
    
    # Simple text
    response = client.messages.send_text(
        instance=instance,
        number=number,
        text="Hello! This is a simple text message."
    )
    print(f"  ✅ Simple text sent: {response.message_id}")
    
    # Text with formatting
    response = client.messages.send_text(
        instance=instance,
        number=number,
        text="*Bold text*, _italic text_, ~strikethrough~, ```code```"
    )
    print(f"  ✅ Formatted text sent: {response.message_id}")
    
    # Text with mentions
    response = client.messages.send_text(
        instance=instance,
        number=number,
        text="Hello @everyone! This message mentions everyone.",
        mentions_everyone=True
    )
    print(f"  ✅ Text with mentions sent: {response.message_id}")


def media_messages_example(client: EvolutionClient, instance: str, number: str):
    """Examples of sending media messages."""
    print("🖼️ Media Messages:")
    
    # Send image
    response = client.messages.send_media(
        instance=instance,
        number=number,
        mediatype="image",
        media="https://picsum.photos/400/300",
        caption="This is a random image from Picsum! 📸"
    )
    print(f"  ✅ Image sent: {response.message_id}")
    
    # Send document
    response = client.messages.send_media(
        instance=instance,
        number=number,
        mediatype="document",
        media="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        caption="Sample PDF document",
        file_name="sample.pdf"
    )
    print(f"  ✅ Document sent: {response.message_id}")


def audio_messages_example(client: EvolutionClient, instance: str, number: str):
    """Examples of sending audio messages."""
    print("🎵 Audio Messages:")
    
    # Send audio message
    response = client.messages.send_audio(
        instance=instance,
        number=number,
        audio="https://www.soundjay.com/misc/sounds/bell-ringing-05.wav"
    )
    print(f"  ✅ Audio sent: {response.message_id}")


def location_messages_example(client: EvolutionClient, instance: str, number: str):
    """Examples of sending location messages."""
    print("📍 Location Messages:")
    
    # Send location
    response = client.messages.send_location(
        instance=instance,
        number=number,
        name="Times Square",
        address="Times Square, New York, NY, USA",
        latitude=40.7589,
        longitude=-73.9851
    )
    print(f"  ✅ Location sent: {response.message_id}")


def contact_messages_example(client: EvolutionClient, instance: str, number: str):
    """Examples of sending contact messages."""
    print("👤 Contact Messages:")
    
    # Send contact
    contacts = [
        {
            "fullName": "John Doe",
            "wuid": "5511999999999",
            "phoneNumber": "+55 11 99999-9999",
            "organization": "PyEvolution Demo",
            "email": "john.doe@example.com"
        }
    ]
    
    response = client.messages.send_contact(
        instance=instance,
        number=number,
        contacts=contacts
    )
    print(f"  ✅ Contact sent: {response.message_id}")


def interactive_messages_example(client: EvolutionClient, instance: str, number: str):
    """Examples of sending interactive messages."""
    print("🔘 Interactive Messages:")
    
    # Send poll
    response = client.messages.send_poll(
        instance=instance,
        number=number,
        name="What's your favorite programming language?",
        values=["Python", "JavaScript", "Go", "Rust", "Other"],
        selectable_count=1
    )
    print(f"  ✅ Poll sent: {response.message_id}")


def sticker_example(client: EvolutionClient, instance: str, number: str):
    """Examples of sending stickers."""
    print("😄 Stickers:")
    
    # Send sticker
    response = client.messages.send_sticker(
        instance=instance,
        number=number,
        sticker="https://github.com/WhatsApp/stickers/raw/main/Android/app/src/main/assets/1/01_Cuppy_smile.webp"
    )
    print(f"  ✅ Sticker sent: {response.message_id}")


def status_example(client: EvolutionClient, instance: str):
    """Examples of sending status/stories."""
    print("📱 Status/Stories:")
    
    # Send text status
    response = client.messages.send_status(
        instance=instance,
        type="text",
        content="Hello from PyEvolution! 🚀",
        all_contacts=True,
        background_color="#FF6B6B",
        font=1
    )
    print(f"  ✅ Text status sent: {response.message_id}")


def main():
    """Main example function."""
    # Configuration
    INSTANCE_NAME = "message-demo"
    RECIPIENT_NUMBER = "5511999999999"  # Replace with actual number
    
    # Create client
    client = EvolutionClient()
    
    try:
        print("PyEvolution Message Examples")
        print("=" * 40)
        
        # Check if instance exists, create if needed
        instances = client.instance.fetch_instances()
        instance_exists = any(inst.instance_name == INSTANCE_NAME for inst in instances)
        
        if not instance_exists:
            print(f"Creating instance '{INSTANCE_NAME}'...")
            client.instance.create(instance_name=INSTANCE_NAME, qrcode=True)
            print("⚠️  Please scan the QR code and connect WhatsApp first!")
            input("Press Enter after connecting...")
        
        # Check connection
        status = client.instance.connection_state(INSTANCE_NAME)
        print(f"Connection status: {status}")
        
        # Run examples
        text_messages_example(client, INSTANCE_NAME, RECIPIENT_NUMBER)
        media_messages_example(client, INSTANCE_NAME, RECIPIENT_NUMBER)
        audio_messages_example(client, INSTANCE_NAME, RECIPIENT_NUMBER)
        location_messages_example(client, INSTANCE_NAME, RECIPIENT_NUMBER)
        contact_messages_example(client, INSTANCE_NAME, RECIPIENT_NUMBER)
        interactive_messages_example(client, INSTANCE_NAME, RECIPIENT_NUMBER)
        sticker_example(client, INSTANCE_NAME, RECIPIENT_NUMBER)
        status_example(client, INSTANCE_NAME)
        
        print("\n✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    # Load environment variables
    if os.path.exists(".env"):
        from dotenv import load_dotenv
        load_dotenv()
    
    main()