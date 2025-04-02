import subprocess
import logging
import os
from functools import lru_cache
from typing import Dict, Any, Optional
from config.settings import settings

logger = logging.getLogger("kubectl-mcp.executor")

class KubernetesCommandExecutor:
    def __init__(self, kubeconfig: Optional[str] = None):
        self.kubeconfig = kubeconfig or settings.kubeconfig
        
    @lru_cache(maxsize=128)
    def execute(self, command: str, namespace: Optional[str] = None) -> Dict[str, Any]:
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
        if namespace and " -n " not in command and " --namespace " not in command:
            return f"{command} -n {namespace}"
        return command
    
    def _command_env(self) -> Dict[str, str]:
        env = os.environ.copy()
        env["KUBECONFIG"] = self.kubeconfig
        return env
    
    def _log_result(self, command: str, result: subprocess.CompletedProcess):
        if result.returncode == 0:
            logger.debug(f"Command succeeded: {command}")
        else:
            logger.warning(f"Command failed (code {result.returncode}): {command}")
    
    def _format_result(self, command: str, result: subprocess.CompletedProcess) -> Dict[str, Any]:
        return {
            "command": command,
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None,
            "success": result.returncode == 0
        }
    
    def _error_result(self, command: str, error: str) -> Dict[str, Any]:
        return {
            "command": command,
            "output": "",
            "error": error,
            "success": False
        }