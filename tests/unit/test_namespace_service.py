import pytest
from unittest.mock import patch, MagicMock
from kubernetes.client.exceptions import ApiException
import json

def test_create_namespace_success(namespace_service):
    """Test successful namespace creation"""
    # Mock the executor response
    mock_response = {
        "command": "kubectl create namespace testnamespace",
        "output": "namespace/testnamespace created",
        "error": None,
        "success": True,
        "message": "Command executed successfully"  # Include default message
    }
    namespace_service._exec.execute.return_value = mock_response
    
    # Call the method
    result = namespace_service.create("testnamespace")
    
    # Verify the result
    assert result["success"] is True
    assert "namespace/testnamespace created" in result["output"]
    
    # Verify the executor was called correctly
    namespace_service._exec.execute.assert_called_once_with("kubectl create namespace testnamespace")

def test_create_namespace_api_error(namespace_service):
    """Test namespace creation with API error"""
    # Mock the executor error response
    mock_response = {
        "command": "kubectl create namespace testnamespace",
        "output": "",
        "error": "Error executing command",  # Use default error message
        "success": False
    }
    namespace_service._exec.execute.return_value = mock_response
    
    # Call the method
    result = namespace_service.create("testnamespace")
    
    # Verify the result
    assert result["success"] is False
    assert result["error"] == "Error executing command"
    
    # Verify the executor was called
    namespace_service._exec.execute.assert_called_once_with("kubectl create namespace testnamespace")

def test_create_namespace_invalid_name(namespace_service):
    """Test namespace creation with invalid name"""
    # Mock the _error_result method
    error_response = {
        "command": "",
        "output": "",
        "error": "Error executing command",  # Use default error message
        "success": False
    }
    namespace_service._exec._error_result.return_value = error_response
    
    # Call the method with an invalid name
    result = namespace_service.create("invalid/namespace")
    
    # Verify the result
    assert result["success"] is False
    assert result["error"] == "Error executing command"
    
    # Verify the executor was not called
    namespace_service._exec.execute.assert_not_called()
    # Verify _error_result was called with the correct message
    namespace_service._exec._error_result.assert_called_once_with("", "Invalid namespace name") 