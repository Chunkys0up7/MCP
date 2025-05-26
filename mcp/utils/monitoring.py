import time

from prometheus_client import Counter, Gauge, Histogram, start_http_server

from mcp.utils.logging import log_error


class Metrics:
    """Metrics collection for MCP."""

    def __init__(self, port: int = 8000):
        """Initialize metrics.

        Args:
            port: Prometheus metrics server port
        """
        # Start Prometheus metrics server
        start_http_server(port)

        # Execution metrics
        self.execution_counter = Counter(
            "mcp_executions_total", "Total number of MCP executions", ["type", "status"]
        )

        self.execution_duration = Histogram(
            "mcp_execution_duration_seconds",
            "MCP execution duration in seconds",
            ["type"],
        )

        # Error metrics
        self.error_counter = Counter(
            "mcp_errors_total", "Total number of MCP errors", ["type", "error_type"]
        )

        # Resource metrics
        self.memory_usage = Gauge("mcp_memory_usage_bytes", "MCP memory usage in bytes")

        self.cpu_usage = Gauge("mcp_cpu_usage_percent", "MCP CPU usage percentage")

        # Cache metrics
        self.cache_hits = Counter("mcp_cache_hits_total", "Total number of cache hits")

        self.cache_misses = Counter(
            "mcp_cache_misses_total", "Total number of cache misses"
        )

        # API metrics
        self.api_requests = Counter(
            "mcp_api_requests_total",
            "Total number of API requests",
            ["endpoint", "method", "status"],
        )

        self.api_duration = Histogram(
            "mcp_api_duration_seconds",
            "API request duration in seconds",
            ["endpoint", "method"],
        )


class Monitor:
    """Monitoring for MCP."""

    def __init__(self, metrics: Metrics):
        """Initialize monitor.

        Args:
            metrics: Metrics instance
        """
        self.metrics = metrics

    def track_execution(self, mcp_type: str):
        """Track MCP execution.

        Args:
            mcp_type: MCP type

        Returns:
            Execution tracker
        """
        return ExecutionTracker(self.metrics, mcp_type)

    def track_api_request(self, endpoint: str, method: str):
        """Track API request.

        Args:
            endpoint: API endpoint
            method: HTTP method

        Returns:
            API request tracker
        """
        return APIRequestTracker(self.metrics, endpoint, method)

    def track_cache_access(self, hit: bool):
        """Track cache access.

        Args:
            hit: Whether cache hit occurred
        """
        if hit:
            self.metrics.cache_hits.inc()
        else:
            self.metrics.cache_misses.inc()

    def track_error(self, error_type: str, mcp_type: str):
        """Track error.

        Args:
            error_type: Error type
            mcp_type: MCP type
        """
        self.metrics.error_counter.labels(type=mcp_type, error_type=error_type).inc()

    def update_resource_metrics(self, memory_bytes: int, cpu_percent: float):
        """Update resource metrics.

        Args:
            memory_bytes: Memory usage in bytes
            cpu_percent: CPU usage percentage
        """
        self.metrics.memory_usage.set(memory_bytes)
        self.metrics.cpu_usage.set(cpu_percent)


class ExecutionTracker:
    """MCP execution tracker."""

    def __init__(self, metrics: Metrics, mcp_type: str):
        """Initialize execution tracker.

        Args:
            metrics: Metrics instance
            mcp_type: MCP type
        """
        self.metrics = metrics
        self.mcp_type = mcp_type
        self.start_time = time.time()

    def __enter__(self):
        """Enter context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        duration = time.time() - self.start_time

        # Record duration
        self.metrics.execution_duration.labels(type=self.mcp_type).observe(duration)

        # Record execution
        if exc_type is None:
            self.metrics.execution_counter.labels(
                type=self.mcp_type, status="success"
            ).inc()
        else:
            self.metrics.execution_counter.labels(
                type=self.mcp_type, status="error"
            ).inc()

            # Log error
            log_error(
                exc_val,
                {"type": "execution", "mcp_type": self.mcp_type, "duration": duration},
            )


class APIRequestTracker:
    """API request tracker."""

    def __init__(self, metrics: Metrics, endpoint: str, method: str):
        """Initialize API request tracker.

        Args:
            metrics: Metrics instance
            endpoint: API endpoint
            method: HTTP method
        """
        self.metrics = metrics
        self.endpoint = endpoint
        self.method = method
        self.start_time = time.time()

    def __enter__(self):
        """Enter context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        duration = time.time() - self.start_time

        # Record duration
        self.metrics.api_duration.labels(
            endpoint=self.endpoint, method=self.method
        ).observe(duration)

        # Record request
        if exc_type is None:
            self.metrics.api_requests.labels(
                endpoint=self.endpoint, method=self.method, status="200"
            ).inc()
        else:
            self.metrics.api_requests.labels(
                endpoint=self.endpoint, method=self.method, status="500"
            ).inc()

            # Log error
            log_error(
                exc_val,
                {
                    "type": "api_request",
                    "endpoint": self.endpoint,
                    "method": self.method,
                    "duration": duration,
                },
            )
