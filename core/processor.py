from typing import Dict, Optional, Any, List, Tuple
from core.executor import KubernetesCommandExecutor
from core.helm_executor import HelmCommandExecutor
import re
import logging

logger = logging.getLogger("kubectl-mcp.nlp")

class NaturalLanguageProcessor:
    # Command patterns with regex support
    COMMAND_PATTERNS = {
        # Kubernetes List commands
        r"(?:show|list|get|display).*?(?:all\s+)?pods?": "kubectl get pods -A -o wide",
        r"(?:show|list|get|display).*?(?:all\s+)?deployments?": "kubectl get deployments -A -o wide",
        r"(?:show|list|get|display).*?(?:all\s+)?namespaces?": "kubectl get namespaces -o wide",
        r"(?:show|list|get|display).*?(?:all\s+)?nodes?": "kubectl get nodes -o wide",
        
        # Kubernetes Create commands
        r"create\s+(?:a\s+)?pod\s+(?:named\s+)?([a-z0-9-]+)\s+(?:using|with)\s+(?:image\s+)?([a-zA-Z0-9./:-]+)": 
            "kubectl create pod {1} --image={2}",
        r"create\s+(?:a\s+)?deployment\s+(?:named\s+)?([a-z0-9-]+)\s+(?:using|with)\s+(?:image\s+)?([a-zA-Z0-9./:-]+)(?:\s+with\s+(\d+)\s+replicas?)?": 
            "kubectl create deployment {1} --image={2} --replicas={3}",
        
        # Kubernetes Delete commands
        r"(?:delete|remove)\s+(?:the\s+)?pod\s+(?:named\s+)?([a-z0-9-]+)": 
            "kubectl delete pod {1}",
        r"(?:delete|remove)\s+(?:the\s+)?deployment\s+(?:named\s+)?([a-z0-9-]+)": 
            "kubectl delete deployment {1}",
        
        # Kubernetes Scale commands
        r"scale\s+(?:the\s+)?deployment\s+(?:named\s+)?([a-z0-9-]+)\s+to\s+(\d+)\s+replicas?": 
            "kubectl scale deployment {1} --replicas={2}",
        
        # Kubernetes Describe commands
        r"describe\s+(?:the\s+)?pod\s+(?:named\s+)?([a-z0-9-]+)": 
            "kubectl describe pod {1}",
        r"describe\s+(?:the\s+)?deployment\s+(?:named\s+)?([a-z0-9-]+)": 
            "kubectl describe deployment {1}",
        
        # Kubernetes Log commands
        r"(?:show|get)\s+logs?\s+(?:for|of)\s+(?:the\s+)?pod\s+(?:named\s+)?([a-z0-9-]+)": 
            "kubectl logs {1}",

        # Helm List commands
        r"(?:show|list|get|display).*?(?:all\s+)?helm\s+releases?": "helm list -A",
        r"(?:show|list|get|display).*?(?:all\s+)?helm\s+releases?\s+in\s+namespace\s+([a-z0-9-]+)": "helm list -n {1}",
        
        # Helm Install commands
        r"install\s+(?:helm\s+)?release\s+(?:named\s+)?([a-z0-9-]+)\s+(?:using|with)\s+chart\s+([a-zA-Z0-9./:-]+)(?:\s+in\s+namespace\s+([a-z0-9-]+))?(?:\s+version\s+([0-9.]+))?": 
            "helm install {1} {2}" + " -n {3}" if "{3}" else "" + " --version {4}" if "{4}" else "",
        
        # Helm Upgrade commands
        r"upgrade\s+(?:helm\s+)?release\s+(?:named\s+)?([a-z0-9-]+)\s+(?:using|with)\s+chart\s+([a-zA-Z0-9./:-]+)(?:\s+in\s+namespace\s+([a-z0-9-]+))?(?:\s+version\s+([0-9.]+))?": 
            "helm upgrade {1} {2}" + " -n {3}" if "{3}" else "" + " --version {4}" if "{4}" else "",
        
        # Helm Uninstall commands
        r"(?:uninstall|delete|remove)\s+(?:helm\s+)?release\s+(?:named\s+)?([a-z0-9-]+)(?:\s+in\s+namespace\s+([a-z0-9-]+))?(?:\s+keep\s+history)?": 
            "helm uninstall {1}" + " -n {2}" if "{2}" else "" + " --keep-history" if "keep history" in query else "",
        
        # Helm Rollback commands
        r"rollback\s+(?:helm\s+)?release\s+(?:named\s+)?([a-z0-9-]+)\s+to\s+revision\s+(\d+)(?:\s+in\s+namespace\s+([a-z0-9-]+))?": 
            "helm rollback {1} {2}" + " -n {3}" if "{3}" else "",
        
        # Helm Repository commands
        r"(?:show|list|get|display).*?(?:all\s+)?helm\s+repositories?": "helm repo list",
        r"add\s+helm\s+repository\s+(?:named\s+)?([a-z0-9-]+)\s+with\s+url\s+([a-zA-Z0-9./:-]+)": 
            "helm repo add {1} {2}",
        r"(?:remove|delete)\s+helm\s+repository\s+(?:named\s+)?([a-z0-9-]+)": 
            "helm repo remove {1}",
        r"update\s+helm\s+repositories?": "helm repo update",
        r"search\s+helm\s+repositories?\s+for\s+([a-zA-Z0-9-]+)": 
            "helm search repo {1}",
    }
    
    def __init__(self, executor: KubernetesCommandExecutor, helm_executor: Optional[HelmCommandExecutor] = None):
        self.executor = executor
        self.helm_executor = helm_executor
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for better performance"""
        self.compiled_patterns = [
            (re.compile(pattern, re.IGNORECASE), command)
            for pattern, command in self.COMMAND_PATTERNS.items()
        ]
    
    async def process(self, query: str, namespace: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a natural language query and execute the corresponding command
        Args:
            query: Natural language query
            namespace: Optional namespace to target
        Returns:
            Command execution result
        """
        try:
            command = self._match_query(query)
            if not command:
                logger.warning(f"No matching command found for query: {query}")
                return self.executor._error_result("", "No matching command found")
            
            # Extract namespace from query if present
            if not namespace:
                namespace_match = re.search(r"in\s+namespace\s+([a-z0-9-]+)", query, re.IGNORECASE)
                if namespace_match:
                    namespace = namespace_match.group(1)
            
            # Determine if this is a Helm command
            is_helm_command = any(helm_keyword in command.lower() for helm_keyword in ["helm", "release", "repository"])
            
            # Use appropriate executor based on command type
            executor = self.helm_executor if is_helm_command and self.helm_executor else self.executor
            return await executor.execute(command, namespace)
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return self.executor._error_result("", str(e))
    
    def _match_query(self, query: str) -> Optional[str]:
        """
        Match a natural language query to a command
        Args:
            query: Natural language query
        Returns:
            Matched command or None
        """
        query = query.strip().lower()
        
        # Try to match against compiled patterns
        for pattern, command_template in self.compiled_patterns:
            match = pattern.match(query)
            if match:
                # If the command has placeholders, format it with the matched groups
                if "{" in command_template:
                    try:
                        return command_template.format(*match.groups())
                    except (IndexError, KeyError) as e:
                        logger.error(f"Error formatting command: {str(e)}")
                        continue
                return command_template
        
        # Default to listing all resources if no specific match
        return "kubectl get all -A -o wide"
    
    def get_supported_commands(self) -> List[str]:
        """
        Get a list of supported command patterns
        Returns:
            List of supported command descriptions
        """
        commands = []
        for pattern in self.COMMAND_PATTERNS.keys():
            # Convert regex pattern to human-readable format
            readable = pattern.replace(r"(?:", "").replace(r")", "")
            readable = readable.replace(r"\s+", " ")
            readable = readable.replace(r"[a-z0-9-]+", "<name>")
            readable = readable.replace(r"[a-zA-Z0-9./:-]+", "<image/chart/url>")
            readable = readable.replace(r"\d+", "<number>")
            commands.append(readable)
        return commands