interface RateLimitConfig {
  maxRequests: number;
  timeWindow: number; // in milliseconds
}

interface RateLimitState {
  requests: number[];
  lastReset: number;
}

class RateLimiter {
  private state: Map<string, RateLimitState>;
  private config: RateLimitConfig;

  constructor(config: RateLimitConfig) {
    this.state = new Map();
    this.config = config;
  }

  private getState(key: string): RateLimitState {
    const now = Date.now();
    const currentState = this.state.get(key);

    if (!currentState || now - currentState.lastReset >= this.config.timeWindow) {
      return {
        requests: [],
        lastReset: now,
      };
    }

    return currentState;
  }

  private cleanup(key: string, now: number): void {
    const state = this.state.get(key);
    if (state) {
      state.requests = state.requests.filter(
        (timestamp) => now - timestamp < this.config.timeWindow
      );
      this.state.set(key, state);
    }
  }

  public async checkLimit(key: string): Promise<boolean> {
    const now = Date.now();
    const state = this.getState(key);
    this.cleanup(key, now);

    if (state.requests.length >= this.config.maxRequests) {
      return false;
    }

    state.requests.push(now);
    this.state.set(key, state);
    return true;
  }

  public getRemainingRequests(key: string): number {
    const now = Date.now();
    const state = this.getState(key);
    this.cleanup(key, now);

    return Math.max(0, this.config.maxRequests - state.requests.length);
  }

  public getTimeUntilReset(key: string): number {
    const now = Date.now();
    const state = this.getState(key);
    return Math.max(0, this.config.timeWindow - (now - state.lastReset));
  }
}

// Create a singleton instance with default configuration
export const rateLimiter = new RateLimiter({
  maxRequests: 100, // 100 requests
  timeWindow: 60000, // per minute
});

// Create a higher-order function to wrap API calls with rate limiting
export const withRateLimit = <T>(
  key: string,
  fn: () => Promise<T>,
  onLimitExceeded?: () => void
): Promise<T> => {
  return new Promise((resolve, reject) => {
    rateLimiter.checkLimit(key).then((allowed) => {
      if (allowed) {
        fn().then(resolve).catch(reject);
      } else {
        if (onLimitExceeded) {
          onLimitExceeded();
        }
        reject(
          new Error(
            `Rate limit exceeded. Try again in ${Math.ceil(
              rateLimiter.getTimeUntilReset(key) / 1000
            )} seconds.`
          )
        );
      }
    });
  });
}; 