import logging
from mcp.server.fastmcp import FastMCP
from typing import Dict, Optional
from core.executor import KubernetesCommandExecutor
from core.processor import NaturalLanguageProcessor
from services.namespace import NamespaceService
from services.cluster import ClusterService
from services.pod import PodService
from services.deployment import DeploymentService

logger = logging.getLogger("kubectl-mcp.server")

async def setup_server():
    executor = KubernetesCommandExecutor()
    nl_processor = NaturalLanguageProcessor(executor)
    namespace_service = NamespaceService(executor)
    cluster_service = ClusterService(executor)
    pod_service = PodService(executor)
    deployment_service = DeploymentService(executor)
    
    server = FastMCP("kubectl-mcp-server")
    
    @server.tool("process_query")
    async def process_query(query: str, namespace: str = None):
        return nl_processor.process(query, namespace)

    # Pod endpoints
    @server.tool("create_pod")
    async def create_pod(
        name: str,
        namespace: str = "default",
        image: str = "nginx:latest",
        labels: Optional[Dict[str, str]] = None
    ):
        return pod_service.create_pod(name, namespace, image, labels)
    
    @server.tool("get_pod")
    async def get_pod(name: str, namespace: str = "default"):
        return pod_service.get_pod(name, namespace)
    
    @server.tool("update_pod_labels")
    async def update_pod_labels(
        name: str,
        labels: Dict[str, str],
        namespace: str = "default"
    ):
        return pod_service.update_pod_labels(name, labels, namespace)
    
    @server.tool("delete_pod")
    async def delete_pod(
        name: str,
        namespace: str = "default",
        grace_period: int = 0
    ):
        return pod_service.delete_pod(name, namespace, grace_period)
    
    @server.tool("list_pods")
    async def list_pods(
        namespace: str = "default",
        label_selector: Optional[str] = None
    ):
        return pod_service.list_pods(namespace, label_selector)
    
    @server.tool("port_forward")
    async def port_forward(pod_name: str, namespace: str, ports: str):
        local_port, pod_port = ports.split(":")
        return pod_service.port_forward(pod_name, namespace, int(local_port), int(pod_port))

    # Deployment endpoints
    @server.tool("create_deployment")
    async def create_deployment(
        name: str,
        namespace: str = "default",
        image: str = "nginx:latest",
        replicas: int = 1,
        labels: Optional[Dict[str, str]] = None,
        env_vars: Optional[Dict[str, str]] = None,
        container_port: Optional[int] = None,
        resources: Optional[Dict[str, Dict[str, str]]] = None
    ):
        return deployment_service.create_deployment(
            name, namespace, image, replicas, labels, env_vars, container_port, resources
        )
    
    @server.tool("get_deployment")
    async def get_deployment(name: str, namespace: str = "default"):
        return deployment_service.get_deployment(name, namespace)
    
    @server.tool("update_deployment")
    async def update_deployment(
        name: str,
        namespace: str = "default",
        replicas: Optional[int] = None,
        image: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None
    ):
        return deployment_service.update_deployment(name, namespace, replicas, image, labels)
    
    @server.tool("delete_deployment")
    async def delete_deployment(
        name: str,
        namespace: str = "default",
        grace_period: int = 0
    ):
        return deployment_service.delete_deployment(name, namespace, grace_period)
    
    @server.tool("list_deployments")
    async def list_deployments(
        namespace: str = "default",
        label_selector: Optional[str] = None
    ):
        return deployment_service.list_deployments(namespace, label_selector)
    
    @server.tool("scale_deployment")
    async def scale_deployment(
        name: str,
        replicas: int,
        namespace: str = "default"
    ):
        return deployment_service.scale_deployment(name, replicas, namespace)

    # Namespace
    @server.tool("create_namespace")
    async def create_namespace(name: str):
        return namespace_service.create(name)
    
    @server.tool("cluster_ping")
    async def cluster_ping():
        return cluster_service.ping()
    
    return server