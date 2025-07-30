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

"""MCP Client for connecting to remote Google Research models."""

import logging
import time
from typing import Any, Dict, List, Optional, Union

from mcp.connector import HTTPConnector, WebSocketConnector


class MCPClient:
  """Model Control Protocol client for accessing remote research models.
  
  This client provides a high-level interface for connecting to and
  interacting with remote Google Research models via MCP servers.
  """

  def __init__(self, 
               endpoint: str,
               auth_token: Optional[str] = None,
               connector_type: str = 'http',
               timeout: int = 30,
               max_retries: int = 3):
    """Initialize the MCP client.

    Args:
      endpoint: The remote endpoint URL for the MCP server.
      auth_token: Optional authentication token.
      connector_type: Type of connector ('http' or 'websocket').
      timeout: Connection timeout in seconds.
      max_retries: Maximum number of retry attempts.
    """
    self.endpoint = endpoint
    self.auth_token = auth_token
    self.timeout = timeout
    self.max_retries = max_retries
    
    # Initialize the appropriate connector
    if connector_type.lower() == 'websocket':
      self.connector = WebSocketConnector(
          endpoint=endpoint,
          auth_token=auth_token,
          timeout=timeout,
          max_retries=max_retries
      )
    else:
      self.connector = HTTPConnector(
          endpoint=endpoint,
          auth_token=auth_token,
          timeout=timeout,
          max_retries=max_retries
      )
    
    self._connected = False

  def connect(self) -> bool:
    """Connect to the remote MCP server.
    
    Returns:
      True if connection was successful, False otherwise.
    """
    try:
      self._connected = self.connector.connect()
      if self._connected:
        logging.info(f"Connected to MCP server at {self.endpoint}")
      else:
        logging.error(f"Failed to connect to MCP server at {self.endpoint}")
      return self._connected
    except Exception as e:
      logging.error(f"Connection error: {e}")
      return False

  def disconnect(self) -> None:
    """Disconnect from the remote MCP server."""
    if self.connector:
      self.connector.disconnect()
      self._connected = False
      logging.info("Disconnected from MCP server")

  def health_check(self) -> bool:
    """Check if the remote server is healthy.
    
    Returns:
      True if the server is healthy, False otherwise.
    """
    if not self._connected:
      logging.error("Not connected to MCP server")
      return False
    
    return self.connector.health_check()

  def list_models(self) -> Optional[Dict[str, Any]]:
    """Get a list of available models on the remote server.
    
    Returns:
      Dictionary containing model information, or None if request failed.
    """
    if not self._connected:
      logging.error("Not connected to MCP server")
      return None
    
    response = self.connector.send_request('models', {})
    return response

  def predict(self, 
              model_name: str, 
              input_data: Any,
              **kwargs) -> Optional[Dict[str, Any]]:
    """Make a prediction using a remote model.
    
    Args:
      model_name: Name of the model to use for prediction.
      input_data: Input data for the model.
      **kwargs: Additional parameters to pass to the model.
    
    Returns:
      Prediction result, or None if request failed.
    """
    if not self._connected:
      logging.error("Not connected to MCP server")
      return None
    
    params = {
        'input': input_data,
        **kwargs
    }
    
    response = self.connector.send_request(f'predict/{model_name}', params)
    return response

  def execute_handler(self, 
                      handler_name: str, 
                      params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """Execute a custom handler on the remote server.
    
    Args:
      handler_name: Name of the handler to execute.
      params: Parameters to pass to the handler.
    
    Returns:
      Handler result, or None if request failed.
    """
    if not self._connected:
      logging.error("Not connected to MCP server")
      return None
    
    request_params = {'params': params or {}}
    response = self.connector.send_request(f'execute/{handler_name}', request_params)
    return response

  def batch_predict(self, 
                    model_name: str, 
                    input_batch: List[Any],
                    **kwargs) -> List[Optional[Dict[str, Any]]]:
    """Make batch predictions using a remote model.
    
    Args:
      model_name: Name of the model to use for predictions.
      input_batch: List of input data for batch processing.
      **kwargs: Additional parameters to pass to the model.
    
    Returns:
      List of prediction results.
    """
    results = []
    for input_data in input_batch:
      result = self.predict(model_name, input_data, **kwargs)
      results.append(result)
    
    return results

  def stream_predictions(self, 
                         model_name: str, 
                         input_stream,
                         **kwargs):
    """Stream predictions from a remote model (generator function).
    
    Args:
      model_name: Name of the model to use for predictions.
      input_stream: Iterable of input data for streaming.
      **kwargs: Additional parameters to pass to the model.
    
    Yields:
      Prediction results as they become available.
    """
    for input_data in input_stream:
      result = self.predict(model_name, input_data, **kwargs)
      if result is not None:
        yield result

  @property
  def is_connected(self) -> bool:
    """Check if the client is currently connected."""
    return self._connected and self.connector.is_connected

  def __enter__(self):
    """Context manager entry."""
    self.connect()
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    """Context manager exit."""
    self.disconnect()


class MCPModelProxy:
  """Proxy class that makes remote models behave like local objects."""

  def __init__(self, client: MCPClient, model_name: str):
    """Initialize the model proxy.
    
    Args:
      client: Connected MCP client instance.
      model_name: Name of the remote model.
    """
    self.client = client
    self.model_name = model_name

  def predict(self, input_data: Any, **kwargs) -> Optional[Dict[str, Any]]:
    """Make a prediction using the remote model."""
    return self.client.predict(self.model_name, input_data, **kwargs)

  def __call__(self, input_data: Any, **kwargs) -> Optional[Dict[str, Any]]:
    """Allow the proxy to be called like a function."""
    return self.predict(input_data, **kwargs)


# Example usage
if __name__ == '__main__':
  # Example client usage
  with MCPClient('http://127.0.0.1:8080') as client:
    if client.is_connected:
      # Check server health
      if client.health_check():
        print("Server is healthy")
      
      # List available models
      models = client.list_models()
      if models:
        print(f"Available models: {models}")
      
      # Make a prediction
      result = client.predict('example', {'data': 'test input'})
      if result:
        print(f"Prediction result: {result}")
      
      # Execute a custom handler
      handler_result = client.execute_handler('example_handler', {'param1': 'value1'})
      if handler_result:
        print(f"Handler result: {handler_result}")
    
    else:
      print("Failed to connect to MCP server")