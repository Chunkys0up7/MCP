import uvicorn
import os
from pathlib import Path

def main():
    # Get the absolute path to the project root
    project_root = Path(__file__).parent.absolute()
    
    # Set working directory to project root
    os.chdir(project_root)
    
    # Configure uvicorn
    config = uvicorn.Config(
        "mcp.api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[str(project_root / "mcp")],
        log_level="info",
        workers=1
    )
    
    # Start server
    server = uvicorn.Server(config)
    server.run()

if __name__ == "__main__":
    main() 