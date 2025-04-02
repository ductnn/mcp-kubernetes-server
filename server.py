import logging
from mcp.server.fastmcp import FastMCP
from core.executor import KubernetesCommandExecutor
from core.processor import NaturalLanguageProcessor
from services.namespace import NamespaceService
from services.cluster import ClusterService

logger = logging.getLogger("kubectl-mcp.server")

async def setup_server():
    executor = KubernetesCommandExecutor()
    nl_processor = NaturalLanguageProcessor(executor)
    namespace_service = NamespaceService(executor)
    cluster_service = ClusterService(executor)
    
    server = FastMCP("kubectl-mcp-server")
    
    @server.tool("process_query")
    async def process_query(query: str, namespace: str = None):
        return nl_processor.process(query, namespace)
    
    # Namespace
    @server.tool("create_namespace")
    async def create_namespace(name: str):
        return namespace_service.create(name)
    
    @server.tool("cluster_ping")
    async def cluster_ping():
        return cluster_service.ping()
    
    return server