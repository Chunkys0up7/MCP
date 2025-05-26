from mcp.cache.redis_manager import RedisCacheManager
from mcp.db.session import SessionLocal


def test_postgres():
    print("\nTesting PostgreSQL...")
    db = SessionLocal()

    # Create a test configuration
    test_config = {"type": "prompt", "template": "Test template", "model": "test-model"}

    config = ops.create_configuration(
        name="Test Config", type="prompt", config=test_config
    )
    print(f"Created configuration: {config.id}")

    # Retrieve the configuration
    retrieved = ops.get_configuration(config.id)
    print(f"Retrieved configuration: {retrieved.name}")
    print(f"Config data: {retrieved.config}")

    # Clean up
    ops.delete_configuration(config.id)
    print("PostgreSQL test completed successfully!")


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
