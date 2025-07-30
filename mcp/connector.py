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

"""MCP Connector base class for remote model access."""

import abc
import json
import logging
from typing import Any, Dict, Optional, Union
import six


class MCPConnector(six.with_metaclass(abc.ABCMeta)):
  """Base class for Model Control Protocol connectors.
  
  This class provides a standardized interface for connecting remote systems
  to Google Research models, enabling distributed inference, training, and
  experimentation.
  """

  def __init__(self, 
               endpoint: str,
               auth_token: Optional[str] = None,
               timeout: int = 30,
               max_retries: int = 3):
    """Initialize the MCP connector.

    Args:
      endpoint: The remote endpoint URL for the model service.
      auth_token: Optional authentication token for secure connections.
      timeout: Connection timeout in seconds.
      max_retries: Maximum number of connection retry attempts.
    """
    self.endpoint = endpoint
    self.auth_token = auth_token
    self.timeout = timeout
    self.max_retries = max_retries
    self._connection = None
    self._is_connected = False

  @abc.abstractmethod
  def connect(self) -> bool:
    """Establish connection to the remote model service.
    
    Returns:
      True if connection was successful, False otherwise.
    """
    pass

  @abc.abstractmethod
  def disconnect(self) -> None:
    """Close the connection to the remote model service."""
    pass

  @abc.abstractmethod
  def send_request(self, 
                   method: str, 
                   params: Dict[str, Any]) -> Union[Dict[str, Any], None]:
    """Send a request to the remote model service.
    
    Args:
      method: The method name to call on the remote service.
      params: Parameters to pass to the remote method.
      
    Returns:
      Response from the remote service, or None if request failed.
    """
    pass

  @property
  def is_connected(self) -> bool:
    """Check if the connector is currently connected."""
    return self._is_connected

  def health_check(self) -> bool:
    """Perform a health check on the remote service.
    
    Returns:
      True if the service is healthy, False otherwise.
    """
    try:
      response = self.send_request('health_check', {})
      return response is not None and response.get('status') == 'healthy'
    except Exception as e:
      logging.warning(f"Health check failed: {e}")
      return False


class HTTPConnector(MCPConnector):
  """HTTP-based MCP connector for REST API communication."""

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._session = None

  def connect(self) -> bool:
    """Establish HTTP connection to the remote service."""
    try:
      import requests
      self._session = requests.Session()
      
      if self.auth_token:
        self._session.headers.update({
            'Authorization': f'Bearer {self.auth_token}',
            'Content-Type': 'application/json'
        })
      
      # Test connection with health check
      self._is_connected = self.health_check()
      return self._is_connected
      
    except ImportError:
      logging.error("requests library not available for HTTP connector")
      return False
    except Exception as e:
      logging.error(f"Failed to establish HTTP connection: {e}")
      return False

  def disconnect(self) -> None:
    """Close the HTTP session."""
    if self._session:
      self._session.close()
      self._session = None
    self._is_connected = False

  def send_request(self, 
                   method: str, 
                   params: Dict[str, Any]) -> Union[Dict[str, Any], None]:
    """Send HTTP POST request to the remote service."""
    if not self._session or not self._is_connected:
      logging.error("Not connected to remote service")
      return None

    try:
      url = f"{self.endpoint}/{method}"
      response = self._session.post(
          url, 
          json=params, 
          timeout=self.timeout
      )
      response.raise_for_status()
      return response.json()
      
    except Exception as e:
      logging.error(f"HTTP request failed: {e}")
      return None


class WebSocketConnector(MCPConnector):
  """WebSocket-based MCP connector for real-time communication."""

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._websocket = None

  def connect(self) -> bool:
    """Establish WebSocket connection to the remote service."""
    try:
      import websocket
      
      def on_open(ws):
        logging.info("WebSocket connection established")
        self._is_connected = True

      def on_close(ws, close_status_code, close_msg):
        logging.info("WebSocket connection closed")
        self._is_connected = False

      def on_error(ws, error):
        logging.error(f"WebSocket error: {error}")
        self._is_connected = False

      headers = {}
      if self.auth_token:
        headers['Authorization'] = f'Bearer {self.auth_token}'

      self._websocket = websocket.WebSocketApp(
          self.endpoint,
          header=headers,
          on_open=on_open,
          on_close=on_close,
          on_error=on_error
      )
      
      # Start connection in a separate thread
      import threading
      def run_websocket():
        self._websocket.run_forever()
      
      ws_thread = threading.Thread(target=run_websocket, daemon=True)
      ws_thread.start()
      
      # Wait for connection
      import time
      for _ in range(self.timeout):
        if self._is_connected:
          return True
        time.sleep(1)
      
      return False
      
    except ImportError:
      logging.error("websocket-client library not available")
      return False
    except Exception as e:
      logging.error(f"Failed to establish WebSocket connection: {e}")
      return False

  def disconnect(self) -> None:
    """Close the WebSocket connection."""
    if self._websocket:
      self._websocket.close()
      self._websocket = None
    self._is_connected = False

  def send_request(self, 
                   method: str, 
                   params: Dict[str, Any]) -> Union[Dict[str, Any], None]:
    """Send request over WebSocket connection."""
    if not self._websocket or not self._is_connected:
      logging.error("WebSocket not connected")
      return None

    try:
      request = {
          'method': method,
          'params': params,
          'id': id(request)  # Simple request ID
      }
      
      self._websocket.send(json.dumps(request))
      
      # For simplicity, we'll use HTTP connector pattern here
      # In a real implementation, you'd handle async responses
      logging.info(f"Sent WebSocket request: {method}")
      return {'status': 'sent'}
      
    except Exception as e:
      logging.error(f"WebSocket request failed: {e}")
      return None