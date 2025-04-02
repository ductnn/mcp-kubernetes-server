from typing import Dict, Optional, Any
from core.executor import KubernetesCommandExecutor

class NaturalLanguageProcessor:
    COMMAND_MAP = {
        "pod": "kubectl get pods -A -o wide",
        "deployment": "kubectl get deployments -A -o wide"
    }
    
    def __init__(self, executor: KubernetesCommandExecutor):
        self.executor = executor
    
    def process(self, query: str, namespace: Optional[str] = None) -> Dict[str, Any]:
        command = self._match_query(query)
        return self.executor.execute(command, namespace)
    
    def _match_query(self, query: str) -> str:
        query_lower = query.lower()
        for pattern, command in self.COMMAND_MAP.items():
            if pattern in query_lower:
                return command
        return "kubectl get all -A -o wide"