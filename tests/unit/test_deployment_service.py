import pytest
from unittest.mock import patch, MagicMock
from kubernetes.client.exceptions import ApiException
import json

def test_create_deployment_success(deployment_service):
    """Test successful deployment creation"""
    # Mock the Kubernetes API response
    mock_response = MagicMock()
    mock_response.status = MagicMock()
    deployment_service.apps_v1.create_namespaced_deployment.return_value = mock_response
    
    # Call the method
    result = deployment_service.create_deployment(
        name="test-deployment",
        namespace="default",
        image="nginx:latest",
        replicas=3,
        labels={"app": "test"},
        env_vars={"DB_HOST": "db.example.com"},
        container_port=80,
        resources={
            "requests": {"cpu": "100m", "memory": "128Mi"},
            "limits": {"cpu": "500m", "memory": "512Mi"}
        }
    )
    
    # Verify the result
    assert result["success"] is True
    assert "Deployment test-deployment created" in result["message"]
    
    # Verify the API was called correctly
    deployment_service.apps_v1.create_namespaced_deployment.assert_called_once()
    args = deployment_service.apps_v1.create_namespaced_deployment.call_args[1]
    assert args["namespace"] == "default"
    
    # Access the body object's attributes properly
    body = args["body"]
    assert body.metadata.name == "test-deployment"
    assert body.spec.replicas == 3
    assert body.spec.template.spec.containers[0].image == "nginx:latest"
    assert body.spec.template.spec.containers[0].env[0].name == "DB_HOST"
    assert body.spec.template.spec.containers[0].env[0].value == "db.example.com"
    assert body.spec.template.spec.containers[0].ports[0].container_port == 80
    assert body.spec.template.spec.containers[0].resources.requests["cpu"] == "100m"
    assert body.spec.template.spec.containers[0].resources.limits["memory"] == "512Mi"

def test_create_deployment_api_error(deployment_service):
    """Test deployment creation with API error"""
    # Mock the Kubernetes API error
    # Create a mock ApiException with a body attribute
    mock_exception = ApiException(status=409, reason="Conflict")
    mock_exception.body = '{"message": "Deployment already exists"}'
    deployment_service.apps_v1.create_namespaced_deployment.side_effect = mock_exception
    
    # Call the method
    result = deployment_service.create_deployment(
        name="test-deployment",
        namespace="default",
        image="nginx:latest"
    )
    
    # Verify the result
    assert result["success"] is False
    assert "Error executing command" in result["error"]
    
    # Verify the executor was called
    deployment_service._exec._error_result.assert_called_once()

def test_get_deployment_success(deployment_service):
    """Test successful deployment retrieval"""
    # Mock the Kubernetes API response
    mock_response = MagicMock()
    mock_response.metadata.name = "test-deployment"
    mock_response.spec.replicas = 3
    mock_response.status.available_replicas = 3
    mock_response.metadata.labels = {"app": "test"}
    mock_response.spec.selector.match_labels = {"app": "test"}
    deployment_service.apps_v1.read_namespaced_deployment.return_value = mock_response
    
    # Call the method
    result = deployment_service.get_deployment("test-deployment", "default")
    
    # Verify the result
    assert result["success"] is True
    assert result["deployment"]["name"] == "test-deployment"
    assert result["deployment"]["replicas"] == 3
    assert result["deployment"]["available"] == 3
    assert result["deployment"]["labels"] == {"app": "test"}
    assert result["deployment"]["selector"] == {"app": "test"}
    
    # Verify the API was called correctly
    args, kwargs = deployment_service.apps_v1.read_namespaced_deployment.call_args
    assert args[0] == "test-deployment"  # First positional argument is name
    assert args[1] == "default"  # Second positional argument is namespace

def test_update_deployment_success(deployment_service):
    """Test successful deployment update"""
    # Mock the Kubernetes API response
    mock_response = MagicMock()
    mock_response.status = MagicMock()
    deployment_service.apps_v1.patch_namespaced_deployment.return_value = mock_response
    
    # Call the method
    result = deployment_service.update_deployment(
        name="test-deployment",
        namespace="default",
        replicas=5,
        image="nginx:1.19",
        labels={"app": "test", "env": "prod"}
    )
    
    # Verify the result
    assert result["success"] is True
    assert "Deployment test-deployment updated" in result["message"]
    
    # Verify the API was called correctly
    deployment_service.apps_v1.patch_namespaced_deployment.assert_called_once()
    call_args = deployment_service.apps_v1.patch_namespaced_deployment.call_args[1]
    assert call_args["name"] == "test-deployment"
    assert call_args["namespace"] == "default"
    assert "spec" in call_args["body"]
    assert "metadata" in call_args["body"]
    assert "template" in call_args["body"]["spec"]

def test_delete_deployment_success(deployment_service):
    """Test successful deployment deletion"""
    # Call the method
    result = deployment_service.delete_deployment(
        name="test-deployment",
        namespace="default",
        grace_period=30
    )
    
    # Verify the result
    assert result["success"] is True
    assert "Deployment test-deployment scheduled for deletion" in result["message"]
    
    # Verify the API was called correctly
    deployment_service.apps_v1.delete_namespaced_deployment.assert_called_once_with(
        name="test-deployment",
        namespace="default",
        grace_period_seconds=30
    )

def test_list_deployments_success(deployment_service):
    """Test successful deployment listing"""
    # Mock the Kubernetes API response
    mock_deployment1 = MagicMock()
    mock_deployment1.metadata.name = "deployment-1"
    mock_deployment1.spec.replicas = 3
    mock_deployment1.status.available_replicas = 3
    mock_deployment1.metadata.labels = {"app": "test"}
    
    mock_deployment2 = MagicMock()
    mock_deployment2.metadata.name = "deployment-2"
    mock_deployment2.spec.replicas = 1
    mock_deployment2.status.available_replicas = 1
    mock_deployment2.metadata.labels = {"app": "api"}
    
    mock_response = MagicMock()
    mock_response.items = [mock_deployment1, mock_deployment2]
    deployment_service.apps_v1.list_namespaced_deployment.return_value = mock_response
    
    # Call the method
    result = deployment_service.list_deployments("default", "app=test")
    
    # Verify the result
    assert result["success"] is True
    assert len(result["deployments"]) == 2
    assert result["deployments"][0]["name"] == "deployment-1"
    assert result["deployments"][0]["replicas"] == 3
    assert result["deployments"][0]["available"] == 3
    assert result["deployments"][0]["labels"] == {"app": "test"}
    assert result["deployments"][1]["name"] == "deployment-2"
    assert result["deployments"][1]["replicas"] == 1
    assert result["deployments"][1]["available"] == 1
    assert result["deployments"][1]["labels"] == {"app": "api"}
    
    # Verify the API was called correctly
    deployment_service.apps_v1.list_namespaced_deployment.assert_called_once_with(
        namespace="default",
        label_selector="app=test"
    )

def test_scale_deployment_success(deployment_service):
    """Test successful deployment scaling"""
    # Mock the Kubernetes API response
    mock_response = MagicMock()
    mock_response.status = MagicMock()
    deployment_service.apps_v1.patch_namespaced_deployment_scale.return_value = mock_response
    
    # Call the method
    result = deployment_service.scale_deployment(
        name="test-deployment",
        replicas=5,
        namespace="default"
    )
    
    # Verify the result
    assert result["success"] is True
    assert "Deployment test-deployment scaled to 5 replicas" in result["message"]
    
    # Verify the API was called correctly
    deployment_service.apps_v1.patch_namespaced_deployment_scale.assert_called_once_with(
        name="test-deployment",
        namespace="default",
        body={"spec": {"replicas": 5}}
    ) 