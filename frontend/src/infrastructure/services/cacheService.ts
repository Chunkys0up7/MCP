import { performanceMonitoringService } from './performanceMonitoringService';

interface CacheEntry<T> {
  value: T;
  timestamp: number;
  expiresAt: number;
  metadata?: Record<string, any>;
}

interface CacheOptions {
  ttl?: number; // Time to live in milliseconds
  maxSize?: number; // Maximum number of entries
  metadata?: Record<string, any>;
}

class CacheService {
  private cache: Map<string, CacheEntry<any>> = new Map();
  private defaultTTL = 5 * 60 * 1000; // 5 minutes
  private maxSize = 1000; // Maximum number of entries

  constructor(options?: { defaultTTL?: number; maxSize?: number }) {
    if (options?.defaultTTL) this.defaultTTL = options.defaultTTL;
    if (options?.maxSize) this.maxSize = options.maxSize;
  }

  async get<T>(key: string): Promise<T | null> {
    const entry = this.cache.get(key);
    
    if (!entry) {
      performanceMonitoringService.trackCacheOperation(key, false);
      return null;
    }

    if (Date.now() > entry.expiresAt) {
      this.cache.delete(key);
      performanceMonitoringService.trackCacheOperation(key, false);
      return null;
    }

    performanceMonitoringService.trackCacheOperation(key, true);
    return entry.value as T;
  }

  async set<T>(key: string, value: T, options?: CacheOptions): Promise<void> {
    const now = Date.now();
    const ttl = options?.ttl ?? this.defaultTTL;

    // Check if we need to evict entries
    if (this.cache.size >= this.maxSize) {
      this.evictOldest();
    }

    this.cache.set(key, {
      value,
      timestamp: now,
      expiresAt: now + ttl,
      metadata: options?.metadata
    });
  }

  async delete(key: string): Promise<void> {
    this.cache.delete(key);
  }

  async clear(): Promise<void> {
    this.cache.clear();
  }

  async has(key: string): Promise<boolean> {
    const entry = this.cache.get(key);
    if (!entry) return false;
    return Date.now() <= entry.expiresAt;
  }

  async getMetadata(key: string): Promise<Record<string, any> | undefined> {
    const entry = this.cache.get(key);
    return entry?.metadata;
  }

  async updateMetadata(key: string, metadata: Record<string, any>): Promise<void> {
    const entry = this.cache.get(key);
    if (entry) {
      this.cache.set(key, {
        ...entry,
        metadata: { ...entry.metadata, ...metadata }
      });
    }
  }

  private evictOldest(): void {
    let oldestKey: string | null = null;
    let oldestTimestamp = Infinity;

    for (const [key, entry] of this.cache.entries()) {
      if (entry.timestamp < oldestTimestamp) {
        oldestTimestamp = entry.timestamp;
        oldestKey = key;
      }
    }

    if (oldestKey) {
      this.cache.delete(oldestKey);
    }
  }

  // Cache statistics
  getStats(): {
    size: number;
    hitRate: number;
    missRate: number;
    oldestEntry: number;
    newestEntry: number;
  } {
    const now = Date.now();
    let oldestTimestamp = Infinity;
    let newestTimestamp = 0;

    for (const entry of this.cache.values()) {
      oldestTimestamp = Math.min(oldestTimestamp, entry.timestamp);
      newestTimestamp = Math.max(newestTimestamp, entry.timestamp);
    }

    return {
      size: this.cache.size,
      hitRate: performanceMonitoringService.getCacheEfficiency('cache'),
      missRate: 100 - performanceMonitoringService.getCacheEfficiency('cache'),
      oldestEntry: oldestTimestamp === Infinity ? 0 : now - oldestTimestamp,
      newestEntry: now - newestTimestamp
    };
  }
}

export const cacheService = new CacheService(); 