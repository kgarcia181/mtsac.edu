# coding=utf-8
# Copyright 2023 The Google Research Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Simple demo of MCP connector without external dependencies."""

import json
import logging
import time
from typing import Any, Dict, Optional

# Simple demo versions that don't require external libraries


class SimpleMCPConnector:
  """Simple MCP connector for demonstration purposes."""

  def __init__(self, endpoint: str, auth_token: Optional[str] = None):
    """Initialize the simple connector."""
    self.endpoint = endpoint
    self.auth_token = auth_token
    self._is_connected = False

  def connect(self) -> bool:
    """Simulate connection."""
    logging.info(f"Connecting to {self.endpoint}")
    self._is_connected = True
    return True

  def disconnect(self) -> None:
    """Simulate disconnection."""
    self._is_connected = False

  def send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Simulate sending a request."""
    if not self._is_connected:
      return {'error': 'Not connected'}
    
    return {
        'method': method,
        'params': params,
        'timestamp': time.time(),
        'status': 'simulated'
    }

  @property
  def is_connected(self) -> bool:
    """Check connection status."""
    return self._is_connected


class SimpleModel:
  """Simple model for demonstration."""
  
  def __init__(self, name: str):
    self.name = name
  
  def predict(self, input_data: Any) -> Dict[str, Any]:
    """Make a simple prediction."""
    return {
        'model': self.name,
        'input': input_data,
        'prediction': f"processed_{input_data}",
        'timestamp': time.time()
    }


class SimpleMCPDemo:
  """Simple demonstration of MCP concepts."""
  
  def __init__(self):
    self.models = {}
    self.handlers = {}
  
  def register_model(self, name: str, model: Any) -> None:
    """Register a model."""
    self.models[name] = model
    logging.info(f"Registered model: {name}")
  
  def register_handler(self, name: str, handler) -> None:
    """Register a handler."""
    self.handlers[name] = handler
    logging.info(f"Registered handler: {name}")
  
  def predict(self, model_name: str, input_data: Any) -> Optional[Dict[str, Any]]:
    """Make a prediction."""
    if model_name not in self.models:
      return {'error': f'Model {model_name} not found'}
    
    model = self.models[model_name]
    return model.predict(input_data)
  
  def execute_handler(self, handler_name: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Execute a handler."""
    if handler_name not in self.handlers:
      return {'error': f'Handler {handler_name} not found'}
    
    handler = self.handlers[handler_name]
    return handler(params)
  
  def list_models(self) -> Dict[str, Any]:
    """List available models."""
    return {
        'models': {name: {'type': type(model).__name__} for name, model in self.models.items()}
    }


def demo_mcp():
  """Run a simple MCP demonstration."""
  
  # Configure logging
  logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
  
  print("=== Simple MCP Framework Demo ===\n")
  
  # Create demo instance
  demo = SimpleMCPDemo()
  
  # Register models
  demo.register_model('echo', SimpleModel('echo'))
  demo.register_model('classifier', SimpleModel('classifier'))
  
  # Register handler
  def sample_handler(params):
    return {'handler_result': f"Processed {params}", 'timestamp': time.time()}
  
  demo.register_handler('sample_handler', sample_handler)
  
  # Demonstrate functionality
  print("1. List available models:")
  models = demo.list_models()
  print(f"   {json.dumps(models, indent=2)}")
  
  print("\n2. Make predictions:")
  result1 = demo.predict('echo', {'text': 'Hello, MCP!'})
  print(f"   Echo model: {json.dumps(result1, indent=2)}")
  
  result2 = demo.predict('classifier', {'data': [1, 2, 3, 4, 5]})
  print(f"   Classifier model: {json.dumps(result2, indent=2)}")
  
  print("\n3. Execute handler:")
  handler_result = demo.execute_handler('sample_handler', {'param1': 'value1'})
  print(f"   Handler result: {json.dumps(handler_result, indent=2)}")
  
  print("\n4. Test connector:")
  connector = SimpleMCPConnector('http://example.com:8080', 'demo_token')
  connector.connect()
  response = connector.send_request('health_check', {})
  print(f"   Connector response: {json.dumps(response, indent=2)}")
  connector.disconnect()
  
  print("\n✓ Demo completed successfully!")


if __name__ == '__main__':
  demo_mcp()