from typing import Dict, Optional, Any, List, Tuple
from core.executor import KubernetesCommandExecutor
import re
import logging

logger = logging.getLogger("kubectl-mcp.nlp")

class NaturalLanguageProcessor:
    # Command patterns with regex support
    COMMAND_PATTERNS = {
        # List commands
        r"(?:show|list|get|display).*?(?:all\s+)?pods?": "kubectl get pods -A -o wide",
        r"(?:show|list|get|display).*?(?:all\s+)?deployments?": "kubectl get deployments -A -o wide",
        r"(?:show|list|get|display).*?(?:all\s+)?namespaces?": "kubectl get namespaces -o wide",
        r"(?:show|list|get|display).*?(?:all\s+)?nodes?": "kubectl get nodes -o wide",
        
        # Create commands
        r"create\s+(?:a\s+)?pod\s+(?:named\s+)?([a-z0-9-]+)\s+(?:using|with)\s+(?:image\s+)?([a-zA-Z0-9./:-]+)": 
            "kubectl create pod {1} --image={2}",
        r"create\s+(?:a\s+)?deployment\s+(?:named\s+)?([a-z0-9-]+)\s+(?:using|with)\s+(?:image\s+)?([a-zA-Z0-9./:-]+)(?:\s+with\s+(\d+)\s+replicas?)?": 
            "kubectl create deployment {1} --image={2} --replicas={3}",
        
        # Delete commands
        r"(?:delete|remove)\s+(?:the\s+)?pod\s+(?:named\s+)?([a-z0-9-]+)": 
            "kubectl delete pod {1}",
        r"(?:delete|remove)\s+(?:the\s+)?deployment\s+(?:named\s+)?([a-z0-9-]+)": 
            "kubectl delete deployment {1}",
        
        # Scale commands
        r"scale\s+(?:the\s+)?deployment\s+(?:named\s+)?([a-z0-9-]+)\s+to\s+(\d+)\s+replicas?": 
            "kubectl scale deployment {1} --replicas={2}",
        
        # Describe commands
        r"describe\s+(?:the\s+)?pod\s+(?:named\s+)?([a-z0-9-]+)": 
            "kubectl describe pod {1}",
        r"describe\s+(?:the\s+)?deployment\s+(?:named\s+)?([a-z0-9-]+)": 
            "kubectl describe deployment {1}",
        
        # Log commands
        r"(?:show|get)\s+logs?\s+(?:for|of)\s+(?:the\s+)?pod\s+(?:named\s+)?([a-z0-9-]+)": 
            "kubectl logs {1}",
    }
    
    def __init__(self, executor: KubernetesCommandExecutor):
        self.executor = executor
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
            
            return await self.executor.execute(command, namespace)
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return self.executor._error_result("", str(e))
    
    def _match_query(self, query: str) -> Optional[str]:
        """
        Match a natural language query to a kubectl command
        Args:
            query: Natural language query
        Returns:
            Matched kubectl command or None
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
            readable = readable.replace(r"[a-zA-Z0-9./:-]+", "<image>")
            readable = readable.replace(r"\d+", "<number>")
            commands.append(readable)
        return commands