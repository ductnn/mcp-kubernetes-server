from typing import Dict, Optional
from mcp.server.fastmcp import FastMCP
from services.pod import PodService

def register_pod_endpoints(server: FastMCP, pod_service: PodService):
    """Register all pod-related endpoints with the server"""
    
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