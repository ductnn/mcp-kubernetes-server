import logging
from mcp.server.fastmcp import FastMCP
from core.executor import KubernetesCommandExecutor
from api.endpoints import register_all_endpoints

logger = logging.getLogger("kubectl-mcp.server")

async def setup_server():
    """Set up and configure the MCP server with all endpoints"""
    # Initialize the executor
    executor = KubernetesCommandExecutor()
    
    # Create the server
    server = FastMCP("kubectl-mcp-server")
    
    # Register all endpoints
    register_all_endpoints(server, executor)
    
    return server