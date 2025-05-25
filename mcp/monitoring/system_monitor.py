"""
System Monitoring and Metrics Collection

This module provides comprehensive system monitoring, metrics collection,
and alerting capabilities for the MCP system.
"""

import logging
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple

import psutil
from prometheus_client import Counter, Gauge, Histogram, start_http_server

logger = logging.getLogger(__name__)


class MetricType(Enum):
    GAUGE = "gauge"
    COUNTER = "counter"
    HISTOGRAM = "histogram"


class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    severity: AlertSeverity
    message: str
    source: str
    timestamp: datetime
    metric_name: Optional[str] = None
    metric_value: Optional[float] = None


class SystemMonitor:
    def __init__(self, port: int = 9090):
        """Initialize the system monitor with Prometheus metrics."""
        self.port = port
        self.alerts: List[Alert] = []
        self.monitoring_thread: Optional[threading.Thread] = None
        self.is_running = False

        # System metrics
        self.cpu_usage = Gauge("system_cpu_usage", "CPU usage percentage")
        self.memory_usage = Gauge("system_memory_usage", "Memory usage percentage")
        self.disk_usage = Gauge("system_disk_usage", "Disk usage percentage")
        self.network_io = Gauge("system_network_io", "Network I/O bytes")

        # Application metrics
        self.request_count = Counter("app_request_count", "Total number of requests")
        self.request_latency = Histogram("app_request_latency", "Request latency in seconds")
        self.error_count = Counter("app_error_count", "Total number of errors")

        # Custom metrics registry
        self.custom_metrics: Dict[str, Gauge] = {}

    def start(self):
        """Start the monitoring server and metrics collection."""
        try:
            start_http_server(self.port)
            self.is_running = True
            self.monitoring_thread = threading.Thread(target=self._collect_metrics)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            logger.info(f"System monitoring started on port {self.port}")
        except Exception as e:
            logger.error(f"Failed to start system monitoring: {e}")
            raise

    def stop(self):
        """Stop the monitoring server and metrics collection."""
        self.is_running = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        logger.info("System monitoring stopped")

    def _collect_metrics(self):
        """Collect system metrics periodically."""
        while self.is_running:
            try:
                # Collect CPU metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                self.cpu_usage.set(cpu_percent)
                self._check_cpu_threshold(cpu_percent)

                # Collect memory metrics
                memory = psutil.virtual_memory()
                self.memory_usage.set(memory.percent)
                self._check_memory_threshold(memory.percent)

                # Collect disk metrics
                disk = psutil.disk_usage("/")
                self.disk_usage.set(disk.percent)
                self._check_disk_threshold(disk.percent)

                # Collect network metrics
                net_io = psutil.net_io_counters()
                self.network_io.set(net_io.bytes_sent + net_io.bytes_recv)

                time.sleep(5)  # Collect metrics every 5 seconds
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")

    def create_custom_metric(self, name: str, description: str, metric_type: MetricType) -> None:
        """Create a new custom metric."""
        if name in self.custom_metrics:
            raise ValueError(f"Metric {name} already exists")

        if metric_type == MetricType.GAUGE:
            self.custom_metrics[name] = Gauge(name, description)
        elif metric_type == MetricType.COUNTER:
            self.custom_metrics[name] = Counter(name, description)
        elif metric_type == MetricType.HISTOGRAM:
            self.custom_metrics[name] = Histogram(name, description)

    def update_metric(self, name: str, value: float) -> None:
        """Update a custom metric value."""
        if name not in self.custom_metrics:
            raise ValueError(f"Metric {name} does not exist")

        metric = self.custom_metrics[name]
        if isinstance(metric, Gauge):
            metric.set(value)
        elif isinstance(metric, Counter):
            metric.inc(value)
        elif isinstance(metric, Histogram):
            metric.observe(value)

    def _check_cpu_threshold(self, cpu_percent: float) -> None:
        """Check CPU usage against thresholds and generate alerts."""
        if cpu_percent > 90:
            self._create_alert(
                AlertSeverity.CRITICAL,
                f"CPU usage is critically high: {cpu_percent}%",
                "system",
                "cpu_usage",
                cpu_percent,
            )
        elif cpu_percent > 80:
            self._create_alert(
                AlertSeverity.WARNING,
                f"CPU usage is high: {cpu_percent}%",
                "system",
                "cpu_usage",
                cpu_percent,
            )

    def _check_memory_threshold(self, memory_percent: float) -> None:
        """Check memory usage against thresholds and generate alerts."""
        if memory_percent > 90:
            self._create_alert(
                AlertSeverity.CRITICAL,
                f"Memory usage is critically high: {memory_percent}%",
                "system",
                "memory_usage",
                memory_percent,
            )
        elif memory_percent > 80:
            self._create_alert(
                AlertSeverity.WARNING,
                f"Memory usage is high: {memory_percent}%",
                "system",
                "memory_usage",
                memory_percent,
            )

    def _check_disk_threshold(self, disk_percent: float) -> None:
        """Check disk usage against thresholds and generate alerts."""
        if disk_percent > 90:
            self._create_alert(
                AlertSeverity.CRITICAL,
                f"Disk usage is critically high: {disk_percent}%",
                "system",
                "disk_usage",
                disk_percent,
            )
        elif disk_percent > 80:
            self._create_alert(
                AlertSeverity.WARNING,
                f"Disk usage is high: {disk_percent}%",
                "system",
                "disk_usage",
                disk_percent,
            )

    def _create_alert(
        self,
        severity: AlertSeverity,
        message: str,
        source: str,
        metric_name: Optional[str] = None,
        metric_value: Optional[float] = None,
    ) -> None:
        """Create and log a new alert."""
        alert = Alert(
            severity=severity,
            message=message,
            source=source,
            timestamp=datetime.now(),
            metric_name=metric_name,
            metric_value=metric_value,
        )
        self.alerts.append(alert)
        logger.warning(f"Alert: {alert.severity.value} - {alert.message}")

    def get_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get alerts, optionally filtered by severity."""
        if severity:
            return [alert for alert in self.alerts if alert.severity == severity]
        return self.alerts

    def clear_alerts(self):
        """Clear all alerts."""
        self.alerts = []
