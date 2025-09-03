# Configuration

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EVOLUTION_BASE_URL` | Yes | - | Evolution API base URL |
| `EVOLUTION_API_KEY` | Yes | - | Global API key |
| `EVOLUTION_INSTANCE_NAME` | No | - | Default instance name |
| `EVOLUTION_DEBUG` | No | `false` | Enable debug logging |
| `EVOLUTION_REQUEST_TIMEOUT` | No | `30` | Request timeout in seconds |
| `EVOLUTION_MAX_RETRIES` | No | `3` | Maximum retry attempts |

## Client Configuration

```python
from pyevolutionapi import EvolutionClient

client = EvolutionClient(
    base_url="http://localhost:8080",
    api_key="your-api-key",
    default_instance="my-instance",
    timeout=60.0,
    max_retries=5,
    debug=True
)
```