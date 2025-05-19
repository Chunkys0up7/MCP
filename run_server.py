import uvicorn
import socket
import sys
import time
from typing import Optional
import logging
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_port_in_use(port: int) -> bool:
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port: int = 8000, max_attempts: int = 10) -> Optional[int]:
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        if not is_port_in_use(port):
            return port
    return None

def start_server(port: int, max_retries: int = 3, retry_delay: int = 2) -> None:
    """Start the FastAPI server with retry logic."""
    for attempt in range(max_retries):
        try:
            logger.info(f"Starting server on port {port} (attempt {attempt + 1}/{max_retries})...")
            uvicorn.run(
                "mcp.api.main:app",
                host="127.0.0.1",
                port=port,
                reload=True,
                reload_dirs=["mcp"],
                reload_delay=1.0,
                log_level="info",
                timeout_keep_alive=30,  # Increase keep-alive timeout
                limit_concurrency=100,  # Limit concurrent connections
                backlog=2048  # Increase connection queue size
            )
            break
        except Exception as e:
            logger.error(f"Error starting server: {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error("Failed to start server after multiple attempts")
                sys.exit(1)

def main():
    """Main entry point for the server."""
    # Run MCP API test before starting the server
    try:
        result = subprocess.run([sys.executable, "-m", "pytest", "tests/test_api_execute.py", "--maxfail=1", "--disable-warnings", "-v"], capture_output=True, text=True)
        if result.returncode != 0:
            print("\n[ERROR] MCP API test failed on startup:\n", result.stdout, result.stderr)
            sys.exit(1)
        else:
            print("[INFO] MCP API test passed on startup.")
    except Exception as e:
        print(f"[ERROR] Exception running MCP API test: {e}")
        sys.exit(1)

    # Try to find an available port
    port = find_available_port()
    if port is None:
        logger.error("Could not find an available port. Please check if any other services are running.")
        sys.exit(1)

    try:
        start_server(port)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 