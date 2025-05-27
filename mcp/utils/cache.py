import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional


class Cache:
    """Cache implementation for MCP."""

    def __init__(self, cache_dir: str = ".cache"):
        """Initialize cache.

        Args:
            cache_dir: Cache directory path
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, key: str) -> str:
        """Generate cache key.

        Args:
            key: Cache key

        Returns:
            Hashed cache key
        """
        return hashlib.md5(key.encode()).hexdigest()

    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path.

        Args:
            key: Cache key

        Returns:
            Cache file path
        """
        return self.cache_dir / f"{self._get_cache_key(key)}.json"

    def get(self, key: str, ttl: Optional[int] = None) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key
            ttl: Time to live in seconds

        Returns:
            Cached value or None if not found or expired
        """
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, "r") as f:
                data = json.load(f)

            # Check TTL
            if ttl is not None:
                timestamp = datetime.fromisoformat(data["timestamp"])
                if datetime.now() - timestamp > timedelta(seconds=ttl):
                    self.delete(key)
                    return None

            return data["value"]

        except (json.JSONDecodeError, KeyError):
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        cache_path = self._get_cache_path(key)

        data = {"value": value, "timestamp": datetime.now().isoformat()}

        with open(cache_path, "w") as f:
            json.dump(data, f)

    def delete(self, key: str):
        """Delete value from cache.

        Args:
            key: Cache key
        """
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_path.unlink()

    def clear(self):
        """Clear all cached values."""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Cache statistics
        """
        stats: Dict[str, Any] = {
            "total_files": 0,
            "total_size": 0,
            "oldest_entry": None,
            "newest_entry": None,
        }

        for cache_file in self.cache_dir.glob("*.json"):
            stats["total_files"] = int(stats["total_files"]) + 1
            stats["total_size"] = int(stats["total_size"]) + cache_file.stat().st_size

            try:
                with open(cache_file, "r") as f:
                    data = json.load(f)
                    timestamp = datetime.fromisoformat(data["timestamp"])

                    if (
                        stats["oldest_entry"] is None
                        or timestamp < stats["oldest_entry"]
                    ):
                        stats["oldest_entry"] = timestamp

                    if (
                        stats["newest_entry"] is None
                        or timestamp > stats["newest_entry"]
                    ):
                        stats["newest_entry"] = timestamp

            except (json.JSONDecodeError, KeyError):
                continue

        return stats


class FunctionCache:
    """Function result cache decorator."""

    def __init__(self, cache: Cache, ttl: Optional[int] = None):
        """Initialize function cache.

        Args:
            cache: Cache instance
            ttl: Time to live in seconds
        """
        self.cache = cache
        self.ttl = ttl

    def __call__(self, func):
        """Cache function results.

        Args:
            func: Function to cache

        Returns:
            Wrapped function
        """

        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_parts = [func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            key = "|".join(key_parts)

            # Try to get from cache
            result = self.cache.get(key, self.ttl)
            if result is not None:
                return result

            # Execute function
            result = func(*args, **kwargs)

            # Cache result
            self.cache.set(key, result, self.ttl)

            return result

        return wrapper
