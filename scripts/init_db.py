"""
Database Initialization Script

This script initializes the database for the MCP system.
It performs:

1. Database schema creation
2. Initial data seeding
3. Index creation
4. Constraint setup
5. Migration handling

Usage:
    ```bash
    # Initialize the database
    python scripts/init_db.py
    ```
"""

import logging
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """
    Main function to initialize the database.

    This function:
    1. Sets up the database connection
    2. Creates all tables
    3. Seeds initial data
    4. Handles any errors

    Raises:
        Exception: If database initialization fails
    """
    try:
        # Import here to ensure proper path setup
        from mcp.db.init_db import init_database

        # Initialize the database
        logger.info("Starting database initialization...")
        init_database()
        logger.info("Database initialized successfully!")

    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
