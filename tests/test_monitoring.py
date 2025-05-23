import pytest
import time
from unittest.mock import patch
from mcp.utils.monitoring import Metrics, Monitor, ExecutionTracker, APIRequestTracker

@pytest.fixture
def metrics():
    """Create metrics instance."""
    with patch('prometheus_client.start_http_server'):
        return Metrics(port=0)

@pytest.fixture
def monitor(metrics):
    """Create monitor instance."""
    return Monitor(metrics)

def test_metrics_initialization(metrics):
    """Test metrics initialization."""
    assert metrics.execution_counter is not None
    assert metrics.execution_duration is not None
    assert metrics.error_counter is not None
    assert metrics.memory_usage is not None
    assert metrics.cpu_usage is not None
    assert metrics.cache_hits is not None
    assert metrics.cache_misses is not None
    assert metrics.api_requests is not None
    assert metrics.api_duration is not None

def test_execution_tracking(monitor, metrics):
    """Test execution tracking."""
    # Track successful execution
    with monitor.track_execution('test_type') as tracker:
        time.sleep(0.1)
    
    # Verify metrics
    assert metrics.execution_counter._value.get(('test_type', 'success')) == 1
    assert metrics.execution_duration._sum.get(('test_type',)) > 0
    
    # Track failed execution
    with pytest.raises(Exception):
        with monitor.track_execution('test_type') as tracker:
            raise Exception("Test error")
    
    # Verify metrics
    assert metrics.execution_counter._value.get(('test_type', 'error')) == 1

def test_api_request_tracking(monitor, metrics):
    """Test API request tracking."""
    # Track successful request
    with monitor.track_api_request('/test', 'GET') as tracker:
        time.sleep(0.1)
    
    # Verify metrics
    assert metrics.api_requests._value.get(('/test', 'GET', '200')) == 1
    assert metrics.api_duration._sum.get(('/test', 'GET')) > 0
    
    # Track failed request
    with pytest.raises(Exception):
        with monitor.track_api_request('/test', 'GET'):
            raise Exception("Test error")
    
    # Verify metrics
    assert metrics.api_requests._value.get(('/test', 'GET', '500')) == 1

def test_cache_tracking(monitor, metrics):
    """Test cache tracking."""
    # Track cache hit
    monitor.track_cache_access(True)
    assert metrics.cache_hits._value.get() == 1
    
    # Track cache miss
    monitor.track_cache_access(False)
    assert metrics.cache_misses._value.get() == 1

def test_error_tracking(monitor, metrics):
    """Test error tracking."""
    # Track error
    monitor.track_error('test_error', 'test_type')
    assert metrics.error_counter._value.get(('test_type', 'test_error')) == 1

def test_resource_metrics(monitor, metrics):
    """Test resource metrics."""
    # Update resource metrics
    monitor.update_resource_metrics(1024, 50.0)
    assert metrics.memory_usage._value.get() == 1024
    assert metrics.cpu_usage._value.get() == 50.0

def test_execution_tracker_context(metrics):
    """Test execution tracker context manager."""
    tracker = ExecutionTracker(metrics, 'test_type')
    
    # Enter context
    with tracker as t:
        assert t is tracker
        time.sleep(0.1)
    
    # Verify metrics
    assert metrics.execution_counter._value.get(('test_type', 'success')) == 1
    assert metrics.execution_duration._sum.get(('test_type',)) > 0

def test_api_request_tracker_context(metrics):
    """Test API request tracker context manager."""
    tracker = APIRequestTracker(metrics, '/test', 'GET')
    
    # Enter context
    with tracker as t:
        assert t is tracker
        time.sleep(0.1)
    
    # Verify metrics
    assert metrics.api_requests._value.get(('/test', 'GET', '200')) == 1
    assert metrics.api_duration._sum.get(('/test', 'GET')) > 0

def test_execution_tracker_error(metrics):
    """Test execution tracker error handling."""
    tracker = ExecutionTracker(metrics, 'test_type')
    
    # Enter context with error
    with pytest.raises(Exception):
        with tracker:
            raise Exception("Test error")
    
    # Verify metrics
    assert metrics.execution_counter._value.get(('test_type', 'error')) == 1

def test_api_request_tracker_error(metrics):
    """Test API request tracker error handling."""
    tracker = APIRequestTracker(metrics, '/test', 'GET')
    
    # Enter context with error
    with pytest.raises(Exception):
        with tracker:
            raise Exception("Test error")
    
    # Verify metrics
    assert metrics.api_requests._value.get(('/test', 'GET', '500')) == 1

def test_metrics_labels(metrics):
    """Test metrics labels."""
    # Test execution counter labels
    metrics.execution_counter.labels(type='test_type', status='success').inc()
    assert metrics.execution_counter._value.get(('test_type', 'success')) == 1
    
    # Test error counter labels
    metrics.error_counter.labels(type='test_type', error_type='test_error').inc()
    assert metrics.error_counter._value.get(('test_type', 'test_error')) == 1
    
    # Test API request labels
    metrics.api_requests.labels(endpoint='/test', method='GET', status='200').inc()
    assert metrics.api_requests._value.get(('/test', 'GET', '200')) == 1 