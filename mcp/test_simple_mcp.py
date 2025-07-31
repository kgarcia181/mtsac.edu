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

"""Simple tests for MCP framework core functionality."""

import unittest
import time
from mcp.demo import SimpleMCPConnector, SimpleModel, SimpleMCPDemo


class TestSimpleMCP(unittest.TestCase):
  """Test cases for simple MCP implementation."""

  def test_simple_connector(self):
    """Test simple connector functionality."""
    connector = SimpleMCPConnector('http://test.com')
    
    # Test initial state
    self.assertFalse(connector.is_connected)
    
    # Test connection
    result = connector.connect()
    self.assertTrue(result)
    self.assertTrue(connector.is_connected)
    
    # Test request
    response = connector.send_request('test_method', {'param': 'value'})
    self.assertIn('method', response)
    self.assertEqual(response['method'], 'test_method')
    
    # Test disconnection
    connector.disconnect()
    self.assertFalse(connector.is_connected)

  def test_simple_model(self):
    """Test simple model functionality."""
    model = SimpleModel('test_model')
    
    result = model.predict({'input': 'test_data'})
    
    self.assertIn('model', result)
    self.assertIn('input', result)
    self.assertIn('prediction', result)
    self.assertIn('timestamp', result)
    
    self.assertEqual(result['model'], 'test_model')
    self.assertEqual(result['input'], {'input': 'test_data'})

  def test_simple_mcp_demo(self):
    """Test simple MCP demo functionality."""
    demo = SimpleMCPDemo()
    
    # Test model registration
    model = SimpleModel('test')
    demo.register_model('test_model', model)
    self.assertIn('test_model', demo.models)
    
    # Test handler registration
    def test_handler(params):
      return {'result': 'success'}
    
    demo.register_handler('test_handler', test_handler)
    self.assertIn('test_handler', demo.handlers)
    
    # Test model listing
    models = demo.list_models()
    self.assertIn('models', models)
    self.assertIn('test_model', models['models'])
    
    # Test prediction
    result = demo.predict('test_model', 'test_input')
    self.assertIsNotNone(result)
    self.assertEqual(result['model'], 'test')
    
    # Test handler execution
    handler_result = demo.execute_handler('test_handler', {'param': 'value'})
    self.assertIsNotNone(handler_result)
    self.assertEqual(handler_result['result'], 'success')
    
    # Test error cases
    error_result = demo.predict('nonexistent_model', 'input')
    self.assertIn('error', error_result)
    
    error_handler = demo.execute_handler('nonexistent_handler', {})
    self.assertIn('error', error_handler)


class TestMCPIntegration(unittest.TestCase):
  """Integration tests for MCP framework."""

  def test_end_to_end_workflow(self):
    """Test a complete workflow with connector and demo."""
    # Set up demo
    demo = SimpleMCPDemo()
    model = SimpleModel('integration_test')
    demo.register_model('test_model', model)
    
    def integration_handler(params):
      return {'processed': True, 'input_count': len(params)}
    
    demo.register_handler('integration_handler', integration_handler)
    
    # Set up connector
    connector = SimpleMCPConnector('http://integration.test')
    connector.connect()
    
    # Test workflow
    self.assertTrue(connector.is_connected)
    
    # Simulate client-server interaction
    models_response = demo.list_models()
    self.assertIn('test_model', models_response['models'])
    
    prediction_response = demo.predict('test_model', {'data': 'integration_test'})
    self.assertEqual(prediction_response['model'], 'integration_test')
    
    handler_response = demo.execute_handler('integration_handler', {'a': 1, 'b': 2})
    self.assertTrue(handler_response['processed'])
    self.assertEqual(handler_response['input_count'], 2)
    
    # Clean up
    connector.disconnect()
    self.assertFalse(connector.is_connected)


if __name__ == '__main__':
    unittest.main(verbosity=2)