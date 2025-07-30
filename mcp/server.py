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

"""MCP Server for hosting Google Research models remotely."""

import json
import logging
import threading
import time
from typing import Any, Callable, Dict, Optional

try:
  from flask import Flask, request, jsonify
  FLASK_AVAILABLE = True
except ImportError:
  FLASK_AVAILABLE = False
  Flask = None
  request = None
  jsonify = None


class MCPServer:
  """Model Control Protocol server for hosting research models.
  
  This server provides a standardized interface for remote access to
  Google Research models, enabling distributed inference and experimentation.
  """

  def __init__(self, 
               host: str = '127.0.0.1',
               port: int = 8080,
               auth_token: Optional[str] = None,
               debug: bool = False):
    """Initialize the MCP server.

    Args:
      host: Host address to bind the server to.
      port: Port number to listen on.
      auth_token: Optional authentication token for securing endpoints.
      debug: Whether to run in debug mode.
    """
    if not FLASK_AVAILABLE:
      raise ImportError("Flask is required for MCPServer. Install with: pip install flask")
      
    self.host = host
    self.port = port
    self.auth_token = auth_token
    self.debug = debug
    
    self.app = Flask(__name__)
    self.app.config['DEBUG'] = debug
    
    self._models = {}
    self._handlers = {}
    self._is_running = False
    
    self._setup_routes()

  def _setup_routes(self):
    """Set up the HTTP routes for the server."""
    
    @self.app.route('/health_check', methods=['GET', 'POST'])
    def health_check():
      """Health check endpoint."""
      return jsonify({'status': 'healthy', 'timestamp': time.time()})

    @self.app.route('/models', methods=['GET'])
    def list_models():
      """List available models."""
      if not self._authenticate(request):
        return jsonify({'error': 'Unauthorized'}), 401
      
      models_info = {}
      for name, model in self._models.items():
        models_info[name] = {
            'type': type(model).__name__,
            'loaded': True
        }
      return jsonify({'models': models_info})

    @self.app.route('/predict/<model_name>', methods=['POST'])
    def predict(model_name):
      """Make predictions using a specific model."""
      if not self._authenticate(request):
        return jsonify({'error': 'Unauthorized'}), 401
      
      if model_name not in self._models:
        return jsonify({'error': f'Model {model_name} not found'}), 404
      
      try:
        data = request.get_json()
        if 'input' not in data:
          return jsonify({'error': 'Missing input data'}), 400
        
        model = self._models[model_name]
        
        # Handle different model types
        if hasattr(model, 'predict'):
          result = model.predict(data['input'])
        elif hasattr(model, '__call__'):
          result = model(data['input'])
        else:
          return jsonify({'error': 'Model does not support prediction'}), 400
        
        return jsonify({
            'model': model_name,
            'prediction': result,
            'timestamp': time.time()
        })
        
      except Exception as e:
        logging.error(f"Prediction error for model {model_name}: {e}")
        return jsonify({'error': str(e)}), 500

    @self.app.route('/execute/<handler_name>', methods=['POST'])
    def execute_handler(handler_name):
      """Execute a custom handler function."""
      if not self._authenticate(request):
        return jsonify({'error': 'Unauthorized'}), 401
      
      if handler_name not in self._handlers:
        return jsonify({'error': f'Handler {handler_name} not found'}), 404
      
      try:
        data = request.get_json() or {}
        handler = self._handlers[handler_name]
        result = handler(data.get('params', {}))
        
        return jsonify({
            'handler': handler_name,
            'result': result,
            'timestamp': time.time()
        })
        
      except Exception as e:
        logging.error(f"Handler execution error for {handler_name}: {e}")
        return jsonify({'error': str(e)}), 500

  def _authenticate(self, req) -> bool:
    """Authenticate incoming requests."""
    if not self.auth_token:
      return True  # No authentication required
    
    auth_header = req.headers.get('Authorization')
    if not auth_header:
      return False
    
    try:
      scheme, token = auth_header.split(' ', 1)
      return scheme.lower() == 'bearer' and token == self.auth_token
    except ValueError:
      return False

  def register_model(self, name: str, model: Any) -> None:
    """Register a model for remote access.
    
    Args:
      name: Unique name for the model.
      model: The model object to register.
    """
    self._models[name] = model
    logging.info(f"Registered model: {name}")

  def register_handler(self, name: str, handler: Callable) -> None:
    """Register a custom handler function.
    
    Args:
      name: Unique name for the handler.
      handler: Function to handle custom requests.
    """
    self._handlers[name] = handler
    logging.info(f"Registered handler: {name}")

  def start(self, threaded: bool = True) -> None:
    """Start the MCP server.
    
    Args:
      threaded: Whether to run the server in a separate thread.
    """
    if self._is_running:
      logging.warning("Server is already running")
      return

    logging.info(f"Starting MCP server on {self.host}:{self.port}")
    
    if threaded:
      def run_server():
        self.app.run(
            host=self.host,
            port=self.port,
            debug=self.debug,
            threaded=True,
            use_reloader=False
        )
      
      server_thread = threading.Thread(target=run_server, daemon=True)
      server_thread.start()
      self._is_running = True
      
      # Give the server a moment to start
      time.sleep(1)
      logging.info("MCP server started in background thread")
      
    else:
      self._is_running = True
      self.app.run(
          host=self.host,
          port=self.port,
          debug=self.debug,
          threaded=True
      )

  def stop(self) -> None:
    """Stop the MCP server."""
    self._is_running = False
    logging.info("MCP server stopped")

  @property
  def is_running(self) -> bool:
    """Check if the server is currently running."""
    return self._is_running


# Example usage functions
def create_example_model():
  """Create a simple example model for demonstration."""
  class ExampleModel:
    def predict(self, input_data):
      # Simple echo model for demonstration
      return {
          'echo': input_data,
          'processed': True,
          'model_info': 'Google Research Example Model'
      }
  
  return ExampleModel()


def example_handler(params):
  """Example custom handler function."""
  return {
      'message': 'Handler executed successfully',
      'params_received': params,
      'server_time': time.time()
  }


if __name__ == '__main__':
  # Example server setup
  server = MCPServer(host='127.0.0.1', port=8080, debug=True)
  
  # Register an example model
  server.register_model('example', create_example_model())
  
  # Register an example handler
  server.register_handler('example_handler', example_handler)
  
  # Start the server
  server.start(threaded=False)