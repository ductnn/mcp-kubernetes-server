# Kubernetes MCP Server 

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A lightweight MCP server that provides natural language processing and API access to Kubernetes clusters, combining both kubectl commands and Kubernetes Python client.

## ✨ Features

- **Natural Language Interface**: Convert plain English queries to kubectl commands
- **Full CRUD Operations**:
  - 🆕 Create/Delete namespaces and pods
  - 🔍 Inspect cluster resources
  - ✏️ Modify labels and annotations
  - 🗑️ Graceful deletion
- **Dual Execution Mode**:
  - `kubectl` command integration
  - Kubernetes Python client (official SDK)
- **Advanced Capabilities**:
  - Namespace validation (DNS-1123 compliant)
  - Label filtering
  - Grace period control
  - Automatic command fallback

## 📦 Installation

### Prerequisites
- Python 3.8+
- Kubernetes cluster access
- `kubectl` configured locally
- [UV](https://github.com/astral-sh/uv) installed



```bash
# Clone repository
git clone https://github.com/ductnn/mcp-kubernetes-server.git 
cd mcp-kubernetes-server

# Create virtual environment (uv >= 0.1.8 required)
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

## 🤝 Contributing
- Fork the project
- Create your feature branch (git checkout -b feature/AmazingFeature)
- Commit changes (git commit -m 'Add some amazing feature')
- Push to branch (git push origin feature/AmazingFeature)
- Open a Pull Request