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

"""Basic tests for MCP (Model Control Protocol) framework."""

import unittest
import time
from unittest.mock import Mock, patch

from mcp.connector import HTTPConnector, MCPConnector
from mcp.server import MCPServer
from mcp.client import MCPClient
from mcp.config import MCPConfig


class TestMCPConnector(unittest.TestCase):
  """Test cases for MCP connector base class."""

  def test_connector_initialization(self):
    """Test connector initialization with valid parameters."""
    connector = HTTPConnector(
        endpoint='http://test.com',
        auth_token='test_token',
        timeout=60,
        max_retries=5
    )
    
    self.assertEqual(connector.endpoint, 'http://test.com')
    self.assertEqual(connector.auth_token, 'test_token')
    self.assertEqual(connector.timeout, 60)
    self.assertEqual(connector.max_retries, 5)
    self.assertFalse(connector.is_connected)

  def test_connector_abstract_methods(self):
    """Test that abstract methods raise NotImplementedError."""
    
    class TestConnector(MCPConnector):
      pass
    
    with self.assertRaises(TypeError):
      TestConnector('http://test.com')


class TestMCPServer(unittest.TestCase):
  """Test cases for MCP server."""

  def setUp(self):
    """Set up test server."""
    self.server = MCPServer(host='127.0.0.1', port=0)  # Port 0 for testing

  def test_server_initialization(self):
    """Test server initialization."""
    self.assertEqual(self.server.host, '127.0.0.1')
    self.assertEqual(self.server.port, 0)
    self.assertFalse(self.server.is_running)

  def test_model_registration(self):
    """Test model registration."""
    mock_model = Mock()
    mock_model.predict = Mock(return_value={'result': 'test'})
    
    self.server.register_model('test_model', mock_model)
    self.assertIn('test_model', self.server._models)
    self.assertEqual(self.server._models['test_model'], mock_model)

  def test_handler_registration(self):
    """Test handler registration."""
    def test_handler(params):
      return {'handled': True}
    
    self.server.register_handler('test_handler', test_handler)
    self.assertIn('test_handler', self.server._handlers)
    self.assertEqual(self.server._handlers['test_handler'], test_handler)


class TestMCPClient(unittest.TestCase):
  """Test cases for MCP client."""

  def setUp(self):
    """Set up test client."""
    with patch('mcp.connector.HTTPConnector'):
      self.client = MCPClient('http://test.com')

  def test_client_initialization(self):
    """Test client initialization."""
    self.assertEqual(self.client.endpoint, 'http://test.com')
    self.assertIsNotNone(self.client.connector)

  @patch('mcp.connector.HTTPConnector.connect')
  def test_client_connect(self, mock_connect):
    """Test client connection."""
    mock_connect.return_value = True
    
    result = self.client.connect()
    self.assertTrue(result)
    mock_connect.assert_called_once()


class TestMCPConfig(unittest.TestCase):
  """Test cases for MCP configuration."""

  def test_default_config(self):
    """Test default configuration loading."""
    with patch('os.path.exists', return_value=False):
      config = MCPConfig()
      
      server_config = config.get_server_config()
      self.assertIn('host', server_config)
      self.assertIn('port', server_config)
      
      client_config = config.get_client_config()
      self.assertIn('timeout', client_config)
      self.assertIn('connector_type', client_config)

  def test_config_updates(self):
    """Test configuration updates."""
    config = MCPConfig()
    
    config.update_config('server', {'host': '0.0.0.0'})
    self.assertEqual(config.get_server_config()['host'], '0.0.0.0')
    
    config.add_model_config('test_model', {'type': 'test'})
    model_config = config.get_model_config('test_model')
    self.assertEqual(model_config['type'], 'test')


class MockModel:
  """Mock model for testing."""
  
  def predict(self, input_data):
    return {'prediction': f'processed_{input_data}'}


class TestIntegration(unittest.TestCase):
  """Integration tests for MCP framework."""

  def setUp(self):
    """Set up integration test environment."""
    self.server = MCPServer(host='127.0.0.1', port=0, debug=False)
    self.mock_model = MockModel()
    self.server.register_model('test_model', self.mock_model)

  def test_model_prediction_workflow(self):
    """Test end-to-end model prediction workflow."""
    # This would require actual server startup for full integration
    # For now, test the components individually
    
    # Test model registration
    self.assertIn('test_model', self.server._models)
    
    # Test model functionality
    result = self.mock_model.predict('test_input')
    self.assertEqual(result['prediction'], 'processed_test_input')


if __name__ == '__main__':
  # Run tests
  unittest.main(verbosity=2)