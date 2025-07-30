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

"""Configuration utilities for MCP (Model Control Protocol)."""

import json
import os
from typing import Any, Dict, Optional


class MCPConfig:
  """Configuration management for MCP servers and clients."""

  def __init__(self, config_path: Optional[str] = None):
    """Initialize MCP configuration.
    
    Args:
      config_path: Path to configuration file. If None, uses default locations.
    """
    self.config_path = config_path or self._find_config_file()
    self.config = self._load_config()

  def _find_config_file(self) -> Optional[str]:
    """Find configuration file in default locations."""
    possible_paths = [
        'mcp_config.json',
        '~/.mcp/config.json',
        '/etc/mcp/config.json',
        os.environ.get('MCP_CONFIG_PATH', '')
    ]
    
    for path in possible_paths:
      if path and os.path.exists(os.path.expanduser(path)):
        return os.path.expanduser(path)
    
    return None

  def _load_config(self) -> Dict[str, Any]:
    """Load configuration from file or use defaults."""
    default_config = {
        'server': {
            'host': '127.0.0.1',
            'port': 8080,
            'auth_token': None,
            'debug': False,
            'timeout': 30,
            'max_workers': 4
        },
        'client': {
            'timeout': 30,
            'max_retries': 3,
            'connector_type': 'http',
            'auth_token': None
        },
        'models': {},
        'logging': {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    }
    
    if not self.config_path or not os.path.exists(self.config_path):
      return default_config
    
    try:
      with open(self.config_path, 'r') as f:
        file_config = json.load(f)
      
      # Merge with defaults
      merged_config = default_config.copy()
      for section, values in file_config.items():
        if section in merged_config and isinstance(values, dict):
          merged_config[section].update(values)
        else:
          merged_config[section] = values
      
      return merged_config
      
    except (json.JSONDecodeError, IOError) as e:
      print(f"Warning: Could not load config from {self.config_path}: {e}")
      return default_config

  def get_server_config(self) -> Dict[str, Any]:
    """Get server configuration."""
    return self.config.get('server', {})

  def get_client_config(self) -> Dict[str, Any]:
    """Get client configuration."""
    return self.config.get('client', {})

  def get_model_config(self, model_name: str) -> Dict[str, Any]:
    """Get configuration for a specific model."""
    return self.config.get('models', {}).get(model_name, {})

  def save_config(self, config_path: Optional[str] = None) -> None:
    """Save current configuration to file."""
    path = config_path or self.config_path or 'mcp_config.json'
    
    try:
      os.makedirs(os.path.dirname(path), exist_ok=True)
      with open(path, 'w') as f:
        json.dump(self.config, f, indent=2)
      print(f"Configuration saved to {path}")
    except IOError as e:
      print(f"Error saving configuration: {e}")

  def update_config(self, section: str, updates: Dict[str, Any]) -> None:
    """Update a configuration section."""
    if section not in self.config:
      self.config[section] = {}
    
    self.config[section].update(updates)

  def add_model_config(self, model_name: str, config: Dict[str, Any]) -> None:
    """Add configuration for a model."""
    if 'models' not in self.config:
      self.config['models'] = {}
    
    self.config['models'][model_name] = config


# Environment variable utilities
def get_env_config() -> Dict[str, Any]:
  """Get configuration from environment variables."""
  config = {}
  
  # Server configuration
  if os.environ.get('MCP_SERVER_HOST'):
    config.setdefault('server', {})['host'] = os.environ['MCP_SERVER_HOST']
  
  if os.environ.get('MCP_SERVER_PORT'):
    config.setdefault('server', {})['port'] = int(os.environ['MCP_SERVER_PORT'])
  
  if os.environ.get('MCP_AUTH_TOKEN'):
    config.setdefault('server', {})['auth_token'] = os.environ['MCP_AUTH_TOKEN']
    config.setdefault('client', {})['auth_token'] = os.environ['MCP_AUTH_TOKEN']
  
  # Client configuration
  if os.environ.get('MCP_CLIENT_TIMEOUT'):
    config.setdefault('client', {})['timeout'] = int(os.environ['MCP_CLIENT_TIMEOUT'])
  
  if os.environ.get('MCP_CONNECTOR_TYPE'):
    config.setdefault('client', {})['connector_type'] = os.environ['MCP_CONNECTOR_TYPE']
  
  return config


def create_default_config(config_path: str) -> None:
  """Create a default configuration file."""
  config = MCPConfig()
  config.save_config(config_path)


if __name__ == '__main__':
  # Example usage
  config = MCPConfig()
  
  print("Server config:", config.get_server_config())
  print("Client config:", config.get_client_config())
  
  # Add a model configuration
  config.add_model_config('bert_model', {
      'type': 'transformer',
      'checkpoint_path': '/path/to/bert/checkpoint',
      'max_sequence_length': 512
  })
  
  # Save configuration
  config.save_config('example_mcp_config.json')