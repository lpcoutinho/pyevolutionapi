# PyEvolution

**Python client for Evolution API - WhatsApp integration made simple**

[![CI](https://github.com/lpcoutinho/pyevolution/workflows/CI/badge.svg)](https://github.com/lpcoutinho/pyevolution/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/lpcoutinho/pyevolution/branch/main/graph/badge.svg)](https://codecov.io/gh/lpcoutinho/pyevolution)
[![PyPI version](https://badge.fury.io/py/pyevolutionapi.svg)](https://badge.fury.io/py/pyevolutionapi)

PyEvolution is a modern, type-safe Python library that provides an intuitive interface to the Evolution API, making WhatsApp integration effortless for developers.

## Features

- 🎯 **Type-safe**: Complete type hints with Pydantic models
- 🔄 **Async/Sync**: Full support for both synchronous and asynchronous operations
- 🛡️ **Error Handling**: Comprehensive exception hierarchy with detailed error information
- 📱 **Complete API Coverage**: Support for messages, media, groups, instances, and more
- 🔧 **Easy Configuration**: Environment variables and multiple authentication methods
- 📚 **Well Documented**: Extensive documentation and examples
- ✅ **Tested**: Comprehensive test suite with high coverage
- 🔌 **Webhook Support**: Built-in webhook configuration and event handling

## Quick Start

### Installation

```bash
pip install pyevolutionapi
```

### Basic Example

```python
from pyevolutionapi import EvolutionClient

# Create client
client = EvolutionClient(
    base_url="http://localhost:8080",
    api_key="your-api-key-here"
)

# Create an instance
instance = client.instance.create(
    instance_name="my-whatsapp-bot",
    qrcode=True
)

# Send a message
response = client.messages.send_text(
    instance="my-whatsapp-bot",
    number="5511999999999",
    text="Hello from PyEvolution! 🚀"
)

print(f"Message sent! ID: {response.message_id}")
```

## Next Steps

- [Installation Guide](getting-started/installation.md)
- [Quick Start Tutorial](getting-started/quickstart.md)
- [API Reference](api/client.md)
- [Examples](examples/basic.md)

## Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/lpcoutinho/pyevolution/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/lpcoutinho/pyevolution/discussions)
- 📧 **Email**: your.email@example.com