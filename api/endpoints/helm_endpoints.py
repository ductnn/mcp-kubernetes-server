from typing import Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from services.helm import HelmService
import logging

logger = logging.getLogger("kubectl-mcp.helm_endpoints")

def register_helm_endpoints(server: FastMCP, helm_service: HelmService):
    """Register all Helm endpoints with the server"""
    
    @server.tool("helm_list")
    async def list_releases(namespace: Optional[str] = None) -> Dict[str, Any]:
        """
        List Helm releases
        Args:
            namespace: Optional namespace to target
        Returns:
            List of releases
        """
        return await helm_service.list_releases(namespace)
    
    @server.tool("helm_install")
    async def install_release(
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
        return await helm_service.install_release(name, chart, namespace, values, version)
    
    @server.tool("helm_upgrade")
    async def upgrade_release(
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
        return await helm_service.upgrade_release(name, chart, namespace, values, version)
    
    @server.tool("helm_uninstall")
    async def uninstall_release(
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
        return await helm_service.uninstall_release(name, namespace, keep_history)
    
    @server.tool("helm_get_values")
    async def get_values(
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
        return await helm_service.get_values(name, namespace, all_values)
    
    @server.tool("helm_rollback")
    async def rollback_release(
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
        return await helm_service.rollback_release(name, revision, namespace)
    
    @server.tool("helm_search")
    async def search_repos(
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
        return await helm_service.search_repos(keyword, regex)
    
    @server.tool("helm_repo_add")
    async def repo_add(name: str, url: str) -> Dict[str, Any]:
        """
        Add a Helm repository
        Args:
            name: Repository name
            url: Repository URL
        Returns:
            Add result
        """
        return await helm_service.repo_add(name, url)
    
    @server.tool("helm_repo_update")
    async def repo_update() -> Dict[str, Any]:
        """
        Update Helm repositories
        Returns:
            Update result
        """
        return await helm_service.repo_update()
    
    @server.tool("helm_repo_list")
    async def repo_list() -> Dict[str, Any]:
        """
        List Helm repositories
        Returns:
            List of repositories
        """
        return await helm_service.repo_list()
    
    @server.tool("helm_repo_remove")
    async def repo_remove(name: str) -> Dict[str, Any]:
        """
        Remove a Helm repository
        Args:
            name: Repository name
        Returns:
            Remove result
        """
        return await helm_service.repo_remove(name) 