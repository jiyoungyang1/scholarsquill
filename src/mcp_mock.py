"""
Mock MCP classes for testing when real MCP is not available
"""

from typing import Dict, Any, List, Callable
import asyncio


class Server:
    """Mock MCP Server"""
    
    def __init__(self, name: str):
        self.name = name
        self.tools = {}
        self.resources = {}
    
    def tool(self):
        """Decorator to register a tool"""
        def decorator(func):
            self.tools[func.__name__] = func
            return func
        return decorator
    
    def list_resources(self):
        """Decorator to register resource listing"""
        def decorator(func):
            self.resources['list'] = func
            return func
        return decorator
    
    def read_resource(self):
        """Decorator to register resource reading"""
        def decorator(func):
            self.resources['read'] = func
            return func
        return decorator
    
    async def run(self, read_stream, write_stream, options):
        """Mock run method"""
        print(f"Mock MCP server '{self.name}' would run here")
        return {"status": "mock_running"}
    
    async def run_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Mock run_tool method to simulate tool execution"""
        if tool_name in self.tools:
            print(f"Mock MCP: Running tool '{tool_name}' with args: {kwargs}")
            # Call the registered tool function directly
            return await self.tools[tool_name](**kwargs)
        else:
            print(f"Mock MCP: Tool '{tool_name}' not found.")
            return {"success": False, "error": f"Tool '{tool_name}' not found in mock server."}
    
    def create_initialization_options(self):
        """Mock initialization options"""
        return {"mock": True}


class Tool:
    """Mock Tool"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description


class ToolResult:
    """Mock Tool Result"""
    def __init__(self, content: str):
        self.content = content


# Mock types for compatibility
class TextContent:
    def __init__(self, text: str):
        self.text = text


class ImageContent:
    def __init__(self, data: str, mimeType: str):
        self.data = data
        self.mimeType = mimeType


class EmbeddedResource:
    def __init__(self, resource: Any):
        self.resource = resource


class Resource:
    def __init__(self, uri: str, name: str, description: str = "", mimeType: str = "text/plain"):
        self.uri = uri
        self.name = name
        self.description = description
        self.mimeType = mimeType