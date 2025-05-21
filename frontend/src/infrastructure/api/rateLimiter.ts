interface RateLimitConfig {
  maxRequests: number;
  timeWindow: number; // in milliseconds
  burstSize?: number; // Optional burst size for handling sudden spikes
}

interface RateLimitState {
  requests: number[];
  lastReset: number;
  burstCount: number;
}

export class RateLimitError extends Error {
  constructor(
    message: string,
    public readonly timeUntilReset: number,
    public readonly remainingRequests: number
  ) {
    super(message);
    this.name = 'RateLimitError';
  }
}

class RateLimiter {
  private state: Map<string, RateLimitState>;
  private config: Required<RateLimitConfig>;

  constructor(config: RateLimitConfig) {
    this.state = new Map();
    this.config = {
      maxRequests: config.maxRequests,
      timeWindow: config.timeWindow,
      burstSize: config.burstSize || Math.floor(config.maxRequests * 0.2), // Default burst size is 20% of max requests
    };
  }

  private getState(key: string): RateLimitState {
    const now = Date.now();
    const currentState = this.state.get(key);

    if (!currentState || now - currentState.lastReset >= this.config.timeWindow) {
      return {
        requests: [],
        lastReset: now,
        burstCount: 0,
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

    // Check if we're in burst mode
    if (state.burstCount < this.config.burstSize) {
      state.burstCount++;
      state.requests.push(now);
      this.state.set(key, state);
      return true;
    }

    // Normal rate limiting
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

  public getBurstRemaining(key: string): number {
    const state = this.state.get(key);
    if (!state) {
      return this.config.burstSize;
    }
    return Math.max(0, this.config.burstSize - state.burstCount);
  }
}

// Create a singleton instance with default configuration
export const rateLimiter = new RateLimiter({
  maxRequests: 100, // 100 requests
  timeWindow: 60000, // per minute
  burstSize: 20, // Allow 20 requests in burst mode
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
        const timeUntilReset = rateLimiter.getTimeUntilReset(key);
        const remainingRequests = rateLimiter.getRemainingRequests(key);
        reject(
          new RateLimitError(
            `Rate limit exceeded. Try again in ${Math.ceil(timeUntilReset / 1000)} seconds.`,
            timeUntilReset,
            remainingRequests
          )
        );
      }
    });
  });
}; 