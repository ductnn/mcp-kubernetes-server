import asyncio
import json
import logging
from typing import Dict, Any, Callable, List, Optional, Set
from datetime import datetime

logger = logging.getLogger("kubectl-mcp.sse")

class SSEManager:
    """
    Manager for Server-Sent Events (SSE) connections
    Handles client connections, event broadcasting, and event filtering
    """
    
    def __init__(self):
        self._clients: Set[asyncio.Queue] = set()
        self._resource_watchers: Dict[str, List[Callable]] = {}
        self._lock = asyncio.Lock()
    
    async def add_client(self, client_queue: asyncio.Queue) -> None:
        """Add a new client to the SSE manager"""
        async with self._lock:
            self._clients.add(client_queue)
            logger.info(f"New SSE client connected. Total clients: {len(self._clients)}")
    
    async def remove_client(self, client_queue: asyncio.Queue) -> None:
        """Remove a client from the SSE manager"""
        async with self._lock:
            self._clients.discard(client_queue)
            logger.info(f"SSE client disconnected. Total clients: {len(self._clients)}")
    
    async def broadcast(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Broadcast an event to all connected clients
        
        Args:
            event_type: Type of event (e.g., 'pod_created', 'deployment_updated')
            data: Event data to send
        """
        if not self._clients:
            return
        
        # Add timestamp to event data
        event_data = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": data
        }
        
        # Format as SSE message
        message = f"event: {event_type}\ndata: {json.dumps(event_data)}\n\n"
        
        # Send to all clients
        disconnected_clients = set()
        for client in self._clients:
            try:
                await client.put(message)
            except Exception as e:
                logger.error(f"Error sending SSE to client: {e}")
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        if disconnected_clients:
            async with self._lock:
                self._clients -= disconnected_clients
                logger.info(f"Removed {len(disconnected_clients)} disconnected clients")
    
    async def register_resource_watcher(self, resource_type: str, callback: Callable) -> None:
        """
        Register a callback for resource changes
        
        Args:
            resource_type: Type of resource to watch (e.g., 'pod', 'deployment')
            callback: Async function to call when resource changes
        """
        if resource_type not in self._resource_watchers:
            self._resource_watchers[resource_type] = []
        self._resource_watchers[resource_type].append(callback)
        logger.info(f"Registered watcher for {resource_type}")
    
    async def notify_resource_change(self, resource_type: str, event_type: str, data: Dict[str, Any]) -> None:
        """
        Notify watchers about a resource change
        
        Args:
            resource_type: Type of resource that changed
            event_type: Type of event (e.g., 'created', 'updated', 'deleted')
            data: Event data
        """
        # Broadcast to all clients
        await self.broadcast(f"{resource_type}_{event_type}", data)
        
        # Notify specific watchers
        if resource_type in self._resource_watchers:
            for callback in self._resource_watchers[resource_type]:
                try:
                    await callback(event_type, data)
                except Exception as e:
                    logger.error(f"Error in resource watcher callback: {e}")

# Global SSE manager instance
sse_manager = SSEManager() 