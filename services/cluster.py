from typing import Dict, Any
from core.executor import KubernetesCommandExecutor

class ClusterService:
    def __init__(self, executor: KubernetesCommandExecutor):
        self.executor = executor
    
    def ping(self) -> Dict[str, Any]:
        result = self.executor.execute("kubectl cluster-info")
        return {
            "status": "connected" if result["success"] else "disconnected",
            "details": result
        }