# Model Control Protocol (MCP) for Google Research

This module provides a standardized way to connect to and interact with Google Research models remotely. It implements the Model Control Protocol (MCP) which enables distributed inference, training, and experimentation across different systems.

## Features

- **Remote Model Access**: Connect to research models hosted on remote servers
- **Multiple Connector Types**: Support for HTTP REST API and WebSocket connections
- **Authentication**: Secure connections with token-based authentication
- **Configuration Management**: Flexible configuration system with environment variable support
- **High-level Client API**: Easy-to-use client interface for model interactions
- **Server Framework**: Complete server implementation for hosting models remotely

## Quick Start

### 1. Basic Server Setup

```python
from mcp.server import MCPServer

# Create and configure server
server = MCPServer(host='127.0.0.1', port=8080)

# Register a model (any object with predict method)
server.register_model('my_model', your_model_instance)

# Start the server
server.start()
```

### 2. Basic Client Usage

```python
from mcp.client import MCPClient

# Connect to remote server
with MCPClient('http://127.0.0.1:8080') as client:
    # Make predictions
    result = client.predict('my_model', {'input': 'your data'})
    print(result)
```

## Installation

The MCP module requires the following dependencies:

```bash
pip install flask requests websocket-client
```

For development or testing:

```bash
pip install flask requests websocket-client pytest
```

## Detailed Usage

### Server Configuration

```python
from mcp.server import MCPServer
from mcp.config import MCPConfig

# Load configuration
config = MCPConfig('path/to/config.json')
server_config = config.get_server_config()

# Create server with configuration
server = MCPServer(**server_config)

# Register multiple models
server.register_model('bert_classifier', bert_model)
server.register_model('image_classifier', image_model)

# Register custom handlers
def custom_preprocessing(params):
    # Your custom logic here
    return processed_data

server.register_handler('preprocess', custom_preprocessing)

# Start server
server.start(threaded=True)
```

### Client Configuration

```python
from mcp.client import MCPClient
from mcp.config import MCPConfig

# Load configuration
config = MCPConfig()
client_config = config.get_client_config()

# Create client
client = MCPClient(
    endpoint='http://remote-server:8080',
    auth_token='your-auth-token',
    **client_config
)

# Connect and use
if client.connect():
    # List available models
    models = client.list_models()
    
    # Make predictions
    result = client.predict('bert_classifier', {
        'text': 'This is a sample sentence to classify'
    })
    
    # Batch predictions
    batch_results = client.batch_predict('image_classifier', [
        image1_data, image2_data, image3_data
    ])
    
    # Execute custom handlers
    processed = client.execute_handler('preprocess', {
        'data': raw_data,
        'params': preprocessing_params
    })

client.disconnect()
```

### Model Proxy Usage

```python
from mcp.client import MCPClient, MCPModelProxy

# Create client and connect
client = MCPClient('http://127.0.0.1:8080')
client.connect()

# Create proxy for specific model
model_proxy = MCPModelProxy(client, 'bert_classifier')

# Use proxy like a local model
result = model_proxy.predict('Input text here')
# or
result = model_proxy('Input text here')
```

### Configuration File Example

Create `mcp_config.json`:

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8080,
    "auth_token": "your-secure-token",
    "debug": false,
    "timeout": 60
  },
  "client": {
    "timeout": 30,
    "max_retries": 3,
    "connector_type": "http",
    "auth_token": "your-secure-token"
  },
  "models": {
    "bert_classifier": {
      "type": "transformer",
      "checkpoint_path": "/path/to/bert/checkpoint",
      "max_sequence_length": 512
    },
    "image_classifier": {
      "type": "cnn",
      "checkpoint_path": "/path/to/cnn/checkpoint",
      "input_size": [224, 224, 3]
    }
  },
  "logging": {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  }
}
```

### Environment Variables

You can also configure MCP using environment variables:

```bash
export MCP_SERVER_HOST=0.0.0.0
export MCP_SERVER_PORT=8080
export MCP_AUTH_TOKEN=your-secure-token
export MCP_CLIENT_TIMEOUT=30
export MCP_CONNECTOR_TYPE=http
```

## API Reference

### MCPServer

- `register_model(name, model)`: Register a model for remote access
- `register_handler(name, handler)`: Register a custom handler function
- `start(threaded=True)`: Start the server
- `stop()`: Stop the server

### MCPClient

- `connect()`: Connect to remote server
- `disconnect()`: Disconnect from server
- `health_check()`: Check server health
- `list_models()`: Get available models
- `predict(model_name, input_data)`: Make single prediction
- `batch_predict(model_name, input_batch)`: Make batch predictions
- `execute_handler(handler_name, params)`: Execute custom handler

### MCPConnector

Base class for connectors with implementations:
- `HTTPConnector`: REST API communication
- `WebSocketConnector`: Real-time WebSocket communication

## Integration with Google Research Models

### Example with TensorFlow Models

```python
import tensorflow as tf
from mcp.server import MCPServer

# Load your TensorFlow model
model = tf.keras.models.load_model('path/to/your/model')

# Wrap for MCP compatibility
class TFModelWrapper:
    def __init__(self, model):
        self.model = model
    
    def predict(self, input_data):
        # Convert input_data to appropriate format
        predictions = self.model.predict(input_data)
        return predictions.tolist()

# Register with MCP server
server = MCPServer()
server.register_model('tf_model', TFModelWrapper(model))
server.start()
```

### Example with JAX Models

```python
import jax
import jax.numpy as jnp
from mcp.server import MCPServer

# Your JAX model function
def jax_model_fn(params, x):
    # Your model implementation
    return predictions

# Wrap for MCP
class JAXModelWrapper:
    def __init__(self, model_fn, params):
        self.model_fn = model_fn
        self.params = params
    
    def predict(self, input_data):
        x = jnp.array(input_data)
        predictions = self.model_fn(self.params, x)
        return predictions.tolist()

# Register with MCP server
wrapper = JAXModelWrapper(jax_model_fn, trained_params)
server = MCPServer()
server.register_model('jax_model', wrapper)
server.start()
```

## Security Considerations

1. **Authentication**: Always use authentication tokens in production
2. **HTTPS**: Use HTTPS endpoints for secure communication
3. **Input Validation**: Validate all inputs on the server side
4. **Rate Limiting**: Implement rate limiting for production deployments
5. **Firewall**: Restrict access to MCP servers using firewall rules

## Monitoring and Logging

The MCP framework includes comprehensive logging:

```python
import logging
from mcp.server import MCPServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

server = MCPServer(debug=True)
# Server will now log all requests and responses
```

## Contributing

To contribute to the MCP framework:

1. Follow the existing code style and patterns
2. Add comprehensive tests for new features
3. Update documentation for any API changes
4. Ensure backward compatibility when possible

## License

This code is released under the Apache 2.0 license. See the LICENSE file for details.