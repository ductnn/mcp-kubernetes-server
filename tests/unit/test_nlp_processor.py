import pytest
from unittest.mock import patch, MagicMock

def test_process_query_list_pods(nl_processor):
    """Test processing a query to list pods"""
    # Mock the executor response
    mock_response = {
        "command": "kubectl get pods -A -o wide",
        "output": "NAME READY STATUS RESTARTS AGE\npod-1 1/1 Running 0 1h\npod-2 1/1 Running 0 1h",
        "error": None,
        "success": True
    }
    nl_processor.executor.execute.return_value = mock_response
    
    # Call the method
    result = nl_processor.process("Show me all pods")
    
    # Verify the result
    assert result == mock_response
    assert result["success"] is True
    assert "pod-1" in result["output"]
    assert "pod-2" in result["output"]
    
    # Verify the executor was called with the correct command
    nl_processor.executor.execute.assert_called_once_with("kubectl get pods -A -o wide", None)

def test_process_query_list_deployments(nl_processor):
    """Test processing a query to list deployments"""
    # Mock the executor response
    mock_response = {
        "command": "kubectl get deployments -A -o wide",
        "output": "NAME READY UP-TO-DATE AVAILABLE AGE\ndeployment-1 3/3 3 3 1h\ndeployment-2 2/2 2 2 1h",
        "error": None,
        "success": True
    }
    nl_processor.executor.execute.return_value = mock_response
    
    # Call the method
    result = nl_processor.process("Show me all deployments")
    
    # Verify the result
    assert result == mock_response
    assert result["success"] is True
    assert "deployment-1" in result["output"]
    assert "deployment-2" in result["output"]
    
    # Verify the executor was called with the correct command
    nl_processor.executor.execute.assert_called_once_with("kubectl get deployments -A -o wide", None)

def test_process_query_with_namespace(nl_processor):
    """Test processing a query with a specific namespace"""
    # Mock the executor response
    mock_response = {
        "command": "kubectl get all -A -o wide",
        "output": "NAME READY STATUS RESTARTS AGE\npod-1 1/1 Running 0 1h",
        "error": None,
        "success": True
    }
    nl_processor.executor.execute.return_value = mock_response
    
    # Call the method
    result = nl_processor.process("Show me all resources", "kube-system")
    
    # Verify the result
    assert result == mock_response
    assert result["success"] is True
    assert "pod-1" in result["output"]
    
    # Verify the executor was called with the correct command and namespace
    nl_processor.executor.execute.assert_called_once_with("kubectl get all -A -o wide", "kube-system")

def test_process_query_unknown(nl_processor):
    """Test processing an unknown query"""
    # Mock the executor response
    mock_response = {
        "command": "kubectl get all -A -o wide",
        "output": "NAME READY STATUS RESTARTS AGE\npod-1 1/1 Running 0 1h",
        "error": None,
        "success": True
    }
    nl_processor.executor.execute.return_value = mock_response
    
    # Call the method
    result = nl_processor.process("Do something unknown")
    
    # Verify the result
    assert result == mock_response
    assert result["success"] is True
    
    # Verify the executor was called with the default command
    nl_processor.executor.execute.assert_called_once_with("kubectl get all -A -o wide", None)

def test_process_query_create_pod(nl_processor):
    """Test processing a query to create a pod"""
    # Mock the executor response
    mock_response = {
        "command": "kubectl get all -A -o wide",
        "output": "NAME READY STATUS RESTARTS AGE\npod-1 1/1 Running 0 1h",
        "error": None,
        "success": True
    }
    nl_processor.executor.execute.return_value = mock_response
    
    # Call the method with a query that doesn't contain "pod" or "deployment"
    result = nl_processor.process("Create a new container named test-container with image nginx:latest")
    
    # Verify the result
    assert result == mock_response
    assert result["success"] is True
    
    # Verify the executor was called with the default command since create is not supported
    nl_processor.executor.execute.assert_called_once_with("kubectl get all -A -o wide", None)

def test_process_query_delete_pod(nl_processor):
    """Test processing a query to delete a pod"""
    # Mock the executor response
    mock_response = {
        "command": "kubectl get all -A -o wide",
        "output": "NAME READY STATUS RESTARTS AGE\npod-1 1/1 Running 0 1h",
        "error": None,
        "success": True
    }
    nl_processor.executor.execute.return_value = mock_response
    
    # Call the method with a query that doesn't contain "pod" or "deployment"
    result = nl_processor.process("Remove the container named test-container")
    
    # Verify the result
    assert result == mock_response
    assert result["success"] is True
    
    # Verify the executor was called with the default command since delete is not supported
    nl_processor.executor.execute.assert_called_once_with("kubectl get all -A -o wide", None) 