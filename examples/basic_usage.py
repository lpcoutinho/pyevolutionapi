#!/usr/bin/env python3
"""
Basic usage example for PyEvolution.

This example demonstrates:
1. Creating a client
2. Creating an instance
3. Connecting to WhatsApp
4. Sending messages
"""

import os
import asyncio
from pyevolutionapi import EvolutionClient


def basic_example():
    """Basic synchronous example."""
    # Create client
    client = EvolutionClient(
        base_url="http://localhost:8080",
        api_key="your-api-key-here"  # Replace with your actual API key
    )
    
    try:
        # Create an instance
        print("Creating instance...")
        instance_response = client.instance.create(
            instance_name="my-whatsapp-bot",
            qrcode=True
        )
        
        if instance_response.qr_code_base64:
            print("QR Code generated! Scan it with your WhatsApp.")
            print(f"QR Code (base64): {instance_response.qr_code_base64[:50]}...")
        
        # Check connection status
        print("Checking connection status...")
        status = client.instance.connection_state("my-whatsapp-bot")
        print(f"Connection status: {status}")
        
        # Send a text message (make sure WhatsApp is connected first)
        print("Sending test message...")
        message_response = client.messages.send_text(
            instance="my-whatsapp-bot",
            number="5511999999999",  # Replace with actual phone number
            text="Hello from PyEvolution! 🚀"
        )
        
        if message_response.is_success:
            print(f"Message sent successfully! ID: {message_response.message_id}")
        else:
            print("Failed to send message")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        client.close()


async def async_example():
    """Async example."""
    client = EvolutionClient(
        base_url="http://localhost:8080",
        api_key="your-api-key-here"
    )
    
    try:
        async with client:  # Use as async context manager
            # Create instance
            instance_response = await client.instance.acreate(
                instance_name="async-bot",
                qrcode=True
            )
            
            print(f"Instance created: {instance_response.instance.instance_name}")
            
            # Send multiple messages concurrently
            tasks = [
                client.messages.asend_text(
                    instance="async-bot",
                    number="5511999999999",
                    text=f"Async message {i}"
                )
                for i in range(1, 4)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results, 1):
                if isinstance(result, Exception):
                    print(f"Message {i} failed: {result}")
                else:
                    print(f"Message {i} sent: {result.message_id}")
                    
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("PyEvolution Basic Usage Example")
    print("=" * 40)
    
    # Load environment variables if available
    if os.path.exists(".env"):
        from dotenv import load_dotenv
        load_dotenv()
    
    # Run synchronous example
    print("\n1. Synchronous Example:")
    print("-" * 20)
    basic_example()
    
    # Run async example
    print("\n2. Asynchronous Example:")
    print("-" * 20)
    asyncio.run(async_example())
    
    print("\nDone!")