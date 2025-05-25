"""
Database Optimizations

This module provides database optimization utilities for the MCP system.
It includes:

1. Index definitions for common query patterns
2. Query optimization functions
3. Database monitoring utilities
4. Connection pooling configuration
"""

import logging
from typing import Any, Dict, List

from sqlalchemy import Index, text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# Define indexes for common query patterns
INDEXES = {
    "mcp_configurations": [
        Index("idx_mcp_config_name", "name"),
        Index("idx_mcp_config_type", "type"),
        Index("idx_mcp_config_created_at", "created_at"),
    ],
    "mcp_chains": [
        Index("idx_mcp_chain_name", "name"),
        Index("idx_mcp_chain_version", "version"),
        Index("idx_mcp_chain_parent", "parent_chain"),
    ],
    "chain_sessions": [
        Index("idx_chain_session_id", "session_id"),
        Index("idx_chain_session_created_at", "created_at"),
    ],
    "mcp_permissions": [
        Index("idx_mcp_permissions_user", "user_id"),
        Index("idx_mcp_permissions_chain", "chain_id"),
        Index("idx_mcp_permissions_access", "access_level"),
    ],
    "audit_logs": [
        Index("idx_audit_logs_user", "user_id"),
        Index("idx_audit_logs_action", "action_type"),
        Index("idx_audit_logs_target", "target_id"),
        Index("idx_audit_logs_created_at", "created_at"),
    ],
}


def create_indexes(session: Session) -> None:
    """
    Create all defined indexes in the database.

    Args:
        session: Database session
    """
    try:
        for table_name, indexes in INDEXES.items():
            for index in indexes:
                index.create(session.get_bind())
        logger.info("Successfully created all database indexes")
    except Exception as e:
        logger.error(f"Failed to create indexes: {str(e)}")
        raise


def analyze_query_performance(session: Session, query: str) -> Dict[str, Any]:
    """
    Analyze the performance of a SQL query using EXPLAIN ANALYZE.

    Args:
        session: Database session
        query: SQL query to analyze

    Returns:
        Dict[str, Any]: Query analysis results
    """
    try:
        result = session.execute(text(f"EXPLAIN ANALYZE {query}"))
        return {"query": query, "plan": [row[0] for row in result]}
    except Exception as e:
        logger.error(f"Failed to analyze query: {str(e)}")
        raise


def get_table_statistics(session: Session, table_name: str) -> Dict[str, Any]:
    """
    Get statistics for a specific table.

    Args:
        session: Database session
        table_name: Name of the table to analyze

    Returns:
        Dict[str, Any]: Table statistics
    """
    try:
        result = session.execute(
            text(
                f"""
            SELECT 
                schemaname,
                relname,
                n_live_tup,
                n_dead_tup,
                last_vacuum,
                last_autovacuum,
                last_analyze,
                last_autoanalyze
            FROM pg_stat_user_tables
            WHERE relname = :table_name
        """
            ),
            {"table_name": table_name},
        )

        row = result.fetchone()
        if row:
            return {
                "schema": row[0],
                "table": row[1],
                "live_tuples": row[2],
                "dead_tuples": row[3],
                "last_vacuum": row[4],
                "last_autovacuum": row[5],
                "last_analyze": row[6],
                "last_autoanalyze": row[7],
            }
        return {}
    except Exception as e:
        logger.error(f"Failed to get table statistics: {str(e)}")
        raise


def get_index_usage(session: Session) -> List[Dict[str, Any]]:
    """
    Get statistics about index usage.

    Args:
        session: Database session

    Returns:
        List[Dict[str, Any]]: Index usage statistics
    """
    try:
        result = session.execute(
            text(
                """
            SELECT
                schemaname,
                relname as table_name,
                indexrelname as index_name,
                idx_scan as number_of_scans,
                idx_tup_read as tuples_read,
                idx_tup_fetch as tuples_fetched
            FROM pg_stat_user_indexes
            ORDER BY idx_scan DESC
        """
            )
        )

        return [
            {
                "schema": row[0],
                "table": row[1],
                "index": row[2],
                "scans": row[3],
                "tuples_read": row[4],
                "tuples_fetched": row[5],
            }
            for row in result
        ]
    except Exception as e:
        logger.error(f"Failed to get index usage statistics: {str(e)}")
        raise
