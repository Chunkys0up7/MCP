"""
Test script for the system monitoring functionality.
"""

import logging
import os
import sys
import time

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.monitoring.system_monitor import (AlertSeverity, MetricType,
                                           SystemMonitor)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_metric_collection():
    """Test basic metric collection functionality."""
    monitor = SystemMonitor(port=9091)  # Use a different port for testing

    try:
        # Start monitoring
        monitor.start()
        logger.info("Started system monitoring")

        # Wait for some metrics to be collected
        time.sleep(10)

        # Check if alerts were generated
        alerts = monitor.get_alerts()
        logger.info(f"Generated alerts: {len(alerts)}")
        for alert in alerts:
            logger.info(f"- {alert.severity.value}: {alert.message}")

        return len(alerts) > 0
    finally:
        monitor.stop()
        logger.info("Stopped system monitoring")


def test_custom_metrics():
    """Test custom metric creation and updates."""
    monitor = SystemMonitor(port=9092)  # Use a different port for testing

    try:
        # Create custom metrics
        monitor.create_custom_metric(
            "test_gauge", "Test gauge metric", MetricType.GAUGE
        )
        monitor.create_custom_metric(
            "test_counter", "Test counter metric", MetricType.COUNTER
        )
        monitor.create_custom_metric(
            "test_histogram", "Test histogram metric", MetricType.HISTOGRAM
        )

        # Update metrics
        monitor.update_metric("test_gauge", 42.0)
        monitor.update_metric("test_counter", 1.0)
        monitor.update_metric("test_histogram", 0.5)

        logger.info("Custom metrics created and updated")
        return True
    except Exception as e:
        logger.error(f"Error testing custom metrics: {e}")
        return False
    finally:
        monitor.stop()


def test_alert_filtering():
    """Test alert filtering by severity."""
    monitor = SystemMonitor(port=9093)  # Use a different port for testing

    try:
        # Generate some alerts
        monitor._create_alert(AlertSeverity.INFO, "Test info alert", "test")
        monitor._create_alert(AlertSeverity.WARNING, "Test warning alert", "test")
        monitor._create_alert(AlertSeverity.ERROR, "Test error alert", "test")

        # Test filtering
        info_alerts = monitor.get_alerts(AlertSeverity.INFO)
        warning_alerts = monitor.get_alerts(AlertSeverity.WARNING)
        error_alerts = monitor.get_alerts(AlertSeverity.ERROR)

        assert len(info_alerts) == 1, "Should have one info alert"
        assert len(warning_alerts) == 1, "Should have one warning alert"
        assert len(error_alerts) == 1, "Should have one error alert"

        logger.info("Alert filtering test passed")
        return True
    except Exception as e:
        logger.error(f"Error testing alert filtering: {e}")
        return False
    finally:
        monitor.stop()


def main():
    """Run all tests."""
    logger.info("Starting system monitoring tests...")

    # Test metric collection
    if test_metric_collection():
        logger.info("Metric collection test passed")
    else:
        logger.error("Metric collection test failed")

    # Test custom metrics
    if test_custom_metrics():
        logger.info("Custom metrics test passed")
    else:
        logger.error("Custom metrics test failed")

    # Test alert filtering
    if test_alert_filtering():
        logger.info("Alert filtering test passed")
    else:
        logger.error("Alert filtering test failed")

    logger.info("All tests completed")


if __name__ == "__main__":
    main()
