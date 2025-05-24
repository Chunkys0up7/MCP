interface LLMConfig {
  model: string;
  temperature: number;
  maxTokens: number;
  input: any;
}

export class LLMService {
  async execute(config: LLMConfig): Promise<any> {
    try {
      const response = await fetch('/api/llm/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: config.model,
          temperature: config.temperature,
          max_tokens: config.maxTokens,
          input: config.input,
        }),
      });

      if (!response.ok) {
        throw new Error(`LLM execution failed: ${response.statusText}`);
      }

      const result = await response.json();
      return result.output;
    } catch (error) {
      console.error('LLM execution error:', error);
      throw error;
    }
  }
} 