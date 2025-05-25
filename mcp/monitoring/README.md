# System Monitor

## Overview
The System Monitor is a comprehensive monitoring and metrics collection system for the MCP platform. It provides real-time system health monitoring, performance metrics collection, alerting capabilities, and integration with Prometheus for metrics visualization.

## Features

### System Metrics
- CPU usage monitoring
- Memory utilization tracking
- Disk space monitoring
- Network I/O statistics
- Custom metric support

### Alerting System
- Multi-level severity alerts
- Configurable thresholds
- Alert history tracking
- Custom alert rules

### Prometheus Integration
- Metrics export
- Custom metric types
- Real-time monitoring
- Historical data collection

### Performance Monitoring
- Request latency tracking
- Error rate monitoring
- Resource utilization
- Custom performance metrics

## Usage

### Basic Setup
```python
from mcp.monitoring.system_monitor import SystemMonitor

# Initialize the monitor
monitor = SystemMonitor(port=9090)

# Start monitoring
monitor.start()

# Create custom metrics
monitor.create_custom_metric(
    name="custom_metric",
    description="Custom metric description",
    metric_type=MetricType.GAUGE
)

# Update metrics
monitor.update_metric("custom_metric", 42.0)

# Get alerts
alerts = monitor.get_alerts(severity=AlertSeverity.WARNING)
```

### Alert Management
```python
# Get all alerts
all_alerts = monitor.get_alerts()

# Get critical alerts
critical_alerts = monitor.get_alerts(severity=AlertSeverity.CRITICAL)

# Clear alerts
monitor.clear_alerts()
```

## Metric Types

### System Metrics
- CPU usage percentage
- Memory utilization
- Disk space usage
- Network I/O bytes
- Process statistics

### Application Metrics
- Request count
- Request latency
- Error count
- Custom metrics
- Performance indicators

### Custom Metrics
- Gauge metrics
- Counter metrics
- Histogram metrics
- Custom aggregations

## Alert System

### Severity Levels
- INFO: Informational messages
- WARNING: Potential issues
- ERROR: System errors
- CRITICAL: Critical failures

### Alert Sources
- System metrics
- Application metrics
- Custom metrics
- External sources

### Alert Management
- Alert creation
- Alert filtering
- Alert history
- Alert clearing

## Implementation Details

### Metric Collection
1. **System Metrics**
   - CPU monitoring
   - Memory tracking
   - Disk monitoring
   - Network statistics

2. **Application Metrics**
   - Request tracking
   - Performance monitoring
   - Error tracking
   - Custom metrics

3. **Custom Metrics**
   - Metric creation
   - Value updates
   - Type management
   - Aggregation

### Alert Generation
1. **Threshold Monitoring**
   - CPU thresholds
   - Memory thresholds
   - Disk thresholds
   - Custom thresholds

2. **Alert Creation**
   - Severity assignment
   - Message generation
   - Source tracking
   - Timestamp recording

3. **Alert Management**
   - Alert storage
   - Alert retrieval
   - Alert filtering
   - Alert clearing

## Testing

Run the test suite:
```bash
python scripts/test_system_monitor.py
```

The test suite verifies:
- Metric collection
- Alert generation
- Custom metrics
- Prometheus integration

## Integration

### Prometheus
- Metrics export
- Data collection
- Visualization
- Alerting

### Monitoring Systems
- Grafana integration
- Alert management
- Dashboard creation
- Data analysis

## Best Practices

1. **Metric Management**
   - Regular monitoring
   - Threshold adjustment
   - Metric cleanup
   - Performance optimization

2. **Alert Handling**
   - Timely response
   - Alert prioritization
   - Resolution tracking
   - Documentation

3. **Resource Usage**
   - Efficient collection
   - Storage management
   - Performance impact
   - Scalability

## Troubleshooting

### Common Issues

1. **Metric Collection**
   - Solution: Check system access
   - Verify permissions
   - Review collection intervals
   - Monitor resource usage

2. **Alert Generation**
   - Solution: Verify thresholds
   - Check alert rules
   - Review alert history
   - Test alert delivery

3. **Prometheus Integration**
   - Solution: Check connectivity
   - Verify metrics format
   - Review configuration
   - Test data flow

## Contributing

1. Follow the project's coding standards
2. Add tests for new features
3. Update documentation
4. Submit pull requests

## License
MIT 