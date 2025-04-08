from typing import Dict, Optional, Any
from kubernetes import client, config
from kubernetes.client.exceptions import ApiException
from core.executor import KubernetesCommandExecutor
from core.sse import sse_manager
import logging
import json

logger = logging.getLogger("kubectl-mcp.pod")

class PodService:
    def __init__(self, executor: Optional[KubernetesCommandExecutor] = None):
        try:
            config.load_kube_config()
            self.core_v1 = client.CoreV1Api()
            self._exec = executor or KubernetesCommandExecutor()
        except Exception as e:
            logger.error(f"Failed to initialize Kubernetes client: {e}")
            raise

    # Create
    async def create_pod(
        self,
        name: str,
        namespace: str = "default",
        image: str = "nginx:latest",
        labels: Optional[Dict[str, str]] = None,
        env_vars: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create a pod using Kubernetes client
        Args:
            name: Pod name
            namespace: Target namespace
            image: Container image
            labels: Pod labels
            env_vars: Environment variables
        Returns:
            Operation result
        """
        try:
            env = [client.V1EnvVar(name=k, value=v) for k, v in (env_vars or {}).items()]
            
            pod_manifest = {
                "apiVersion": "v1",
                "kind": "Pod",
                "metadata": {
                    "name": name,
                    "labels": labels or {"app": name}
                },
                "spec": {
                    "containers": [{
                        "name": name,
                        "image": image,
                        "env": env
                    }]
                }
            }
            
            resp = self.core_v1.create_namespaced_pod(
                namespace=namespace,
                body=pod_manifest
            )
            
            result = {
                "success": True,
                "status": resp.status,
                "pod_ip": resp.status.pod_ip,
                "message": f"Pod {name} created"
            }
            
            # Notify SSE clients about the new pod
            await sse_manager.notify_resource_change(
                "pod", 
                "created", 
                {
                    "name": name,
                    "namespace": namespace,
                    "status": resp.status.phase,
                    "pod_ip": resp.status.pod_ip
                }
            )
            
            return result
            
        except ApiException as e:
            error_msg = f"K8s API error: {json.loads(e.body)['message']}"
            logger.error(error_msg)
            return self._exec._error_result("kubectl", error_msg)

    # Read
    async def get_pod(self, name: str, namespace: str = "default") -> Dict[str, Any]:
        """
        Get pod details
        Args:
            name: Pod name
            namespace: Target namespace
        Returns:
            Pod information or error
        """
        try:
            resp = self.core_v1.read_namespaced_pod(name, namespace)
            return {
                "success": True,
                "pod": {
                    "name": resp.metadata.name,
                    "status": resp.status.phase,
                    "ip": resp.status.pod_ip,
                    "node": resp.spec.node_name,
                    "labels": resp.metadata.labels
                }
            }
        except ApiException:
            # Fallback to kubectl if API fails
            cmd = f"kubectl get pod {name} -n {namespace} -o json"
            return self._exec.execute(cmd)

    # Update
    async def update_pod_labels(
        self,
        name: str,
        labels: Dict[str, str],
        namespace: str = "default"
    ) -> Dict[str, Any]:
        """
        Update pod labels
        Args:
            name: Pod name
            labels: New labels (will merge with existing)
            namespace: Target namespace
        Returns:
            Operation result
        """
        try:
            body = {"metadata": {"labels": labels}}
            resp = self.core_v1.patch_namespaced_pod(
                name=name,
                namespace=namespace,
                body=body
            )
            
            result = {
                "success": True,
                "message": f"Labels updated for pod {name}",
                "new_labels": resp.metadata.labels
            }
            
            # Notify SSE clients about the pod update
            await sse_manager.notify_resource_change(
                "pod", 
                "updated", 
                {
                    "name": name,
                    "namespace": namespace,
                    "labels": resp.metadata.labels
                }
            )
            
            return result
            
        except ApiException as e:
            return self._exec._error_result(
                "kubectl",
                f"Label update failed: {json.loads(e.body)['message']}"
            )

    # Delete
    async def delete_pod(
        self,
        name: str,
        namespace: str = "default",
        grace_period: int = 0
    ) -> Dict[str, Any]:
        """
        Delete a pod
        Args:
            name: Pod name
            namespace: Target namespace
            grace_period: Grace period in seconds
        Returns:
            Operation result
        """
        try:
            self.core_v1.delete_namespaced_pod(
                name=name,
                namespace=namespace,
                grace_period_seconds=grace_period
            )
            
            result = {
                "success": True,
                "message": f"Pod {name} scheduled for deletion"
            }
            
            # Notify SSE clients about the pod deletion
            await sse_manager.notify_resource_change(
                "pod", 
                "deleted", 
                {
                    "name": name,
                    "namespace": namespace
                }
            )
            
            return result
            
        except ApiException:
            # Fallback to kubectl
            cmd = f"kubectl delete pod {name} -n {namespace} --grace-period={grace_period}"
            return self._exec.execute(cmd)

    # List
    async def list_pods(
        self,
        namespace: str = "default",
        label_selector: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List pods with optional filters
        Args:
            namespace: Target namespace
            label_selector: Label selector query
        Returns:
            List of pods or error
        """
        try:
            resp = self.core_v1.list_namespaced_pod(
                namespace=namespace,
                label_selector=label_selector
            )
            return {
                "success": True,
                "pods": [{
                    "name": item.metadata.name,
                    "status": item.status.phase,
                    "ip": item.status.pod_ip
                } for item in resp.items]
            }
        except ApiException:
            # Fallback to kubectl
            selector = f"-l {label_selector}" if label_selector else ""
            cmd = f"kubectl get pods -n {namespace} {selector} -o json"
            return self._exec.execute(cmd)

    # Add to PodService class
    async def port_forward(self, pod_name: str, namespace: str, local_port: int, pod_port: int) -> Dict[str, Any]:
        """Forward local port to pod"""
        cmd = f"kubectl port-forward {pod_name} -n {namespace} {local_port}:{pod_port}"
        return self._exec.execute(cmd, timeout_override=3600)  # Long timeout for forwarding

    async def exec_command(self, pod_name: str, namespace: str, command: str) -> Dict[str, Any]:
        """Execute command in pod container"""
        cmd = f"kubectl exec {pod_name} -n {namespace} -- {command}"
        return self._exec.execute(cmd)
