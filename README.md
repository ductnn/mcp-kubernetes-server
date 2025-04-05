# Kubernetes MCP Server 

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A lightweight MCP server that provides natural language processing and API access to Kubernetes clusters, combining both kubectl commands and Kubernetes Python client.

https://github.com/user-attachments/assets/48e061cd-3e85-40ff-ab04-a1a2b9bbd152

## ✨ Features

- **Natural Language Interface**: Convert plain English queries to kubectl commands
  - List pods and deployments across all namespaces
  - Fallback to general resource listing for unsupported queries
- **Full CRUD Operations**:
  - 🆕 Create/Delete namespaces, pods, and deployments via API endpoints
  - 🔍 Inspect cluster resources
  - ✏️ Modify labels, annotations, and deployment configurations
  - 🗑️ Graceful deletion
  - 📊 Scale deployments
- **Dual Execution Mode**:
  - `kubectl` command integration
  - Kubernetes Python client (official SDK)
- **Advanced Capabilities**:
  - Namespace validation (DNS-1123 compliant)
  - Label filtering
  - Grace period control
  - Automatic command fallback
  - Resource management (CPU, memory)
  - Environment variable configuration

## 📦 Installation

### Prerequisites
- Python 3.11+
- Kubernetes cluster access
- `kubectl` configured locally
- [UV](https://github.com/astral-sh/uv) installed

```bash
# Clone repository
git clone https://github.com/ductnn/mcp-kubernetes-server.git 
cd mcp-kubernetes-server

# Create virtual environment
uv venv .venv

# Activate (Unix)
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

## 🚀 Usage

### Natural Language Processing

The server supports basic natural language queries for listing resources:

```python
# List all pods
result = nl_processor.process("Show me all pods")

# List all deployments
result = nl_processor.process("Show me all deployments")

# Query with namespace
result = nl_processor.process("Show me all resources", "kube-system")
```

For more complex operations, use the dedicated API endpoints:

```python
# Create a pod
pod_service.create_pod(
    name="my-pod",
    namespace="default",
    image="nginx:latest",
    labels={"app": "my-app"}
)

# Create a deployment
deployment_service.create_deployment(
    name="my-deployment",
    namespace="default",
    image="nginx:latest",
    replicas=3
)

# Delete a namespace
namespace_service.delete("my-namespace", force=True)
```

### API Endpoints

The server provides RESTful endpoints for all operations:

- `/api/pods` - Pod operations
- `/api/deployments` - Deployment operations
- `/api/namespaces` - Namespace operations
- `/api/cluster` - Cluster operations
- `/api/nlp` - Natural language processing

## 🤖 Usage with AI Assistants

### Claude Desktop

- Open your **Claude Desktop** and choose `Settings` -> choose mode `Developer` -> `Edit config` and open file `claude_desktop_config.json` and edit:

```json
{
    "mcpServers": {
        "kubernetes": {
            "command": "/path-to-your-uv/uv",
            "args": [
                "--directory",
                "/path-you-project/", // Example for me /Users/ductn/mcp-kubernetes-server
                "run",
                "main.py"
            ]
        }
    }
}
```

- Then, restart your Claude Desktop and play :)

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_pod_service.py

# Run with coverage
pytest --cov=.
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
