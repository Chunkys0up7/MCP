
def test_redis_kv_and_hash(redis_client):
    """Test Redis key-value and hash operations."""
    # Test basic key-value operations
    test_key = "test_key"
    test_value = {"message": "Hello, Redis!"}
    redis_client.set(test_key, test_value)
    retrieved = redis_client.get(test_key)
    assert retrieved == test_value
    
    # Test hash operations
    test_hash = "test_hash"
    test_hash_data = {
        "field1": "value1",
        "field2": {"nested": "data"}
    }
    redis_client.set_hash(test_hash, test_hash_data)
    retrieved_hash = redis_client.get_hash(test_hash)
    assert retrieved_hash["field1"] == "value1"
    assert retrieved_hash["field2"] == {"nested": "data"}
    # Clean up
    redis_client.delete(test_key)
    redis_client.delete_hash(test_hash) 