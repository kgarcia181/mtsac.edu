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

"""Model Control Protocol (MCP) connector for Google Research models.

This module provides a standardized way to connect to and interact with 
Google Research models remotely. It supports both full-featured implementations
with web frameworks and simple demo versions for basic usage.

Usage:
    For full functionality (requires Flask, requests, websocket-client):
    >>> from mcp.server import MCPServer
    >>> from mcp.client import MCPClient
    
    For demo/testing (no external dependencies):
    >>> from mcp.demo import demo_mcp
    >>> demo_mcp()
"""

# Try to import full-featured components
try:
    from mcp.server import MCPServer
    from mcp.client import MCPClient
    FULL_MCP_AVAILABLE = True
except ImportError:
    MCPServer = None
    MCPClient = None
    FULL_MCP_AVAILABLE = False

# Always available components
from mcp.connector import MCPConnector, HTTPConnector, WebSocketConnector
from mcp.config import MCPConfig
from mcp.demo import SimpleMCPConnector, SimpleModel, SimpleMCPDemo, demo_mcp

# Define public API
__all__ = [
    'MCPConnector', 'HTTPConnector', 'WebSocketConnector',
    'MCPConfig',
    'SimpleMCPConnector', 'SimpleModel', 'SimpleMCPDemo', 'demo_mcp'
]

# Add full components if available
if FULL_MCP_AVAILABLE:
    __all__.extend(['MCPServer', 'MCPClient'])

__version__ = '1.0.0'