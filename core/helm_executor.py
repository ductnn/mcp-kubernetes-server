import subprocess
import logging
import os
from functools import lru_cache
from typing import Dict, Any, Optional
from config.settings import settings

logger = logging.getLogger("kubectl-mcp.helm")

class HelmCommandExecutor:
    def __init__(self, kubeconfig: Optional[str] = None):
        self.kubeconfig = kubeconfig or settings.kubeconfig
        
    @lru_cache(maxsize=128)
    def execute(self, command: str, namespace: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a Helm command
        Args:
            command: Helm command to execute
            namespace: Optional namespace to target
        Returns:
            Command execution result
        """
        full_command = self._build_command(command, namespace)
        try:
            result = subprocess.run(
                full_command,
                shell=True,
                check=False,
                capture_output=True,
                text=True,
                timeout=settings.COMMAND_TIMEOUT,
                env=self._command_env()
            )
            self._log_result(command, result)
            return self._format_result(command, result)
        except subprocess.TimeoutExpired:
            return self._error_result(command, "Command timed out")
        except Exception as e:
            return self._error_result(command, str(e))
    
    def _build_command(self, command: str, namespace: Optional[str]) -> str:
        """
        Build the full Helm command with namespace if provided
        Args:
            command: Base Helm command
            namespace: Optional namespace
        Returns:
            Full Helm command
        """
        if namespace and " -n " not in command and " --namespace " not in command:
            return f"{command} -n {namespace}"
        return command
    
    def _command_env(self) -> Dict[str, str]:
        """
        Get environment variables for command execution
        Returns:
            Environment variables dictionary
        """
        env = os.environ.copy()
        env["KUBECONFIG"] = self.kubeconfig
        return env
    
    def _log_result(self, command: str, result: subprocess.CompletedProcess):
        """
        Log command execution result
        Args:
            command: Executed command
            result: Command result
        """
        if result.returncode == 0:
            logger.debug(f"Helm command succeeded: {command}")
        else:
            logger.warning(f"Helm command failed (code {result.returncode}): {command}")
    
    def _format_result(self, command: str, result: subprocess.CompletedProcess) -> Dict[str, Any]:
        """
        Format command execution result
        Args:
            command: Executed command
            result: Command result
        Returns:
            Formatted result dictionary
        """
        return {
            "command": command,
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None,
            "success": result.returncode == 0
        }
    
    def _error_result(self, command: str, error: str) -> Dict[str, Any]:
        """
        Create error result dictionary
        Args:
            command: Failed command
            error: Error message
        Returns:
            Error result dictionary
        """
        return {
            "command": command,
            "output": "",
            "error": error,
            "success": False
        }
    
    # Common Helm operations
    def list_releases(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """
        List Helm releases
        Args:
            namespace: Optional namespace to target
        Returns:
            List of releases
        """
        return self.execute("helm list", namespace)
    
    def install_release(
        self,
        name: str,
        chart: str,
        namespace: Optional[str] = None,
        values: Optional[Dict[str, Any]] = None,
        version: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Install a Helm release
        Args:
            name: Release name
            chart: Chart name or path
            namespace: Optional namespace
            values: Optional values to override
            version: Optional chart version
        Returns:
            Installation result
        """
        cmd = f"helm install {name} {chart}"
        if version:
            cmd += f" --version {version}"
        if values:
            # TODO: Implement values file creation and usage
            pass
        return self.execute(cmd, namespace)
    
    def upgrade_release(
        self,
        name: str,
        chart: str,
        namespace: Optional[str] = None,
        values: Optional[Dict[str, Any]] = None,
        version: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upgrade a Helm release
        Args:
            name: Release name
            chart: Chart name or path
            namespace: Optional namespace
            values: Optional values to override
            version: Optional chart version
        Returns:
            Upgrade result
        """
        cmd = f"helm upgrade {name} {chart}"
        if version:
            cmd += f" --version {version}"
        if values:
            # TODO: Implement values file creation and usage
            pass
        return self.execute(cmd, namespace)
    
    def uninstall_release(
        self,
        name: str,
        namespace: Optional[str] = None,
        keep_history: bool = False
    ) -> Dict[str, Any]:
        """
        Uninstall a Helm release
        Args:
            name: Release name
            namespace: Optional namespace
            keep_history: Whether to keep release history
        Returns:
            Uninstallation result
        """
        cmd = f"helm uninstall {name}"
        if keep_history:
            cmd += " --keep-history"
        return self.execute(cmd, namespace)
    
    def get_values(
        self,
        name: str,
        namespace: Optional[str] = None,
        all_values: bool = False
    ) -> Dict[str, Any]:
        """
        Get values for a Helm release
        Args:
            name: Release name
            namespace: Optional namespace
            all_values: Whether to show all values
        Returns:
            Release values
        """
        cmd = f"helm get values {name}"
        if all_values:
            cmd += " --all"
        return self.execute(cmd, namespace)
    
    def rollback_release(
        self,
        name: str,
        revision: Optional[int] = None,
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Rollback a Helm release
        Args:
            name: Release name
            revision: Revision to rollback to
            namespace: Optional namespace
        Returns:
            Rollback result
        """
        cmd = f"helm rollback {name}"
        if revision:
            cmd += f" {revision}"
        return self.execute(cmd, namespace)
    
    def search_repos(
        self,
        keyword: Optional[str] = None,
        regex: bool = False
    ) -> Dict[str, Any]:
        """
        Search Helm repositories
        Args:
            keyword: Search keyword
            regex: Whether to use regex search
        Returns:
            Search results
        """
        cmd = "helm search repo"
        if keyword:
            cmd += f" {'--regex' if regex else ''} {keyword}"
        return self.execute(cmd)
    
    def repo_add(self, name: str, url: str) -> Dict[str, Any]:
        """
        Add a Helm repository
        Args:
            name: Repository name
            url: Repository URL
        Returns:
            Add result
        """
        return self.execute(f"helm repo add {name} {url}")
    
    def repo_update(self) -> Dict[str, Any]:
        """
        Update Helm repositories
        Returns:
            Update result
        """
        return self.execute("helm repo update")
    
    def repo_list(self) -> Dict[str, Any]:
        """
        List Helm repositories
        Returns:
            List of repositories
        """
        return self.execute("helm repo list")
    
    def repo_remove(self, name: str) -> Dict[str, Any]:
        """
        Remove a Helm repository
        Args:
            name: Repository name
        Returns:
            Remove result
        """
        return self.execute(f"helm repo remove {name}") 