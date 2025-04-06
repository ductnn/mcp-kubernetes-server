from typing import Dict, Optional, Any
from core.helm_executor import HelmCommandExecutor
import logging
import json

logger = logging.getLogger("kubectl-mcp.helm")

class HelmService:
    def __init__(self, executor: Optional[HelmCommandExecutor] = None):
        self._exec = executor or HelmCommandExecutor()
    
    async def list_releases(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """
        List Helm releases
        Args:
            namespace: Optional namespace to target
        Returns:
            List of releases
        """
        return await self._exec.list_releases(namespace)
    
    async def install_release(
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
        return await self._exec.install_release(name, chart, namespace, values, version)
    
    async def upgrade_release(
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
        return await self._exec.upgrade_release(name, chart, namespace, values, version)
    
    async def uninstall_release(
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
        return await self._exec.uninstall_release(name, namespace, keep_history)
    
    async def get_values(
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
        return await self._exec.get_values(name, namespace, all_values)
    
    async def rollback_release(
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
        return await self._exec.rollback_release(name, revision, namespace)
    
    async def search_repos(
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
        return await self._exec.search_repos(keyword, regex)
    
    async def repo_add(self, name: str, url: str) -> Dict[str, Any]:
        """
        Add a Helm repository
        Args:
            name: Repository name
            url: Repository URL
        Returns:
            Add result
        """
        return await self._exec.repo_add(name, url)
    
    async def repo_update(self) -> Dict[str, Any]:
        """
        Update Helm repositories
        Returns:
            Update result
        """
        return await self._exec.repo_update()
    
    async def repo_list(self) -> Dict[str, Any]:
        """
        List Helm repositories
        Returns:
            List of repositories
        """
        return await self._exec.repo_list()
    
    async def repo_remove(self, name: str) -> Dict[str, Any]:
        """
        Remove a Helm repository
        Args:
            name: Repository name
        Returns:
            Remove result
        """
        return await self._exec.repo_remove(name) 