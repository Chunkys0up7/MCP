# Query Cache

## Overview
The Query Cache is a high-performance caching system for database queries in the MCP platform. It uses Redis to store and retrieve query results, providing significant performance improvements for frequently executed queries.

## Features

### Query Caching
- Automatic query result caching
- Configurable cache TTL
- Cache key generation
- Result serialization

### Cache Management
- Cache invalidation
- Pattern-based clearing
- Cache statistics
- Memory monitoring

### Performance
- Fast result retrieval
- Efficient key generation
- Memory optimization
- Connection pooling

### Monitoring
- Cache hit/miss tracking
- Memory usage statistics
- Connection monitoring
- Performance metrics

## Usage

### Basic Setup
```python
from mcp.db.cache import QueryCache

# Initialize the cache
cache = QueryCache(
    host="localhost",
    port=6379,
    default_ttl=3600  # 1 hour
)

# Use cached query
from mcp.db.cache import cached_query

result = cached_query(
    cache=cache,
    session=db_session,
    query="SELECT * FROM users WHERE status = :status",
    params={"status": "active"}
)
```

### Cache Management
```python
# Invalidate specific cache entries
cache.invalidate_cache("users:*")

# Get cache statistics
stats = cache.get_cache_stats()
print(f"Total keys: {stats['total_keys']}")
print(f"Memory usage: {stats['used_memory']}")
```

### Custom TTL
```python
# Cache with custom TTL
result = cached_query(
    cache=cache,
    session=db_session,
    query="SELECT * FROM products",
    params={},
    ttl=1800  # 30 minutes
)
```

## Configuration

### Redis Connection
- `host`: Redis server host
- `port`: Redis server port
- `db`: Redis database number
- `default_ttl`: Default cache duration

### Cache Settings
- Key prefix
- Serialization format
- Error handling
- Logging level

## Implementation Details

### Cache Operations
1. **Query Caching**
   - Key generation
   - Result serialization
   - TTL management
   - Error handling

2. **Cache Retrieval**
   - Key lookup
   - Result deserialization
   - Cache hit/miss handling
   - Error recovery

3. **Cache Invalidation**
   - Pattern matching
   - Key deletion
   - Batch operations
   - Error handling

### Performance Features
1. **Key Generation**
   - SHA-256 hashing
   - Parameter normalization
   - Prefix management
   - Collision prevention

2. **Result Handling**
   - JSON serialization
   - Type preservation
   - Memory optimization
   - Error recovery

3. **Cache Management**
   - TTL enforcement
   - Memory monitoring
   - Connection management
   - Error handling

## Testing

Run the test suite:
```bash
python scripts/test_query_cache.py
```

The test suite verifies:
- Cache operations
- Query execution
- Error handling
- Performance metrics

## Integration

### Database Systems
- PostgreSQL
- MySQL
- SQLite
- Other SQLAlchemy-supported databases

### Caching Systems
- Redis
- Redis Cluster
- Redis Sentinel
- Custom Redis configurations

## Best Practices

1. **Cache Configuration**
   - Set appropriate TTL
   - Monitor memory usage
   - Configure error handling
   - Enable logging

2. **Query Caching**
   - Cache frequently used queries
   - Use appropriate TTL
   - Handle cache misses
   - Monitor performance

3. **Resource Management**
   - Monitor memory usage
   - Handle connection errors
   - Implement cleanup
   - Track statistics

## Troubleshooting

### Common Issues

1. **Cache Misses**
   - Solution: Check key generation
   - Verify TTL settings
   - Review invalidation
   - Monitor patterns

2. **Memory Issues**
   - Solution: Monitor usage
   - Adjust TTL
   - Implement cleanup
   - Review patterns

3. **Connection Problems**
   - Solution: Check Redis
   - Verify configuration
   - Monitor connections
   - Handle errors

## Contributing

1. Follow the project's coding standards
2. Add tests for new features
3. Update documentation
4. Submit pull requests

## License
MIT 