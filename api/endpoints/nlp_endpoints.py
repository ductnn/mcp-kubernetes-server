from mcp.server.fastmcp import FastMCP
from core.processor import NaturalLanguageProcessor

def register_nlp_endpoints(server: FastMCP, nl_processor: NaturalLanguageProcessor):
    """Register all natural language processing endpoints with the server"""
    
    @server.tool("process_query")
    async def process_query(query: str, namespace: str = None):
        return nl_processor.process(query, namespace) 