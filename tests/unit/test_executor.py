import pytest
from unittest.mock import patch, MagicMock
import subprocess
import json
from core.executor import KubernetesCommandExecutor

def test_execute_success():
    """Test successful command execution"""
    # Create a mock executor
    executor = KubernetesCommandExecutor()
    
    # Mock subprocess.run
    with patch("subprocess.run") as mock_run:
        # Configure the mock
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "Command executed successfully"
        mock_process.stderr = ""
        mock_run.return_value = mock_process
        
        # Call the method
        result = executor.execute("kubectl get pods")
        
        # Verify the result
        assert result["success"] is True
        assert result["output"] == "Command executed successfully"
        assert result["error"] is None
        assert result["command"] == "kubectl get pods"
        
        # Verify subprocess.run was called correctly
        mock_run.assert_called_once()
        call_args = mock_run.call_args[1]
        assert call_args["shell"] is True
        assert call_args["capture_output"] is True
        assert call_args["text"] is True

def test_execute_failure():
    """Test command execution failure"""
    # Create a mock executor
    executor = KubernetesCommandExecutor()
    
    # Mock subprocess.run
    with patch("subprocess.run") as mock_run:
        # Configure the mock
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stdout = ""
        mock_process.stderr = "Command failed"
        mock_run.return_value = mock_process
        
        # Call the method
        result = executor.execute("kubectl get pods")
        
        # Verify the result
        assert result["success"] is False
        assert result["output"] == ""
        assert result["error"] == "Command failed"
        assert result["command"] == "kubectl get pods"
        
        # Verify subprocess.run was called correctly
        mock_run.assert_called_once()

def test_execute_timeout():
    """Test command execution timeout"""
    # Create a mock executor
    executor = KubernetesCommandExecutor()
    
    # Mock subprocess.run
    with patch("subprocess.run") as mock_run:
        # Configure the mock to raise a timeout exception
        mock_run.side_effect = subprocess.TimeoutExpired("kubectl get pods", 30)
        
        # Call the method
        result = executor.execute("kubectl get pods")
        
        # Verify the result
        assert result["success"] is False
        assert result["output"] == ""
        assert result["error"] == "Command timed out"
        assert result["command"] == "kubectl get pods"
        
        # Verify subprocess.run was called correctly
        mock_run.assert_called_once()

def test_error_result():
    """Test error result creation"""
    # Create a mock executor
    executor = KubernetesCommandExecutor()
    
    # Call the method
    result = executor._error_result("kubectl get pods", "Command failed")
    
    # Verify the result
    assert result["success"] is False
    assert result["output"] == ""
    assert result["error"] == "Command failed"
    assert result["command"] == "kubectl get pods" 