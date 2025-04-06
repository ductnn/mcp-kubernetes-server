from typing import Dict, Optional, Any
from kubernetes import client, config
from kubernetes.client.exceptions import ApiException
from core.executor import KubernetesCommandExecutor
from core.sse import sse_manager
import logging
import json

logger = logging.getLogger("kubectl-mcp.deployment")

class DeploymentService:
    def __init__(self, executor: Optional[KubernetesCommandExecutor] = None):
        try:
            config.load_kube_config()
            self.apps_v1 = client.AppsV1Api()
            self._exec = executor or KubernetesCommandExecutor()
        except Exception as e:
            logger.error(f"Failed to initialize Kubernetes client: {e}")
            raise

    async def create_deployment(
        self,
        name: str,
        namespace: str = "default",
        image: str = "nginx:latest",
        replicas: int = 1,
        labels: Optional[Dict[str, str]] = None,
        env_vars: Optional[Dict[str, str]] = None,
        container_port: Optional[int] = None,
        resources: Optional[Dict[str, Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Create a deployment using Kubernetes client
        Args:
            name: Deployment name
            namespace: Target namespace
            image: Container image
            replicas: Number of replicas
            labels: Deployment labels
            env_vars: Environment variables
            container_port: Container port to expose
            resources: Resource requests and limits
        Returns:
            Operation result
        """
        try:
            env = [client.V1EnvVar(name=k, value=v) for k, v in (env_vars or {}).items()]
            
            container = client.V1Container(
                name=name,
                image=image,
                env=env,
                ports=[client.V1ContainerPort(container_port=container_port)] if container_port else None,
                resources=client.V1ResourceRequirements(**resources) if resources else None
            )

            template = client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels=labels or {"app": name}),
                spec=client.V1PodSpec(containers=[container])
            )

            spec = client.V1DeploymentSpec(
                replicas=replicas,
                selector=client.V1LabelSelector(match_labels=labels or {"app": name}),
                template=template
            )

            deployment = client.V1Deployment(
                api_version="apps/v1",
                kind="Deployment",
                metadata=client.V1ObjectMeta(name=name),
                spec=spec
            )

            resp = self.apps_v1.create_namespaced_deployment(
                namespace=namespace,
                body=deployment
            )

            result = {
                "success": True,
                "status": resp.status,
                "message": f"Deployment {name} created"
            }
            
            # Notify SSE clients about the new deployment
            await sse_manager.notify_resource_change(
                "deployment", 
                "created", 
                {
                    "name": name,
                    "namespace": namespace,
                    "replicas": replicas,
                    "available": resp.status.available_replicas
                }
            )
            
            return result

        except ApiException as e:
            error_msg = f"K8s API error: {json.loads(e.body)['message']}"
            logger.error(error_msg)
            return self._exec._error_result("kubectl", error_msg)

    async def get_deployment(self, name: str, namespace: str = "default") -> Dict[str, Any]:
        """
        Get deployment details
        Args:
            name: Deployment name
            namespace: Target namespace
        Returns:
            Deployment information or error
        """
        try:
            resp = self.apps_v1.read_namespaced_deployment(name, namespace)
            return {
                "success": True,
                "deployment": {
                    "name": resp.metadata.name,
                    "replicas": resp.spec.replicas,
                    "available": resp.status.available_replicas,
                    "labels": resp.metadata.labels,
                    "selector": resp.spec.selector.match_labels
                }
            }
        except ApiException:
            cmd = f"kubectl get deployment {name} -n {namespace} -o json"
            return self._exec.execute(cmd)

    async def update_deployment(
        self,
        name: str,
        namespace: str = "default",
        replicas: Optional[int] = None,
        image: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Update deployment configuration
        Args:
            name: Deployment name
            namespace: Target namespace
            replicas: New number of replicas
            image: New container image
            labels: New labels
        Returns:
            Operation result
        """
        try:
            body = {}
            if replicas is not None:
                body["spec"] = {"replicas": replicas}
            if image is not None:
                body["spec"] = body.get("spec", {})
                body["spec"]["template"] = {"spec": {"containers": [{"name": name, "image": image}]}}
            if labels is not None:
                body["metadata"] = {"labels": labels}
                body["spec"] = body.get("spec", {})
                body["spec"]["selector"] = {"matchLabels": labels}
                body["spec"]["template"] = body.get("spec", {}).get("template", {})
                body["spec"]["template"]["metadata"] = {"labels": labels}

            resp = self.apps_v1.patch_namespaced_deployment(
                name=name,
                namespace=namespace,
                body=body
            )

            result = {
                "success": True,
                "message": f"Deployment {name} updated",
                "status": resp.status
            }
            
            # Notify SSE clients about the deployment update
            await sse_manager.notify_resource_change(
                "deployment", 
                "updated", 
                {
                    "name": name,
                    "namespace": namespace,
                    "replicas": replicas if replicas is not None else resp.spec.replicas,
                    "available": resp.status.available_replicas
                }
            )
            
            return result
            
        except ApiException as e:
            return self._exec._error_result(
                "kubectl",
                f"Deployment update failed: {json.loads(e.body)['message']}"
            )

    async def delete_deployment(
        self,
        name: str,
        namespace: str = "default",
        grace_period: int = 0
    ) -> Dict[str, Any]:
        """
        Delete a deployment
        Args:
            name: Deployment name
            namespace: Target namespace
            grace_period: Grace period in seconds
        Returns:
            Operation result
        """
        try:
            self.apps_v1.delete_namespaced_deployment(
                name=name,
                namespace=namespace,
                grace_period_seconds=grace_period
            )
            
            result = {
                "success": True,
                "message": f"Deployment {name} scheduled for deletion"
            }
            
            # Notify SSE clients about the deployment deletion
            await sse_manager.notify_resource_change(
                "deployment", 
                "deleted", 
                {
                    "name": name,
                    "namespace": namespace
                }
            )
            
            return result
            
        except ApiException:
            cmd = f"kubectl delete deployment {name} -n {namespace} --grace-period={grace_period}"
            return self._exec.execute(cmd)

    async def list_deployments(
        self,
        namespace: str = "default",
        label_selector: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List deployments with optional filters
        Args:
            namespace: Target namespace
            label_selector: Label selector query
        Returns:
            List of deployments or error
        """
        try:
            resp = self.apps_v1.list_namespaced_deployment(
                namespace=namespace,
                label_selector=label_selector
            )
            return {
                "success": True,
                "deployments": [{
                    "name": item.metadata.name,
                    "replicas": item.spec.replicas,
                    "available": item.status.available_replicas,
                    "labels": item.metadata.labels
                } for item in resp.items]
            }
        except ApiException:
            selector = f"-l {label_selector}" if label_selector else ""
            cmd = f"kubectl get deployments -n {namespace} {selector} -o json"
            return self._exec.execute(cmd)

    async def scale_deployment(
        self,
        name: str,
        replicas: int,
        namespace: str = "default"
    ) -> Dict[str, Any]:
        """
        Scale a deployment to a specific number of replicas
        Args:
            name: Deployment name
            replicas: Target number of replicas
            namespace: Target namespace
        Returns:
            Operation result
        """
        try:
            resp = self.apps_v1.patch_namespaced_deployment_scale(
                name=name,
                namespace=namespace,
                body={"spec": {"replicas": replicas}}
            )
            
            result = {
                "success": True,
                "message": f"Deployment {name} scaled to {replicas} replicas",
                "status": resp.status
            }
            
            # Notify SSE clients about the deployment scale
            await sse_manager.notify_resource_change(
                "deployment", 
                "scaled", 
                {
                    "name": name,
                    "namespace": namespace,
                    "replicas": replicas,
                    "available": resp.status.available_replicas
                }
            )
            
            return result
            
        except ApiException as e:
            return self._exec._error_result(
                "kubectl",
                f"Scale operation failed: {json.loads(e.body)['message']}"
            ) 