# API endpoints for Kubernetes MCP Server 

from mcp.server.fastmcp import FastMCP
from core.executor import KubernetesCommandExecutor
from core.helm_executor import HelmCommandExecutor
from core.processor import NaturalLanguageProcessor
from services.namespace import NamespaceService
from services.cluster import ClusterService
from services.pod import PodService
from services.deployment import DeploymentService
from services.helm import HelmService

from .pod_endpoints import register_pod_endpoints
from .deployment_endpoints import register_deployment_endpoints
from .namespace_endpoints import register_namespace_endpoints
from .cluster_endpoints import register_cluster_endpoints
from .nlp_endpoints import register_nlp_endpoints
from .helm_endpoints import register_helm_endpoints

def register_all_endpoints(server: FastMCP, executor: KubernetesCommandExecutor):
    """Register all API endpoints with the server"""
    
    # Initialize services
    nl_processor = NaturalLanguageProcessor(executor)
    namespace_service = NamespaceService(executor)
    cluster_service = ClusterService(executor)
    pod_service = PodService(executor)
    deployment_service = DeploymentService(executor)
    
    # Initialize Helm service
    helm_executor = HelmCommandExecutor()
    helm_service = HelmService(helm_executor)
    
    # Register endpoints by resource type
    register_nlp_endpoints(server, nl_processor)
    register_pod_endpoints(server, pod_service)
    register_deployment_endpoints(server, deployment_service)
    register_namespace_endpoints(server, namespace_service)
    register_cluster_endpoints(server, cluster_service)
    register_helm_endpoints(server, helm_service) 