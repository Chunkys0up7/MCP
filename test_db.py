from mcp.cache.redis_manager import RedisCacheManager
from mcp.db.session import SessionLocal
import pytest
import os


def test_postgres():
    print("\nTesting PostgreSQL...")
    db = SessionLocal()
    # TODO: Implement CRUD tests for PostgreSQL when operations are available
    print("PostgreSQL test placeholder - no operations implemented.")


@pytest.mark.skipif(
    os.environ.get("SKIP_REDIS_TESTS", "1") == "1",
    reason="Redis is not running or SKIP_REDIS_TESTS is set."
)
def test_redis():
    print("\nTesting Redis...")
    redis = RedisCacheManager()

    # Test basic key-value operations
    test_key = "test_key"
    test_value = {"message": "Hello, Redis!"}

    # Set and get
    redis.set(test_key, test_value)
    retrieved = redis.get(test_key)
    print(f"Retrieved from Redis: {retrieved}")

    # Test hash operations
    test_hash = "test_hash"
    test_hash_data = {"field1": "value1", "field2": {"nested": "data"}}

    redis.set_hash(test_hash, test_hash_data)
    retrieved_hash = redis.get_hash(test_hash)
    print(f"Retrieved hash from Redis: {retrieved_hash}")

    # Clean up
    redis.delete(test_key)
    redis.delete_hash(test_hash)
    print("Redis test completed successfully!")


if __name__ == "__main__":
    print("Starting database tests...")
    test_postgres()
    test_redis()
    print("\nAll tests completed!")
