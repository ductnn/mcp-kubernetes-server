# Kubernetes MCP Server 

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A lightweight MCP server that provides natural language processing and API access to Kubernetes clusters, combining both kubectl commands and Kubernetes Python client.

https://github.com/user-attachments/assets/48e061cd-3e85-40ff-ab04-a1a2b9bbd152

## ✨ Features

- **Natural Language Interface**: Convert plain English queries to kubectl commands
- **Full CRUD Operations**:
  - 🆕 Create/Delete namespaces, pods, and deployments
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

**...Updating...**

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

## Usage with AI Assistants

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

## API Endpoints

### Pod Management
- `create_pod`: Create a new pod
- `get_pod`: Get pod details
- `update_pod_labels`: Update pod labels
- `delete_pod`: Delete a pod
- `list_pods`: List pods with optional filters
- `port_forward`: Forward local port to pod

### Deployment Management
- `create_deployment`: Create a new deployment with customizable parameters
- `get_deployment`: Get deployment details
- `update_deployment`: Update deployment configuration
- `delete_deployment`: Delete a deployment
- `list_deployments`: List deployments with optional filters
- `scale_deployment`: Scale a deployment to a specific number of replicas

### Namespace Management
- `create_namespace`: Create a new namespace

### Cluster Management
- `cluster_ping`: Check cluster connectivity

## 🤝 Contributing
- Fork the project
- Create your feature branch (git checkout -b feature/AmazingFeature)
- Commit changes (git commit -m 'Add some amazing feature')
- Push to branch (git push origin feature/AmazingFeature)
- Open a Pull Request
