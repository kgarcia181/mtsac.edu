# MCP Connector Quick Start Guide

This guide helps you get started with the Model Control Protocol (MCP) connector for Google Research models.

## Installation

1. **Basic Installation (demo mode only):**
   ```bash
   # No additional dependencies required for demo
   python -c "import mcp; mcp.demo_mcp()"
   ```

2. **Full Installation (with web server capabilities):**
   ```bash
   pip install -r mcp/requirements.txt
   ```

## Quick Start Examples

### 1. Run the Demo

```python
import mcp

# Run the complete demo
mcp.demo_mcp()
```

### 2. Basic Model Registration and Usage

```python
from mcp.demo import SimpleMCPDemo, SimpleModel

# Create demo instance
demo = SimpleMCPDemo()

# Register a model
model = SimpleModel('my_classifier')
demo.register_model('classifier', model)

# Make predictions
result = demo.predict('classifier', {'text': 'Hello World'})
print(result)
```

### 3. Custom Handler Registration

```python
from mcp.demo import SimpleMCPDemo

demo = SimpleMCPDemo()

# Define custom handler
def preprocess_text(params):
    text = params.get('text', '')
    return {
        'cleaned_text': text.strip().lower(),
        'word_count': len(text.split()),
        'char_count': len(text)
    }

# Register handler
demo.register_handler('preprocess', preprocess_text)

# Use handler
result = demo.execute_handler('preprocess', {'text': '  Hello World!  '})
print(result)
```

### 4. Configuration Management

```python
from mcp.config import MCPConfig

# Create configuration
config = MCPConfig()

# Add model configuration
config.add_model_config('bert_model', {
    'type': 'transformer',
    'checkpoint_path': '/path/to/bert',
    'max_length': 512
})

# Get configuration
model_config = config.get_model_config('bert_model')
print(model_config)
```

### 5. Full Server/Client Setup (requires Flask/requests)

```python
# Server setup
from mcp.server import MCPServer

server = MCPServer(host='127.0.0.1', port=8080)
server.register_model('my_model', your_model_instance)
server.start(threaded=True)

# Client usage
from mcp.client import MCPClient

with MCPClient('http://127.0.0.1:8080') as client:
    result = client.predict('my_model', {'input': 'data'})
    print(result)
```

## Integration with Google Research Models

### TensorFlow Integration

```python
import tensorflow as tf
from mcp.demo import SimpleMCPDemo

# Load your TensorFlow model
tf_model = tf.keras.models.load_model('path/to/model')

# Create wrapper
class TFModelWrapper:
    def __init__(self, model):
        self.model = model
    
    def predict(self, input_data):
        # Convert and predict
        predictions = self.model.predict(input_data)
        return {'predictions': predictions.tolist()}

# Register with MCP
demo = SimpleMCPDemo()
demo.register_model('tf_classifier', TFModelWrapper(tf_model))

# Use model
result = demo.predict('tf_classifier', input_array)
```

### JAX Integration

```python
import jax.numpy as jnp
from mcp.demo import SimpleMCPDemo

# Your JAX model
def jax_predict(params, x):
    # Your model logic here
    return predictions

# Create wrapper
class JAXModelWrapper:
    def __init__(self, predict_fn, params):
        self.predict_fn = predict_fn
        self.params = params
    
    def predict(self, input_data):
        x = jnp.array(input_data)
        predictions = self.predict_fn(self.params, x)
        return {'predictions': predictions.tolist()}

# Register with MCP
demo = SimpleMCPDemo()
demo.register_model('jax_model', JAXModelWrapper(jax_predict, trained_params))
```

## Testing Your Implementation

Run the test suite:

```bash
python -m unittest mcp.test_simple_mcp -v
```

## Next Steps

1. **Explore the full API**: Check `mcp/README.md` for comprehensive documentation
2. **Add authentication**: Use auth tokens for secure remote access
3. **Scale up**: Deploy servers with proper web frameworks for production use
4. **Monitor**: Add logging and monitoring for production deployments

## Troubleshooting

**Import errors with full MCP features:**
- Install dependencies: `pip install flask requests websocket-client`
- Use demo mode for testing: `import mcp; mcp.demo_mcp()`

**Model not found errors:**
- Ensure models are registered before use
- Check model names match exactly

**Connection issues:**
- Verify server is running and accessible
- Check firewall and network settings
- Confirm correct endpoint URLs

For more help, see the full documentation in `mcp/README.md`.