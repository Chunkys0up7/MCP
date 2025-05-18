from typing import Any, Dict, Optional
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
import requests
from pydantic import BaseModel

from .base import BaseMCP, MCPConfig

# Load environment variables
load_dotenv()

class LLMPromptConfig(BaseModel):
    """Configuration for LLM Prompt MCP"""
    template: str
    input_variables: list[str]
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: Optional[int] = None

class PerplexityLLM:
    """Custom LLM implementation for Perplexity API (plain Python class)"""
    def __init__(self, model_name: str, temperature: float = 0.7, max_tokens: Optional[int] = None):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY environment variable not set")

    def call(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model_name,
            "prompt": prompt,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=data
        )
        if response.status_code != 200:
            raise Exception(f"Perplexity API error: {response.text}")
        return response.json()["choices"][0]["message"]["content"]

class LLMPromptMCP(BaseMCP):
    """MCP for executing LLM prompts"""
    def __init__(self, config: LLMPromptConfig):
        super().__init__(config)
        self.llm = self._get_llm()
        self.prompt = PromptTemplate(
            template=config.template,
            input_variables=config.input_variables
        )

    def _get_llm(self):
        if self.config.model_name == "perplexity":
            return PerplexityLLM(
                model_name=self.config.model_name,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
        else:
            raise ValueError(f"Unsupported model: {self.config.model_name}")

    def format(self, **kwargs) -> str:
        """Format the prompt with given variables"""
        return self.prompt.format(**kwargs)

    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the prompt with given inputs"""
        try:
            formatted_prompt = self.format(**inputs)
            response = self.llm.call(formatted_prompt)
            return {
                "result": response,
                "model": self.config.model_name,
                "prompt": formatted_prompt
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            } 