import pytest
import time
from datetime import datetime
from mcp.utils.cache import Cache, FunctionCache

@pytest.fixture
def cache_dir(tmp_path):
    """Create temporary cache directory."""
    return tmp_path / "cache"

@pytest.fixture
def cache(cache_dir):
    """Create cache instance."""
    return Cache(str(cache_dir))

def test_cache_initialization(cache_dir):
    """Test cache initialization."""
    cache = Cache(str(cache_dir))
    assert cache.cache_dir.exists()
    assert cache.cache_dir.is_dir()

def test_cache_set_get(cache):
    """Test setting and getting cache values."""
    # Set value
    cache.set("test_key", "test_value")
    
    # Get value
    value = cache.get("test_key")
    assert value == "test_value"
    
    # Get non-existent value
    value = cache.get("non_existent")
    assert value is None

def test_cache_ttl(cache):
    """Test cache TTL."""
    # Set value with TTL
    cache.set("test_key", "test_value", ttl=1)
    
    # Get value immediately
    value = cache.get("test_key", ttl=1)
    assert value == "test_value"
    
    # Wait for TTL to expire
    time.sleep(1.1)
    
    # Get expired value
    value = cache.get("test_key", ttl=1)
    assert value is None

def test_cache_delete(cache):
    """Test cache deletion."""
    # Set value
    cache.set("test_key", "test_value")
    
    # Delete value
    cache.delete("test_key")
    
    # Get deleted value
    value = cache.get("test_key")
    assert value is None

def test_cache_clear(cache):
    """Test cache clearing."""
    # Set multiple values
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    
    # Clear cache
    cache.clear()
    
    # Verify cache is empty
    assert len(list(cache.cache_dir.glob("*.json"))) == 0

def test_cache_stats(cache):
    """Test cache statistics."""
    # Set values
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    
    # Get stats
    stats = cache.get_stats()
    
    assert stats['total_files'] == 2
    assert stats['total_size'] > 0
    assert isinstance(stats['oldest_entry'], datetime)
    assert isinstance(stats['newest_entry'], datetime)
    assert stats['oldest_entry'] <= stats['newest_entry']

def test_function_cache(cache):
    """Test function caching."""
    # Create cached function
    @FunctionCache(cache, ttl=1)
    def test_func(x, y):
        return x + y
    
    # First call
    result1 = test_func(1, 2)
    assert result1 == 3
    
    # Second call (should use cache)
    result2 = test_func(1, 2)
    assert result2 == 3
    
    # Wait for TTL to expire
    time.sleep(1.1)
    
    # Third call (should recompute)
    result3 = test_func(1, 2)
    assert result3 == 3

def test_function_cache_different_args(cache):
    """Test function caching with different arguments."""
    @FunctionCache(cache)
    def test_func(x, y):
        return x + y
    
    # Call with different arguments
    result1 = test_func(1, 2)
    result2 = test_func(2, 3)
    
    assert result1 == 3
    assert result2 == 5

def test_function_cache_kwargs(cache):
    """Test function caching with keyword arguments."""
    @FunctionCache(cache)
    def test_func(x, y, z=0):
        return x + y + z
    
    # Call with different keyword arguments
    result1 = test_func(1, 2, z=3)
    result2 = test_func(1, 2, z=4)
    
    assert result1 == 6
    assert result2 == 7

def test_cache_corruption(cache):
    """Test handling of corrupted cache files."""
    # Create corrupted cache file
    cache_path = cache._get_cache_path("test_key")
    with open(cache_path, 'w') as f:
        f.write("invalid json")
    
    # Try to get corrupted value
    value = cache.get("test_key")
    assert value is None

def test_cache_key_collision(cache):
    """Test cache key collision handling."""
    # Set values with different keys that hash to the same value
    # This is unlikely but possible with MD5
    key1 = "test_key1"
    key2 = "test_key2"
    
    # Force collision by using the same hash
    cache._get_cache_key = lambda x: "collision"
    
    # Set values
    cache.set(key1, "value1")
    cache.set(key2, "value2")
    
    # Get values
    value1 = cache.get(key1)
    value2 = cache.get(key2)
    
    # One of the values should be None due to collision
    assert value1 is None or value2 is None 