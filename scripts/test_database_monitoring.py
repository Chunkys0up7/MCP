"""
Database Monitoring Test Script

This script tests the database monitoring functionality by:
1. Starting the monitoring system
2. Simulating database load
3. Collecting metrics
4. Generating reports
5. Testing alert generation
"""

import sys
import os
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from mcp.db.session import init_pool, get_db_session
from mcp.db.monitoring import DatabaseMonitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def simulate_database_load(session, duration: int = 60) -> None:
    """
    Simulate database load by running various queries.
    
    Args:
        session: Database session
        duration: Duration of load test in seconds
    """
    end_time = time.time() + duration
    
    while time.time() < end_time:
        try:
            # Run some queries to generate load
            session.execute("SELECT pg_sleep(0.1)")  # Sleep for 100ms
            session.execute("SELECT count(*) FROM pg_stat_activity")
            session.execute("SELECT * FROM pg_stat_statements LIMIT 10")
            
        except Exception as e:
            logger.error(f"Error in load simulation: {str(e)}")
            time.sleep(1)

def test_monitoring() -> None:
    """Test the database monitoring system."""
    try:
        # Initialize database pool
        init_pool()
        
        # Get a database session
        with get_db_session() as session:
            # Create monitor with custom thresholds
            monitor = DatabaseMonitor(
                session=session,
                collection_interval=5,  # Collect metrics every 5 seconds
                alert_thresholds={
                    'cache_hit_ratio': 0.95,
                    'connection_utilization': 0.8,
                    'disk_usage': 0.9,
                    'memory_usage': 0.9,
                    'cpu_usage': 0.8
                }
            )
            
            # Start monitoring
            monitor.start_monitoring()
            logger.info("Started database monitoring")
            
            # Simulate database load
            logger.info("Starting load simulation...")
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [
                    executor.submit(simulate_database_load, session, 30)
                    for _ in range(5)
                ]
                # Wait for load simulation to complete
                for future in futures:
                    future.result()
            
            # Wait for some metrics to be collected
            time.sleep(10)
            
            # Get metrics history
            metrics = monitor.get_metrics_history()
            logger.info(f"\nCollected {len(metrics)} metrics")
            
            # Generate report
            report = monitor.generate_report()
            logger.info("\nMonitoring Report:")
            logger.info(f"Period: {report['period']['start']} to {report['period']['end']}")
            logger.info("\nAverages:")
            for metric, value in report['averages'].items():
                logger.info(f"  {metric}: {value:.2%}")
            
            logger.info("\nSlowest Queries:")
            for query in report['slowest_queries']:
                logger.info(f"  Query: {query['query'][:100]}...")
                logger.info(f"    Mean Time: {query['mean_time']:.2f}ms")
                logger.info(f"    Calls: {query['calls']}")
            
            logger.info("\nAlerts:")
            for alert in report['alerts']:
                logger.info(f"  [{alert['type']}] {alert['message']}")
            
            # Stop monitoring
            monitor.stop_monitoring()
            logger.info("\nStopped database monitoring")
            
    except Exception as e:
        logger.error(f"Error in monitoring test: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    test_monitoring() 