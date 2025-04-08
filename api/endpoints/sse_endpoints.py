import asyncio
import json
from typing import Optional, Dict, Any
from mcp.server.fastmcp import FastMCP
from core.sse import sse_manager

def register_sse_endpoints(server: FastMCP):
    """Register all Server-Sent Events (SSE) endpoints with the server"""
    
    @server.tool("subscribe_events")
    async def subscribe_events(resource_type: Optional[str] = None):
        """
        Subscribe to SSE events
        
        Args:
            resource_type: Optional resource type to filter events (e.g., 'pod', 'deployment')
            
        Returns:
            A stream of SSE events
        """
        # Create a queue for this client
        client_queue = asyncio.Queue()
        
        # Add client to SSE manager
        await sse_manager.add_client(client_queue)
        
        try:
            # Send initial connection message
            await client_queue.put(
                f"event: connected\ndata: {json.dumps({'message': 'Connected to SSE stream'})}\n\n"
            )
            
            # Stream events until client disconnects
            while True:
                # Get next event from queue
                message = await client_queue.get()
                
                # If resource type is specified, filter events
                if resource_type and not message.startswith(f"event: {resource_type}_"):
                    continue
                
                # Yield the event
                yield message
                
                # Mark task as done
                client_queue.task_done()
                
        except asyncio.CancelledError:
            # Client disconnected
            pass
        finally:
            # Remove client from SSE manager
            await sse_manager.remove_client(client_queue)
    
    @server.tool("watch_resource")
    async def watch_resource(resource_type: str, namespace: Optional[str] = None):
        """
        Watch a specific resource type for changes
        
        Args:
            resource_type: Type of resource to watch (e.g., 'pod', 'deployment')
            namespace: Optional namespace to filter events
            
        Returns:
            A stream of resource change events
        """
        # Create a queue for this client
        client_queue = asyncio.Queue()
        
        # Add client to SSE manager
        await sse_manager.add_client(client_queue)
        
        try:
            # Send initial connection message
            await client_queue.put(
                f"event: watching\ndata: {json.dumps({'resource': resource_type, 'namespace': namespace})}\n\n"
            )
            
            # Stream events until client disconnects
            while True:
                # Get next event from queue
                message = await client_queue.get()
                
                # Filter by resource type
                if not message.startswith(f"event: {resource_type}_"):
                    continue
                
                # Filter by namespace if specified
                if namespace:
                    try:
                        data = json.loads(message.split("\n")[1].replace("data: ", ""))
                        if "namespace" in data["data"] and data["data"]["namespace"] != namespace:
                            continue
                    except (IndexError, json.JSONDecodeError):
                        pass
                
                # Yield the event
                yield message
                
                # Mark task as done
                client_queue.task_done()
                
        except asyncio.CancelledError:
            # Client disconnected
            pass
        finally:
            # Remove client from SSE manager
            await sse_manager.remove_client(client_queue) 