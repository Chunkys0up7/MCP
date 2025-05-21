import React, { Profiler, useEffect, useRef } from 'react';
import { captureMessage } from './sentry';

interface ProfilerData {
  id: string;
  phase: 'mount' | 'update' | 'nested-update';
  actualDuration: number;
  baseDuration: number;
  startTime: number;
  commitTime: number;
  interactions: Set<any>;
}

interface PerformanceMetrics {
  avg: number;
  max: number;
  min: number;
  count: number;
}

const performanceMetrics = new Map<string, number[]>();
const MAX_METRICS_PER_COMPONENT = 100;

export const onRenderCallback = (
  id: string,
  phase: ProfilerData['phase'],
  actualDuration: number,
  baseDuration: number,
  startTime: number,
  commitTime: number
) => {
  // Store metrics for analysis with size limit
  if (!performanceMetrics.has(id)) {
    performanceMetrics.set(id, []);
  }
  const metrics = performanceMetrics.get(id)!;
  metrics.push(actualDuration);
  
  // Keep only the last N metrics to prevent memory leaks
  if (metrics.length > MAX_METRICS_PER_COMPONENT) {
    metrics.shift();
  }

  // Alert if performance is poor
  if (actualDuration > 100) {
    captureMessage(`Performance warning: ${id} took ${actualDuration}ms to render`, 'warning');
  }

  // Log detailed metrics in development
  if (process.env.NODE_ENV === 'development') {
    console.log({
      id,
      phase,
      actualDuration,
      baseDuration,
      startTime,
      commitTime,
    });
  }
};

export const getPerformanceMetrics = (): Record<string, PerformanceMetrics> => {
  const metrics: Record<string, PerformanceMetrics> = {};
  
  performanceMetrics.forEach((durations, id) => {
    if (durations.length > 0) {
      metrics[id] = {
        avg: durations.reduce((a, b) => a + b, 0) / durations.length,
        max: Math.max(...durations),
        min: Math.min(...durations),
        count: durations.length
      };
    }
  });

  return metrics;
};

export const clearPerformanceMetrics = (id?: string) => {
  if (id) {
    performanceMetrics.delete(id);
  } else {
    performanceMetrics.clear();
  }
};

interface PerformanceMonitorProps {
  id: string;
  children: React.ReactNode;
  onMetricsUpdate?: (metrics: PerformanceMetrics) => void;
}

export const PerformanceMonitor: React.FC<PerformanceMonitorProps> = ({ 
  id, 
  children,
  onMetricsUpdate 
}) => {
  const metricsRef = useRef<PerformanceMetrics | null>(null);

  useEffect(() => {
    return () => {
      // Clean up metrics when component unmounts
      clearPerformanceMetrics(id);
    };
  }, [id]);

  useEffect(() => {
    if (onMetricsUpdate && performanceMetrics.has(id)) {
      const metrics = getPerformanceMetrics()[id];
      if (metrics && JSON.stringify(metrics) !== JSON.stringify(metricsRef.current)) {
        metricsRef.current = metrics;
        onMetricsUpdate(metrics);
      }
    }
  }, [id, onMetricsUpdate]);

  return (
    <Profiler id={id} onRender={onRenderCallback}>
      {children}
    </Profiler>
  );
}; 