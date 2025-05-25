"""
Database Monitoring

This module provides comprehensive database monitoring functionality.
It includes:

1. Performance metrics collection
2. Health checks and alerts
3. Resource usage monitoring
4. Query performance analysis
5. Automated reporting
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from sqlalchemy import text
from sqlalchemy.orm import Session
import psutil
import time
from dataclasses import dataclass
from threading import Thread, Event
import json

logger = logging.getLogger(__name__)

@dataclass
class DatabaseMetrics:
    """Container for database metrics."""
    timestamp: datetime
    active_connections: int
    idle_connections: int
    waiting_connections: int
    total_transactions: int
    active_transactions: int
    cache_hit_ratio: float
    table_sizes: Dict[str, int]
    index_sizes: Dict[str, int]
    slow_queries: List[Dict[str, Any]]
    system_metrics: Dict[str, float]

class DatabaseMonitor:
    """
    Database monitoring system.
    
    This class provides:
    1. Real-time metrics collection
    2. Performance analysis
    3. Health monitoring
    4. Alert generation
    """
    
    def __init__(
        self,
        session: Session,
        collection_interval: int = 60,
        alert_thresholds: Optional[Dict[str, float]] = None
    ):
        """
        Initialize the database monitor.
        
        Args:
            session: Database session
            collection_interval: Metrics collection interval in seconds
            alert_thresholds: Custom alert thresholds
        """
        self.session = session
        self.collection_interval = collection_interval
        self.alert_thresholds = alert_thresholds or {
            'cache_hit_ratio': 0.95,
            'connection_utilization': 0.8,
            'disk_usage': 0.9,
            'memory_usage': 0.9,
            'cpu_usage': 0.8
        }
        self._stop_event = Event()
        self._metrics_history: List[DatabaseMetrics] = []
        self._monitor_thread: Optional[Thread] = None
    
    def start_monitoring(self) -> None:
        """Start the monitoring thread."""
        if self._monitor_thread is not None:
            logger.warning("Monitoring is already running")
            return
        
        self._stop_event.clear()
        self._monitor_thread = Thread(target=self._monitor_loop)
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
        logger.info("Started database monitoring")
    
    def stop_monitoring(self) -> None:
        """Stop the monitoring thread."""
        if self._monitor_thread is None:
            return
        
        self._stop_event.set()
        self._monitor_thread.join()
        self._monitor_thread = None
        logger.info("Stopped database monitoring")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while not self._stop_event.is_set():
            try:
                metrics = self.collect_metrics()
                self._metrics_history.append(metrics)
                
                # Keep only last 24 hours of metrics
                cutoff = datetime.now() - timedelta(hours=24)
                self._metrics_history = [
                    m for m in self._metrics_history
                    if m.timestamp > cutoff
                ]
                
                # Check for alerts
                self._check_alerts(metrics)
                
                time.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(5)  # Wait before retrying
    
    def collect_metrics(self) -> DatabaseMetrics:
        """
        Collect current database metrics.
        
        Returns:
            DatabaseMetrics: Current database metrics
        """
        try:
            # Get connection stats
            conn_stats = self._get_connection_stats()
            
            # Get transaction stats
            tx_stats = self._get_transaction_stats()
            
            # Get cache stats
            cache_stats = self._get_cache_stats()
            
            # Get table and index sizes
            size_stats = self._get_size_stats()
            
            # Get slow queries
            slow_queries = self._get_slow_queries()
            
            # Get system metrics
            system_metrics = self._get_system_metrics()
            
            return DatabaseMetrics(
                timestamp=datetime.now(),
                active_connections=conn_stats['active'],
                idle_connections=conn_stats['idle'],
                waiting_connections=conn_stats['waiting'],
                total_transactions=tx_stats['total'],
                active_transactions=tx_stats['active'],
                cache_hit_ratio=cache_stats['hit_ratio'],
                table_sizes=size_stats['tables'],
                index_sizes=size_stats['indexes'],
                slow_queries=slow_queries,
                system_metrics=system_metrics
            )
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {str(e)}")
            raise
    
    def _get_connection_stats(self) -> Dict[str, int]:
        """Get database connection statistics."""
        result = self.session.execute(text("""
            SELECT
                count(*) FILTER (WHERE state = 'active') as active,
                count(*) FILTER (WHERE state = 'idle') as idle,
                count(*) FILTER (WHERE state = 'waiting') as waiting
            FROM pg_stat_activity
            WHERE datname = current_database()
        """))
        row = result.fetchone()
        return {
            'active': row[0],
            'idle': row[1],
            'waiting': row[2]
        }
    
    def _get_transaction_stats(self) -> Dict[str, int]:
        """Get transaction statistics."""
        result = self.session.execute(text("""
            SELECT
                count(*) as total,
                count(*) FILTER (WHERE state = 'active') as active
            FROM pg_stat_activity
            WHERE datname = current_database()
        """))
        row = result.fetchone()
        return {
            'total': row[0],
            'active': row[1]
        }
    
    def _get_cache_stats(self) -> Dict[str, float]:
        """Get cache statistics."""
        result = self.session.execute(text("""
            SELECT
                sum(heap_blks_hit) as hits,
                sum(heap_blks_read) as reads
            FROM pg_statio_user_tables
        """))
        row = result.fetchone()
        total = row[0] + row[1]
        hit_ratio = row[0] / total if total > 0 else 0
        return {'hit_ratio': hit_ratio}
    
    def _get_size_stats(self) -> Dict[str, Dict[str, int]]:
        """Get table and index size statistics."""
        # Get table sizes
        table_result = self.session.execute(text("""
            SELECT
                relname as table_name,
                pg_total_relation_size(relid) as size
            FROM pg_catalog.pg_statio_user_tables
            ORDER BY size DESC
        """))
        table_sizes = {row[0]: row[1] for row in table_result}
        
        # Get index sizes
        index_result = self.session.execute(text("""
            SELECT
                relname as index_name,
                pg_total_relation_size(relid) as size
            FROM pg_catalog.pg_statio_user_indexes
            ORDER BY size DESC
        """))
        index_sizes = {row[0]: row[1] for row in index_result}
        
        return {
            'tables': table_sizes,
            'indexes': index_sizes
        }
    
    def _get_slow_queries(self) -> List[Dict[str, Any]]:
        """Get slow query statistics."""
        result = self.session.execute(text("""
            SELECT
                query,
                calls,
                total_time,
                mean_time,
                rows
            FROM pg_stat_statements
            WHERE datname = current_database()
            ORDER BY mean_time DESC
            LIMIT 10
        """))
        return [
            {
                'query': row[0],
                'calls': row[1],
                'total_time': row[2],
                'mean_time': row[3],
                'rows': row[4]
            }
            for row in result
        ]
    
    def _get_system_metrics(self) -> Dict[str, float]:
        """Get system resource metrics."""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent
        }
    
    def _check_alerts(self, metrics: DatabaseMetrics) -> None:
        """
        Check metrics against thresholds and generate alerts.
        
        Args:
            metrics: Current database metrics
        """
        # Check cache hit ratio
        if metrics.cache_hit_ratio < self.alert_thresholds['cache_hit_ratio']:
            self._generate_alert(
                'cache_hit_ratio',
                f"Low cache hit ratio: {metrics.cache_hit_ratio:.2%}"
            )
        
        # Check connection utilization
        total_connections = (
            metrics.active_connections +
            metrics.idle_connections +
            metrics.waiting_connections
        )
        if total_connections > 0:
            utilization = metrics.active_connections / total_connections
            if utilization > self.alert_thresholds['connection_utilization']:
                self._generate_alert(
                    'connection_utilization',
                    f"High connection utilization: {utilization:.2%}"
                )
        
        # Check system metrics
        if metrics.system_metrics['disk_percent'] > self.alert_thresholds['disk_usage']:
            self._generate_alert(
                'disk_usage',
                f"High disk usage: {metrics.system_metrics['disk_percent']:.2%}"
            )
        
        if metrics.system_metrics['memory_percent'] > self.alert_thresholds['memory_usage']:
            self._generate_alert(
                'memory_usage',
                f"High memory usage: {metrics.system_metrics['memory_percent']:.2%}"
            )
        
        if metrics.system_metrics['cpu_percent'] > self.alert_thresholds['cpu_usage']:
            self._generate_alert(
                'cpu_usage',
                f"High CPU usage: {metrics.system_metrics['cpu_percent']:.2%}"
            )
    
    def _generate_alert(self, alert_type: str, message: str) -> None:
        """
        Generate an alert.
        
        Args:
            alert_type: Type of alert
            message: Alert message
        """
        logger.warning(f"Database Alert [{alert_type}]: {message}")
        # TODO: Implement alert notification (email, Slack, etc.)
    
    def get_metrics_history(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[DatabaseMetrics]:
        """
        Get historical metrics.
        
        Args:
            start_time: Start time for metrics range
            end_time: End time for metrics range
        
        Returns:
            List[DatabaseMetrics]: Historical metrics
        """
        if not start_time:
            start_time = datetime.now() - timedelta(hours=1)
        if not end_time:
            end_time = datetime.now()
        
        return [
            m for m in self._metrics_history
            if start_time <= m.timestamp <= end_time
        ]
    
    def generate_report(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Generate a monitoring report.
        
        Args:
            start_time: Start time for report range
            end_time: End time for report range
        
        Returns:
            Dict[str, Any]: Monitoring report
        """
        metrics = self.get_metrics_history(start_time, end_time)
        if not metrics:
            return {}
        
        # Calculate averages
        avg_connections = sum(
            m.active_connections + m.idle_connections + m.waiting_connections
            for m in metrics
        ) / len(metrics)
        
        avg_cache_hit = sum(m.cache_hit_ratio for m in metrics) / len(metrics)
        
        avg_cpu = sum(m.system_metrics['cpu_percent'] for m in metrics) / len(metrics)
        avg_memory = sum(m.system_metrics['memory_percent'] for m in metrics) / len(metrics)
        avg_disk = sum(m.system_metrics['disk_percent'] for m in metrics) / len(metrics)
        
        # Get slowest queries
        all_slow_queries = []
        for m in metrics:
            all_slow_queries.extend(m.slow_queries)
        slowest_queries = sorted(
            all_slow_queries,
            key=lambda q: q['mean_time'],
            reverse=True
        )[:5]
        
        return {
            'period': {
                'start': metrics[0].timestamp.isoformat(),
                'end': metrics[-1].timestamp.isoformat()
            },
            'averages': {
                'connections': avg_connections,
                'cache_hit_ratio': avg_cache_hit,
                'cpu_usage': avg_cpu,
                'memory_usage': avg_memory,
                'disk_usage': avg_disk
            },
            'slowest_queries': slowest_queries,
            'alerts': self._get_alerts(metrics)
        }
    
    def _get_alerts(self, metrics: List[DatabaseMetrics]) -> List[Dict[str, Any]]:
        """
        Get alerts from metrics.
        
        Args:
            metrics: List of metrics to analyze
        
        Returns:
            List[Dict[str, Any]]: List of alerts
        """
        alerts = []
        for metric in metrics:
            # Check each metric against thresholds
            if metric.cache_hit_ratio < self.alert_thresholds['cache_hit_ratio']:
                alerts.append({
                    'timestamp': metric.timestamp.isoformat(),
                    'type': 'cache_hit_ratio',
                    'message': f"Low cache hit ratio: {metric.cache_hit_ratio:.2%}"
                })
            
            # Add more alert checks as needed
        
        return alerts 