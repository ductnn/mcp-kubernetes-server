from mcp.server.fastmcp import FastMCP
from services.namespace import NamespaceService

def register_namespace_endpoints(server: FastMCP, namespace_service: NamespaceService):
    """Register all namespace-related endpoints with the server"""
    
    @server.tool("create_namespace")
    async def create_namespace(name: str):
        return namespace_service.create(name) 