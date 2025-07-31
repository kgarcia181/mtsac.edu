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

"""Example usage of the MCP (Model Control Protocol) framework.

This script demonstrates how to set up an MCP server with example models
and connect to it using an MCP client.
"""

import time
import threading
import logging
from typing import Any, Dict

from mcp.server import MCPServer
from mcp.client import MCPClient


# Example models for demonstration
class EchoModel:
  """Simple echo model that returns the input."""
  
  def predict(self, input_data: Any) -> Dict[str, Any]:
    return {
        'echo': input_data,
        'timestamp': time.time(),
        'model_type': 'echo'
    }


class MathModel:
  """Simple math model for basic calculations."""
  
  def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
    operation = input_data.get('operation', 'add')
    a = input_data.get('a', 0)
    b = input_data.get('b', 0)
    
    if operation == 'add':
      result = a + b
    elif operation == 'subtract':
      result = a - b
    elif operation == 'multiply':
      result = a * b
    elif operation == 'divide':
      result = a / b if b != 0 else float('inf')
    else:
      result = 0
    
    return {
        'operation': operation,
        'operands': [a, b],
        'result': result,
        'timestamp': time.time()
    }


def example_handler(params: Dict[str, Any]) -> Dict[str, Any]:
  """Example custom handler function."""
  return {
      'message': f"Handler received: {params}",
      'processed_at': time.time(),
      'handler_name': 'example_handler'
  }


def start_example_server(port: int = 8080) -> MCPServer:
  """Start an example MCP server with demo models."""
  
  # Configure logging
  logging.basicConfig(level=logging.INFO)
  
  # Create server
  server = MCPServer(host='127.0.0.1', port=port, debug=True)
  
  # Register example models
  server.register_model('echo', EchoModel())
  server.register_model('math', MathModel())
  
  # Register example handler
  server.register_handler('example_handler', example_handler)
  
  # Start server in background thread
  server.start(threaded=True)
  
  print(f"MCP server started on http://127.0.0.1:{port}")
  print("Available models: echo, math")
  print("Available handlers: example_handler")
  
  return server


def run_example_client(server_port: int = 8080):
  """Run example client interactions with the MCP server."""
  
  endpoint = f'http://127.0.0.1:{server_port}'
  
  print(f"\nConnecting to MCP server at {endpoint}")
  
  # Create and connect client
  with MCPClient(endpoint) as client:
    if not client.is_connected:
      print("Failed to connect to MCP server")
      return
    
    print("✓ Connected to MCP server")
    
    # Check server health
    if client.health_check():
      print("✓ Server health check passed")
    
    # List available models
    models = client.list_models()
    if models:
      print(f"✓ Available models: {list(models.get('models', {}).keys())}")
    
    # Test echo model
    print("\n--- Testing Echo Model ---")
    echo_result = client.predict('echo', {'message': 'Hello, MCP!'})
    if echo_result:
      print(f"Echo result: {echo_result}")
    
    # Test math model
    print("\n--- Testing Math Model ---")
    math_operations = [
        {'operation': 'add', 'a': 10, 'b': 5},
        {'operation': 'subtract', 'a': 10, 'b': 5},
        {'operation': 'multiply', 'a': 10, 'b': 5},
        {'operation': 'divide', 'a': 10, 'b': 2}
    ]
    
    for op in math_operations:
      result = client.predict('math', op)
      if result:
        print(f"{op['a']} {op['operation']} {op['b']} = {result['result']}")
    
    # Test batch predictions
    print("\n--- Testing Batch Predictions ---")
    batch_inputs = [
        {'message': 'First message'},
        {'message': 'Second message'},
        {'message': 'Third message'}
    ]
    
    batch_results = client.batch_predict('echo', batch_inputs)
    for i, result in enumerate(batch_results):
      if result:
        print(f"Batch {i+1}: {result['echo']['message']}")
    
    # Test custom handler
    print("\n--- Testing Custom Handler ---")
    handler_result = client.execute_handler('example_handler', {
        'param1': 'value1',
        'param2': 42
    })
    if handler_result:
      print(f"Handler result: {handler_result}")
    
    print("\n✓ All tests completed successfully")


def main():
  """Main function to run the complete example."""
  
  print("=== MCP Framework Example ===")
  
  # Start the server
  server = start_example_server(port=8080)
  
  # Give server time to start
  time.sleep(2)
  
  try:
    # Run client examples
    run_example_client(server_port=8080)
    
  except KeyboardInterrupt:
    print("\nReceived interrupt signal")
  
  finally:
    # Clean up
    print("\nStopping MCP server...")
    server.stop()
    print("Example completed")


if __name__ == '__main__':
  main()