import pytest
from unittest.mock import MagicMock, patch
from core.executor import KubernetesCommandExecutor
from services.pod import PodService
from services.deployment import DeploymentService
from services.namespace import NamespaceService
from services.cluster import ClusterService
from core.processor import NaturalLanguageProcessor

@pytest.fixture
def mock_executor():
    """Create a mock KubernetesCommandExecutor"""
    executor = MagicMock(spec=KubernetesCommandExecutor)
    executor.execute.return_value = {"success": True, "message": "Command executed successfully"}
    executor._error_result.return_value = {"success": False, "error": "Error executing command"}
    return executor

@pytest.fixture
def pod_service(mock_executor):
    """Create a PodService with a mock executor"""
    with patch("kubernetes.client.CoreV1Api") as mock_api:
        mock_api.return_value = MagicMock()
        service = PodService(mock_executor)
        return service

@pytest.fixture
def deployment_service(mock_executor):
    """Create a DeploymentService with a mock executor"""
    with patch("kubernetes.client.AppsV1Api") as mock_api:
        mock_api.return_value = MagicMock()
        service = DeploymentService(mock_executor)
        return service

@pytest.fixture
def namespace_service(mock_executor):
    """Create a NamespaceService with a mock executor"""
    with patch("kubernetes.client.CoreV1Api") as mock_api:
        mock_api.return_value = MagicMock()
        service = NamespaceService(mock_executor)
        return service

@pytest.fixture
def cluster_service(mock_executor):
    """Create a ClusterService with a mock executor"""
    service = ClusterService(mock_executor)
    return service

@pytest.fixture
def nl_processor(mock_executor):
    """Create a NaturalLanguageProcessor with a mock executor"""
    processor = NaturalLanguageProcessor(mock_executor)
    return processor 