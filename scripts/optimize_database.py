"""
Database Optimization Script

This script applies database optimizations including:
1. Creating optimized indexes
2. Analyzing query performance
3. Collecting database statistics
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from mcp.db.session import get_db_session
from mcp.db.optimizations import (
    create_indexes,
    analyze_query_performance,
    get_table_statistics,
    get_index_usage
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function to run database optimizations."""
    try:
        # Get database session
        session = get_db_session()
        
        # Create indexes
        logger.info("Creating database indexes...")
        create_indexes(session)
        
        # Get table statistics
        tables = [
            'mcp_configurations',
            'mcp_chains',
            'chain_sessions',
            'mcp_permissions',
            'audit_logs'
        ]
        
        logger.info("Collecting table statistics...")
        for table in tables:
            stats = get_table_statistics(session, table)
            logger.info(f"Statistics for {table}:")
            for key, value in stats.items():
                logger.info(f"  {key}: {value}")
        
        # Get index usage statistics
        logger.info("Collecting index usage statistics...")
        index_stats = get_index_usage(session)
        for stat in index_stats:
            logger.info(f"Index {stat['index']} on {stat['table']}:")
            logger.info(f"  Scans: {stat['scans']}")
            logger.info(f"  Tuples read: {stat['tuples_read']}")
            logger.info(f"  Tuples fetched: {stat['tuples_fetched']}")
        
        logger.info("Database optimization completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to optimize database: {str(e)}")
        sys.exit(1)
    finally:
        session.close()

if __name__ == "__main__":
    main() 