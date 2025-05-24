interface NotebookConfig {
  path: string;
  kernel: string;
  timeout: number;
  input?: any;
}

export class NotebookService {
  async execute(config: NotebookConfig): Promise<any> {
    try {
      const response = await fetch('/api/notebook/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          path: config.path,
          kernel: config.kernel,
          timeout: config.timeout,
          input: config.input,
        }),
      });

      if (!response.ok) {
        throw new Error(`Notebook execution failed: ${response.statusText}`);
      }

      const result = await response.json();
      return result.output;
    } catch (error) {
      console.error('Notebook execution error:', error);
      throw error;
    }
  }
} 