import pytest
from unittest.mock import patch, MagicMock
from kubernetes.client.exceptions import ApiException
import json

def test_create_pod_success(pod_service):
    """Test successful pod creation"""
    # Mock the Kubernetes API response
    mock_response = MagicMock()
    mock_response.status = MagicMock()
    mock_response.status.pod_ip = "10.0.0.1"
    pod_service.core_v1.create_namespaced_pod.return_value = mock_response
    
    # Call the method
    result = pod_service.create_pod(
        name="test-pod",
        namespace="default",
        image="nginx:latest",
        labels={"app": "test"}
    )
    
    # Verify the result
    assert result["success"] is True
    assert result["pod_ip"] == "10.0.0.1"
    assert "Pod test-pod created" in result["message"]
    
    # Verify the API was called correctly
    pod_service.core_v1.create_namespaced_pod.assert_called_once()
    call_args = pod_service.core_v1.create_namespaced_pod.call_args[1]
    assert call_args["namespace"] == "default"
    assert call_args["body"]["metadata"]["name"] == "test-pod"
    assert call_args["body"]["spec"]["containers"][0]["image"] == "nginx:latest"

def test_create_pod_api_error(pod_service):
    """Test pod creation with API error"""
    # Mock the Kubernetes API error
    # Create a mock ApiException with a body attribute
    mock_exception = ApiException(status=409, reason="Conflict")
    mock_exception.body = '{"message": "Pod already exists"}'
    pod_service.core_v1.create_namespaced_pod.side_effect = mock_exception
    
    # Call the method
    result = pod_service.create_pod(
        name="test-pod",
        namespace="default",
        image="nginx:latest"
    )
    
    # Verify the result
    assert result["success"] is False
    assert "Error executing command" in result["error"]
    
    # Verify the executor was called
    pod_service._exec._error_result.assert_called_once()

def test_get_pod_success(pod_service):
    """Test successful pod retrieval"""
    # Create a mock response that exactly matches what the get_pod method expects
    mock_response = MagicMock()
    
    # Set up metadata
    mock_metadata = MagicMock()
    mock_metadata.name = "test-pod"
    mock_metadata.labels = {"app": "test"}
    mock_response.metadata = mock_metadata
    
    # Set up status
    mock_status = MagicMock()
    mock_status.phase = "Running"
    mock_status.pod_ip = "10.0.0.1"
    mock_response.status = mock_status
    
    # Set up spec
    mock_spec = MagicMock()
    mock_spec.node_name = "node-1"
    mock_response.spec = mock_spec
    
    # Set the return value
    pod_service.core_v1.read_namespaced_pod.return_value = mock_response
    
    # Call the method
    result = pod_service.get_pod("test-pod", "default")
    
    # Print the result for debugging
    print(f"Result: {result}")
    
    # Verify the result
    assert result["success"] is True
    assert "pod" in result
    assert result["pod"]["name"] == "test-pod"
    assert result["pod"]["status"] == "Running"
    assert result["pod"]["ip"] == "10.0.0.1"
    assert result["pod"]["node"] == "node-1"
    assert result["pod"]["labels"] == {"app": "test"}
    
    # Verify the API was called correctly
    pod_service.core_v1.read_namespaced_pod.assert_called_once()
    # Check positional arguments instead of keyword arguments
    args, kwargs = pod_service.core_v1.read_namespaced_pod.call_args
    assert args[0] == "test-pod"  # First positional argument is name
    assert args[1] == "default"   # Second positional argument is namespace

def test_get_pod_api_error(pod_service):
    """Test pod retrieval with API error"""
    # Mock the Kubernetes API error
    pod_service.core_v1.read_namespaced_pod.side_effect = ApiException(status=404)
    
    # Call the method
    result = pod_service.get_pod("test-pod", "default")
    
    # Verify the executor was called with the correct command
    pod_service._exec.execute.assert_called_once_with(
        "kubectl get pod test-pod -n default -o json"
    )

def test_update_pod_labels_success(pod_service):
    """Test successful pod label update"""
    # Mock the Kubernetes API response
    mock_response = MagicMock()
    mock_response.metadata.labels = {"app": "test", "env": "prod"}
    pod_service.core_v1.patch_namespaced_pod.return_value = mock_response
    
    # Call the method
    result = pod_service.update_pod_labels(
        name="test-pod",
        labels={"env": "prod"},
        namespace="default"
    )
    
    # Verify the result
    assert result["success"] is True
    assert "Labels updated for pod test-pod" in result["message"]
    assert result["new_labels"] == {"app": "test", "env": "prod"}
    
    # Verify the API was called correctly
    pod_service.core_v1.patch_namespaced_pod.assert_called_once()
    call_args = pod_service.core_v1.patch_namespaced_pod.call_args[1]
    assert call_args["name"] == "test-pod"
    assert call_args["namespace"] == "default"
    assert call_args["body"]["metadata"]["labels"] == {"env": "prod"}

def test_delete_pod_success(pod_service):
    """Test successful pod deletion"""
    # Call the method
    result = pod_service.delete_pod(
        name="test-pod",
        namespace="default",
        grace_period=30
    )
    
    # Verify the result
    assert result["success"] is True
    assert "Pod test-pod scheduled for deletion" in result["message"]
    
    # Verify the API was called correctly
    pod_service.core_v1.delete_namespaced_pod.assert_called_once_with(
        name="test-pod",
        namespace="default",
        grace_period_seconds=30
    )

def test_list_pods_success(pod_service):
    """Test successful pod listing"""
    # Mock the Kubernetes API response
    mock_pod1 = MagicMock()
    mock_pod1.metadata.name = "pod-1"
    mock_pod1.status.phase = "Running"
    mock_pod1.status.pod_ip = "10.0.0.1"
    
    mock_pod2 = MagicMock()
    mock_pod2.metadata.name = "pod-2"
    mock_pod2.status.phase = "Pending"
    mock_pod2.status.pod_ip = None
    
    mock_response = MagicMock()
    mock_response.items = [mock_pod1, mock_pod2]
    pod_service.core_v1.list_namespaced_pod.return_value = mock_response
    
    # Call the method
    result = pod_service.list_pods("default", "app=test")
    
    # Verify the result
    assert result["success"] is True
    assert len(result["pods"]) == 2
    assert result["pods"][0]["name"] == "pod-1"
    assert result["pods"][0]["status"] == "Running"
    assert result["pods"][0]["ip"] == "10.0.0.1"
    assert result["pods"][1]["name"] == "pod-2"
    assert result["pods"][1]["status"] == "Pending"
    assert result["pods"][1]["ip"] is None
    
    # Verify the API was called correctly
    pod_service.core_v1.list_namespaced_pod.assert_called_once_with(
        namespace="default",
        label_selector="app=test"
    ) 