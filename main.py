#!/usr/bin/env python3
"""
Minimal MCP server for kubectl with kubeconfig support.
"""

import os
import sys
import json
import logging
import subprocess

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("minimal-mcp")

# Get kubeconfig path from environment variable or default location
KUBECONFIG = os.getenv("KUBECONFIG", os.path.expanduser("~/.kube/config"))

def run_kubectl_command(command):
    """Run a kubectl command with kubeconfig and return the result."""
    full_command = f"KUBECONFIG={KUBECONFIG} {command}"
    try:
        result = subprocess.run(
            full_command,
            shell=True,
            check=False,
            capture_output=True,
            text=True,
            timeout=10
        )
        return {
            "command": command,
            "result": result.stdout if result.returncode == 0 else result.stderr,
            "success": result.returncode == 0
        }
    except Exception as e:
        logger.error(f"Error running command: {e}")
        return {
            "command": command,
            "result": f"Error: {str(e)}",
            "success": False
        }

async def main():
    """Run a simple MCP server."""
    from mcp.server.fastmcp import FastMCP
    
    # Create a FastMCP server
    server = FastMCP("kubectl-mcp")
    
    # Register a simple tool
    @server.tool("process_natural_language")
    async def process_natural_language(query: str):
        """Process natural language query."""
        logger.info(f"Received query: {query}")
        query_map = {
            "pod": "kubectl get pods -A",
            "deployment": "kubectl get deployments",
            "service": "kubectl get services",
            "namespace list": "kubectl get namespaces"
        }
        cmd = next((v for k, v in query_map.items() if k in query), "kubectl get all")
        
        # Run the command
        result = run_kubectl_command(cmd)
        logger.info(f"Command result: {result}")
        return result

    # Register a tool to create a namespace
    @server.tool("create_namespace")
    async def create_namespace(name: str):
        """Create a new namespace with the given name."""
        cmd = f"kubectl create namespace {name}"
        result = run_kubectl_command(cmd)
        return result
    
    # Register a ping tool
    @server.tool("kubernetes_ping")
    async def kubernetes_ping():
        """Simple ping tool."""
        return {"status": "Kubernetes is connected!"}
    
    # Start the server with stdio transport
    logger.info("Starting MCP server with stdio transport")
    await server.run_stdio_async()

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Error running server: {e}")
        sys.exit(1)
