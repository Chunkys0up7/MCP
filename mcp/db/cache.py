"""
Query Cache Module

This module provides query caching functionality using Redis.
It includes:

1. Cache configuration and connection management
2. Query result caching and retrieval
3. Cache invalidation strategies
4. Cache statistics and monitoring
"""

import hashlib
import json
import logging
from typing import Any, Dict, List, Optional

import redis
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class QueryCache:
    """
    Query cache manager using Redis.

    This class provides:
    1. Query result caching
    2. Cache invalidation
    3. Cache statistics
    4. Automatic cache expiration
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        default_ttl: int = 3600,  # 1 hour default TTL
    ):
        """
        Initialize the query cache.

        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            default_ttl: Default time-to-live for cache entries in seconds
        """
        self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.default_ttl = default_ttl

    def _generate_cache_key(self, query: str, params: Dict[str, Any]) -> str:
        """
        Generate a unique cache key for a query.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            str: Unique cache key
        """
        # Combine query and parameters into a single string
        key_string = f"{query}:{json.dumps(params, sort_keys=True)}"
        # Generate SHA-256 hash
        return f"query_cache:{hashlib.sha256(key_string.encode()).hexdigest()}"

    def get_cached_result(
        self, query: str, params: Dict[str, Any]
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached query result if available.

        Args:
            query: SQL query
            params: Query parameters

        Returns:
            Optional[List[Dict[str, Any]]]: Cached result or None if not found
        """
        try:
            cache_key = self._generate_cache_key(query, params)
            cached_data = self.redis.get(cache_key)

            if cached_data:
                logger.debug(f"Cache hit for query: {query}")
                return json.loads(cached_data)

            logger.debug(f"Cache miss for query: {query}")
            return None

        except Exception as e:
            logger.error(f"Error retrieving cached result: {str(e)}")
            return None

    def cache_result(
        self,
        query: str,
        params: Dict[str, Any],
        result: List[Dict[str, Any]],
        ttl: Optional[int] = None,
    ) -> None:
        """
        Cache query result.

        Args:
            query: SQL query
            params: Query parameters
            result: Query result to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        try:
            cache_key = self._generate_cache_key(query, params)
            ttl = ttl or self.default_ttl

            self.redis.setex(cache_key, ttl, json.dumps(result))
            logger.debug(f"Cached result for query: {query}")

        except Exception as e:
            logger.error(f"Error caching result: {str(e)}")

    def invalidate_cache(self, pattern: str = "*") -> None:
        """
        Invalidate cache entries matching the pattern.

        Args:
            pattern: Pattern to match cache keys (default: all keys)
        """
        try:
            keys = self.redis.keys(f"query_cache:{pattern}")
            if keys:
                self.redis.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache entries")
        except Exception as e:
            logger.error(f"Error invalidating cache: {str(e)}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict[str, Any]: Cache statistics
        """
        try:
            info = self.redis.info()
            return {
                "total_keys": info["db0"]["keys"],
                "used_memory": info["used_memory_human"],
                "connected_clients": info["connected_clients"],
                "uptime_days": info["uptime_in_days"],
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {}


def cached_query(
    cache: QueryCache,
    session: Session,
    query: str,
    params: Dict[str, Any],
    ttl: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Execute a query with caching.

    Args:
        cache: QueryCache instance
        session: Database session
        query: SQL query
        params: Query parameters
        ttl: Cache TTL in seconds

    Returns:
        List[Dict[str, Any]]: Query result
    """
    # Try to get from cache
    cached_result = cache.get_cached_result(query, params)
    if cached_result is not None:
        return cached_result

    # Execute query if not in cache
    try:
        result = session.execute(text(query), params)
        rows = [dict(row) for row in result]

        # Cache the result
        cache.cache_result(query, params, rows, ttl)

        return rows

    except Exception as e:
        logger.error(f"Error executing cached query: {str(e)}")
        raise
