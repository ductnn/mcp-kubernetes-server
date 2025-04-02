#!/usr/bin/env python3
import asyncio
import sys
import logging
from server import setup_server

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)

async def main():
    try:
        server = await setup_server()
        await server.run_stdio_async()
    except Exception as e:
        logging.critical(f"Server failed: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
        sys.exit(0)