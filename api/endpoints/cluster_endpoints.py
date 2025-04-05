from mcp.server.fastmcp import FastMCP
from services.cluster import ClusterService

def register_cluster_endpoints(server: FastMCP, cluster_service: ClusterService):
    """Register all cluster-related endpoints with the server"""
    
    @server.tool("cluster_ping")
    async def cluster_ping():
        return cluster_service.ping() 