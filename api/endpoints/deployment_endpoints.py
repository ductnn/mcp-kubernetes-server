from typing import Dict, Optional
from mcp.server.fastmcp import FastMCP
from services.deployment import DeploymentService

def register_deployment_endpoints(server: FastMCP, deployment_service: DeploymentService):
    """Register all deployment-related endpoints with the server"""
    
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