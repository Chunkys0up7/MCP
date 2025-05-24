interface DataConfig {
  type: string;
  source: string;
  format: string;
}

export class DataService {
  async execute(config: DataConfig): Promise<any> {
    try {
      const response = await fetch('/api/data/load', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          type: config.type,
          source: config.source,
          format: config.format,
        }),
      });

      if (!response.ok) {
        throw new Error(`Data loading failed: ${response.statusText}`);
      }

      const result = await response.json();
      return result.data;
    } catch (error) {
      console.error('Data loading error:', error);
      throw error;
    }
  }
} 