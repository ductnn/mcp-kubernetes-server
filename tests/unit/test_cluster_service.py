import pytest
from unittest.mock import patch, MagicMock

def test_ping_success(cluster_service):
    """Test successful cluster ping"""
    # Mock the executor response
    mock_response = {
        "command": "kubectl cluster-info",
        "output": "Kubernetes cluster is running",
        "error": None,
        "success": True,
        "message": "Command executed successfully"
    }
    cluster_service.executor.execute.return_value = mock_response
    
    # Call the method
    result = cluster_service.ping()
    
    # Verify the result
    assert result["status"] == "connected"
    assert result["details"] == mock_response
    
    # Verify the executor was called with the correct command
    cluster_service.executor.execute.assert_called_once_with("kubectl cluster-info")

def test_ping_failure(cluster_service):
    """Test cluster ping failure"""
    # Mock the executor response
    mock_response = {
        "command": "kubectl cluster-info",
        "output": "",
        "error": "Failed to connect to Kubernetes cluster",
        "success": False
    }
    cluster_service.executor.execute.return_value = mock_response
    
    # Call the method
    result = cluster_service.ping()
    
    # Verify the result
    assert result["status"] == "disconnected"
    assert result["details"] == mock_response
    
    # Verify the executor was called with the correct command
    cluster_service.executor.execute.assert_called_once_with("kubectl cluster-info") 