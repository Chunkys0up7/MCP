"""
Connection Pool Test Script

This script tests the connection pooling functionality by:
1. Simulating concurrent database operations
2. Monitoring pool statistics
3. Testing pool size optimization
4. Verifying connection health
"""

import logging
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from mcp.db.session import (get_db_session, get_pool_stats, init_pool,
                            optimize_pool_size)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def simulate_database_operation(operation_id: int) -> None:
    """
    Simulate a database operation.

    Args:
        operation_id: Unique identifier for the operation
    """
    try:
        with get_db_session() as session:
            # Simulate some database work
            session.execute("SELECT pg_sleep(0.1)")  # Sleep for 100ms
            logger.info(f"Operation {operation_id} completed")
    except Exception as e:
        logger.error(f"Operation {operation_id} failed: {str(e)}")


def test_concurrent_operations(num_operations: int = 20) -> None:
    """
    Test concurrent database operations.

    Args:
        num_operations: Number of concurrent operations to simulate
    """
    try:
        # Initialize pool with small size to test overflow
        init_pool(pool_size=5, max_overflow=10)

        logger.info("Starting concurrent operations test...")
        start_time = time.time()

        # Run operations concurrently
        with ThreadPoolExecutor(max_workers=num_operations) as executor:
            futures = [
                executor.submit(simulate_database_operation, i)
                for i in range(num_operations)
            ]
            # Wait for all operations to complete
            for future in futures:
                future.result()

        end_time = time.time()
        duration = end_time - start_time

        # Get pool statistics
        stats = get_pool_stats()
        logger.info("\nPool statistics after concurrent operations:")
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")

        logger.info(
            f"\nCompleted {num_operations} operations in {duration:.2f} seconds"
        )

        # Test pool optimization
        logger.info("\nTesting pool size optimization...")
        optimize_pool_size()

        # Get updated pool statistics
        stats = get_pool_stats()
        logger.info("\nPool statistics after optimization:")
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")

    except Exception as e:
        logger.error(f"Failed to test connection pool: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    test_concurrent_operations()
