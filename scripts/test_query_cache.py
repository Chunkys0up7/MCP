"""
Query Cache Test Script

This script tests the query caching functionality by:
1. Executing sample queries with and without caching
2. Measuring performance improvements
3. Testing cache invalidation
4. Collecting cache statistics
"""

import sys
import os
import time
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from mcp.db.session import get_db_session
from mcp.db.cache import QueryCache, cached_query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_query_performance():
    """Test query performance with and without caching."""
    try:
        # Initialize cache and session
        cache = QueryCache()
        session = get_db_session()
        
        # Sample queries to test
        queries = [
            {
                'name': 'Get MCP Configurations',
                'query': 'SELECT * FROM mcp_configurations ORDER BY created_at DESC LIMIT 10',
                'params': {}
            },
            {
                'name': 'Get Recent Audit Logs',
                'query': 'SELECT * FROM audit_logs WHERE created_at > NOW() - INTERVAL \'1 day\'',
                'params': {}
            },
            {
                'name': 'Get User Permissions',
                'query': 'SELECT * FROM mcp_permissions WHERE user_id = :user_id',
                'params': {'user_id': '00000000-0000-0000-0000-000000000000'}
            }
        ]
        
        # Test each query
        for query_info in queries:
            logger.info(f"\nTesting query: {query_info['name']}")
            
            # First run (no cache)
            start_time = time.time()
            result1 = cached_query(cache, session, query_info['query'], query_info['params'])
            first_run_time = time.time() - start_time
            logger.info(f"First run time: {first_run_time:.4f} seconds")
            
            # Second run (should use cache)
            start_time = time.time()
            result2 = cached_query(cache, session, query_info['query'], query_info['params'])
            second_run_time = time.time() - start_time
            logger.info(f"Second run time: {second_run_time:.4f} seconds")
            
            # Calculate improvement
            improvement = (first_run_time - second_run_time) / first_run_time * 100
            logger.info(f"Performance improvement: {improvement:.2f}%")
            
            # Verify results match
            assert result1 == result2, "Cached result doesn't match original result"
        
        # Test cache invalidation
        logger.info("\nTesting cache invalidation...")
        cache.invalidate_cache()
        
        # Get cache statistics
        stats = cache.get_cache_stats()
        logger.info("\nCache statistics:")
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")
        
        logger.info("\nQuery cache testing completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to test query cache: {str(e)}")
        sys.exit(1)
    finally:
        session.close()

if __name__ == "__main__":
    test_query_performance() 