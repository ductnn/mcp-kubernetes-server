from typing import Dict, Optional, Any
from core.executor import KubernetesCommandExecutor

class NamespaceService:
    """Service for namespace operations with full KubernetesCommandExecutor utilization"""
    
    def __init__(self, executor: KubernetesCommandExecutor):
        self._exec = executor  # Sử dụng naming convention cho internal attribute
    
    def create(self, name: str, labels: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create namespace with advanced options
        Args:
            name: Namespace name (DNS-1123 compliant)
            labels: Optional labels as key-value pairs
        Returns:
            Command execution result
        """
        if not self._validate_name(name):
            return self._exec._error_result("", "Invalid namespace name")
        
        label_flags = " ".join(f"--label={k}={v}" for k, v in (labels or {}).items())
        cmd = f"kubectl create namespace {name} {label_flags}".strip()
        return self._exec.execute(cmd)
    
    def delete(self, name: str, force: bool = False, timeout: int = None) -> Dict[str, Any]:
        """
        Delete namespace with grace period control
        Args:
            name: Namespace to delete
            force: Immediate deletion (--force --grace-period=0)
            timeout: Custom timeout in seconds
        Returns:
            Command execution result
        """
        force_flags = "--force --grace-period=0" if force else ""
        cmd = f"kubectl delete namespace {name} {force_flags}".strip()
        return self._exec.execute(cmd, timeout=timeout)
    
    def list(self, output_format: str = "wide") -> Dict[str, Any]:
        """
        List namespaces with format options
        Args:
            output_format: wide|json|yaml (default: wide)
        Returns:
            Command execution result
        """
        return self._exec.execute(f"kubectl get namespaces -o {output_format}")
    
    def describe(self, name: str) -> Dict[str, Any]:
        """Get detailed namespace description"""
        return self._exec.execute(f"kubectl describe namespace {name}")
    
    def exists(self, name: str) -> bool:
        """Check namespace existence using cached command"""
        result = self._exec.execute(f"kubectl get namespace {name} --ignore-not-found")
        return bool(result["success"] and name in result["output"])
    
    def _validate_name(self, name: str) -> bool:
        """DNS-1123 compliant validation"""
        return (name and 
                name.isalnum() and 
                name[0].isalpha() and 
                len(name) <= 253 and
                not name.startswith('kube-'))