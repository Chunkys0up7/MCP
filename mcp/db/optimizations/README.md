# Database Optimizations

## Overview
The Database Optimizations module provides comprehensive tools for optimizing PostgreSQL database performance in the MCP platform. It includes index management, query analysis, performance monitoring, and optimization utilities.

## Features

### Index Management
- Predefined indexes for common patterns
- Automatic index creation
- Index usage statistics
- Performance monitoring

### Query Analysis
- EXPLAIN ANALYZE integration
- Query plan analysis
- Performance metrics
- Optimization suggestions

### Table Statistics
- Live/dead tuple tracking
- Vacuum statistics
- Analyze history
- Table health monitoring

### Performance Monitoring
- Index usage tracking
- Query performance metrics
- Table statistics
- Optimization recommendations

## Usage

### Basic Setup
```python
from mcp.db.optimizations import create_indexes, analyze_query_performance

# Create predefined indexes
create_indexes(db_session)

# Analyze query performance
analysis = analyze_query_performance(
    session=db_session,
    query="SELECT * FROM users WHERE status = 'active'"
)
```

### Table Statistics
```python
from mcp.db.optimizations import get_table_statistics

# Get table statistics
stats = get_table_statistics(
    session=db_session,
    table_name="users"
)
print(f"Live tuples: {stats['live_tuples']}")
print(f"Last vacuum: {stats['last_vacuum']}")
```

### Index Usage
```python
from mcp.db.optimizations import get_index_usage

# Get index usage statistics
usage = get_index_usage(db_session)
for index in usage:
    print(f"Index {index['index']} used {index['scans']} times")
```

## Index Definitions

### Configuration Indexes
- `idx_mcp_config_name`: Name lookup
- `idx_mcp_config_type`: Type filtering
- `idx_mcp_config_created_at`: Temporal queries

### Chain Indexes
- `idx_mcp_chain_name`: Name lookup
- `idx_mcp_chain_version`: Version filtering
- `idx_mcp_chain_parent`: Parent relationship

### Session Indexes
- `idx_chain_session_id`: Session lookup
- `idx_chain_session_created_at`: Temporal queries

### Permission Indexes
- `idx_mcp_permissions_user`: User access
- `idx_mcp_permissions_chain`: Chain access
- `idx_mcp_permissions_access`: Access level

### Audit Indexes
- `idx_audit_logs_user`: User activity
- `idx_audit_logs_action`: Action filtering
- `idx_audit_logs_target`: Target tracking
- `idx_audit_logs_created_at`: Temporal queries

## Implementation Details

### Index Management
1. **Index Creation**
   - Predefined indexes
   - Automatic creation
   - Error handling
   - Logging

2. **Index Monitoring**
   - Usage tracking
   - Performance metrics
   - Health checks
   - Optimization

3. **Index Maintenance**
   - Vacuum scheduling
   - Analyze operations
   - Reindexing
   - Cleanup

### Query Analysis
1. **Performance Analysis**
   - Query planning
   - Execution metrics
   - Resource usage
   - Optimization

2. **Statistics Collection**
   - Table statistics
   - Index usage
   - Query patterns
   - Performance trends

3. **Monitoring**
   - Real-time metrics
   - Historical data
   - Trend analysis
   - Alerts

## Testing

Run the test suite:
```bash
python scripts/test_database_optimizations.py
```

The test suite verifies:
- Index creation
- Query analysis
- Statistics collection
- Performance monitoring

## Integration

### Database Systems
- PostgreSQL
- PostgreSQL extensions
- Custom configurations
- Monitoring tools

### Monitoring Systems
- Prometheus metrics
- Grafana dashboards
- Alert systems
- Logging systems

## Best Practices

1. **Index Management**
   - Regular maintenance
   - Usage monitoring
   - Performance tuning
   - Cleanup

2. **Query Optimization**
   - Regular analysis
   - Plan review
   - Index usage
   - Performance tuning

3. **Monitoring**
   - Regular checks
   - Trend analysis
   - Alert configuration
   - Performance tracking

## Troubleshooting

### Common Issues

1. **Index Performance**
   - Solution: Review usage
   - Check statistics
   - Optimize queries
   - Monitor growth

2. **Query Performance**
   - Solution: Analyze plans
   - Check indexes
   - Optimize queries
   - Monitor resources

3. **Statistics Issues**
   - Solution: Run analyze
   - Check vacuum
   - Update statistics
   - Monitor growth

## Contributing

1. Follow the project's coding standards
2. Add tests for new features
3. Update documentation
4. Submit pull requests

## License
MIT 