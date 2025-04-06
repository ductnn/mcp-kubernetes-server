from typing import Dict, Any, Optional, List
from mcp.server.fastmcp import FastMCP
from core.processor import NaturalLanguageProcessor
import logging

logger = logging.getLogger("kubectl-mcp.nlp_endpoints")

def register_nlp_endpoints(server: FastMCP, nl_processor: NaturalLanguageProcessor):
    """Register all natural language processing endpoints with the server"""
    
    @server.tool("process_query")
    async def process_query(query: str, namespace: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a natural language query and execute the corresponding Kubernetes command
        
        Args:
            query: Natural language query to process
            namespace: Optional namespace to target (default: None)
            
        Returns:
            Dict containing:
                - success: bool indicating if the command was successful
                - command: the executed kubectl command
                - output: command output if successful
                - error: error message if unsuccessful
                
        Examples:
            >>> await process_query("Show me all pods")
            >>> await process_query("Create a pod named nginx using image nginx:latest", namespace="default")
            >>> await process_query("List deployments in namespace kube-system")
        """
        try:
            logger.info(f"Processing query: {query} (namespace: {namespace})")
            result = await nl_processor.process(query, namespace)
            logger.debug(f"Query result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to process query: {str(e)}",
                "command": "",
                "output": ""
            }
    
    @server.tool("list_supported_commands")
    async def list_supported_commands() -> List[str]:
        """
        Get a list of all supported natural language command patterns
        
        Returns:
            List of supported command patterns in human-readable format
            
        Examples:
            >>> await list_supported_commands()
            [
                "show all pods",
                "create pod <name> using <image>",
                "scale deployment <name> to <number> replicas",
                ...
            ]
        """
        try:
            commands = nl_processor.get_supported_commands()
            logger.debug(f"Supported commands: {commands}")
            return commands
        except Exception as e:
            logger.error(f"Error listing supported commands: {str(e)}")
            return []
    
    @server.tool("validate_query")
    async def validate_query(query: str) -> Dict[str, Any]:
        """
        Validate if a natural language query can be processed
        
        Args:
            query: Natural language query to validate
            
        Returns:
            Dict containing:
                - valid: bool indicating if the query is valid
                - command: the kubectl command that would be executed
                - error: error message if invalid
                
        Examples:
            >>> await validate_query("Show me all pods")
            {
                "valid": True,
                "command": "kubectl get pods -A -o wide",
                "error": None
            }
            >>> await validate_query("Invalid query")
            {
                "valid": False,
                "command": None,
                "error": "No matching command found"
            }
        """
        try:
            command = nl_processor._match_query(query)
            if command:
                return {
                    "valid": True,
                    "command": command,
                    "error": None
                }
            return {
                "valid": False,
                "command": None,
                "error": "No matching command found"
            }
        except Exception as e:
            logger.error(f"Error validating query: {str(e)}")
            return {
                "valid": False,
                "command": None,
                "error": str(e)
            } 