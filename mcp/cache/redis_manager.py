import json
import os
from typing import Any, Dict, List, Optional

import redis
from dotenv import load_dotenv

load_dotenv()


class RedisCacheManager:
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        db: Optional[int] = None,
        password: Optional[str] = None,
    ):
        """Initialize Redis cache manager."""

        redis_host = host if host is not None else os.getenv("REDIS_HOST", "localhost")
        redis_port = port if port is not None else int(os.getenv("REDIS_PORT", "6379"))
        redis_db = db if db is not None else int(os.getenv("REDIS_DB", "0"))
        redis_password = (
            password if password is not None else os.getenv("REDIS_PASSWORD")
        )

        self.redis = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=redis_password,
            decode_responses=True,
        )

    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set a value in the cache."""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            self.redis.set(key, value)
            if expire:
                self.redis.expire(key, expire)
            return True
        except Exception as e:
            print(f"Error setting cache: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the cache."""
        try:
            value = self.redis.get(key)
            if value is None:
                return default
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except Exception as e:
            print(f"Error getting cache: {e}")
            return default

    def delete(self, key: str) -> bool:
        """Delete a value from the cache."""
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            print(f"Error deleting cache: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if a key exists in the cache."""
        try:
            return bool(self.redis.exists(key))
        except Exception as e:
            print(f"Error checking cache: {e}")
            return False

    def set_hash(self, name: str, mapping: Dict[str, Any]) -> None:
        """Set hash fields to multiple values."""
        processed_mapping = {
            k: json.dumps(v) if isinstance(v, (dict, list)) else v
            for k, v in mapping.items()
        }
        if hasattr(self.redis, "hmset"):
            self.redis.hmset(name, processed_mapping)
        else:
            self.redis.hset(name, mapping=processed_mapping)

    def get_hash(self, name: str) -> Dict[str, Any]:
        """Get a hash from the cache."""
        try:
            hash_data = self.redis.hgetall(name)
            if not hash_data:
                return {}

            # Try to parse JSON values
            processed_data = {}
            for key, value in hash_data.items():
                try:
                    processed_data[key] = json.loads(value)
                except json.JSONDecodeError:
                    processed_data[key] = value
            return processed_data
        except Exception as e:
            print(f"Error getting hash cache: {e}")
            return {}

    def delete_hash(self, name: str, *keys: str) -> bool:
        """Delete keys from a hash."""
        try:
            if keys:
                return bool(self.redis.hdel(name, *keys))
            return bool(self.redis.delete(name))
        except Exception as e:
            print(f"Error deleting hash cache: {e}")
            return False

    def set_list(
        self, name: str, values: List[Any], expire: Optional[int] = None
    ) -> bool:
        """Set a list in the cache."""
        try:
            # Convert values to JSON strings if they are dicts or lists
            processed_values = [
                json.dumps(v) if isinstance(v, (dict, list)) else v for v in values
            ]
            self.redis.delete(name)  # Clear existing list
            if processed_values:
                self.redis.rpush(name, *processed_values)
            if expire:
                self.redis.expire(name, expire)
            return True
        except Exception as e:
            print(f"Error setting list cache: {e}")
            return False

    def get_list(self, name: str, start: int = 0, end: int = -1) -> List[Any]:
        """Get a list from the cache."""
        try:
            values = self.redis.lrange(name, start, end)
            if not values:
                return []

            # Try to parse JSON values
            processed_values = []
            for value in values:
                try:
                    processed_values.append(json.loads(value))
                except json.JSONDecodeError:
                    processed_values.append(value)
            return processed_values
        except Exception as e:
            print(f"Error getting list cache: {e}")
            return []

    def add_to_list(self, name: str, value: Any) -> bool:
        """Add a value to a list."""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            return bool(self.redis.rpush(name, value))
        except Exception as e:
            print(f"Error adding to list cache: {e}")
            return False

    def remove_from_list(self, name: str, value: Any) -> bool:
        """Remove a value from a list."""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            return bool(self.redis.lrem(name, 0, value))
        except Exception as e:
            print(f"Error removing from list cache: {e}")
            return False

    def clear(self) -> bool:
        """Clear all cache data."""
        try:
            return bool(self.redis.flushdb())
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False

    def ping(self) -> bool:
        """Check if Redis server is available."""
        try:
            return bool(self.redis.ping())
        except Exception as e:
            print(f"Error pinging Redis: {e}")
            return False
