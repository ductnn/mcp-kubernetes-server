import os
from typing import Optional

class Settings:
    DEFAULT_KUBECONFIG = os.path.expanduser("~/.kube/config")
    COMMAND_TIMEOUT = 10
    DEFAULT_NAMESPACE = "default"
    
    @property
    def kubeconfig(self) -> str:
        return os.getenv("KUBECONFIG", self.DEFAULT_KUBECONFIG)

settings = Settings()
