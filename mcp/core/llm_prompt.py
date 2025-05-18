from typing import Any, Dict, Optional
import os
from dotenv import load_dotenv
import requests
from pydantic import BaseModel

from .base import BaseMCP, MCPConfig

# Load environment variables
load_dotenv()

class LLMPromptConfig(BaseModel):
    """Configuration for LLM Prompt MCP"""
    name: str
    description: Optional[str] = None
    template: str
    input_variables: list[str]
    model_name: str = "pplx-7b-chat"
    temperature: float = 0.7
    max_tokens: Optional[int] = None

class PerplexityLLM:
    """Custom LLM implementation for Perplexity API"""
    def __init__(self, model_name: str, temperature: float = 0.7, max_tokens: Optional[int] = None):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError(
                "PERPLEXITY_API_KEY environment variable not set. "
                "Please set your API key in one of these ways:\n"
                "1. Create a .env file in the project root with: PERPLEXITY_API_KEY=your_api_key_here\n"
                "2. Set it as an environment variable: set PERPLEXITY_API_KEY=your_api_key_here (Windows) or export PERPLEXITY_API_KEY=your_api_key_here (Linux/Mac)"
            )

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
        try:
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=data
            )
            if response.status_code == 401:
                raise ValueError(
                    "Invalid Perplexity API key. Please check your API key and make sure it's correct.\n"
                    "You can set it in one of these ways:\n"
                    "1. Create a .env file in the project root with: PERPLEXITY_API_KEY=your_api_key_here\n"
                    "2. Set it as an environment variable: set PERPLEXITY_API_KEY=your_api_key_here (Windows) or export PERPLEXITY_API_KEY=your_api_key_here (Linux/Mac)"
                )
            response.raise_for_status()  # Raise an exception for other bad status codes
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            raise Exception(f"Perplexity API error: {str(e)}")

class LLMPromptMCP(BaseMCP):
    """MCP for executing LLM prompts"""
    def __init__(self, config: LLMPromptConfig):
        super().__init__(config)
        self._name = config.name
        self._description = config.description
        self.llm = self._get_llm()
        self.template = config.template
        self.input_variables = config.input_variables

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> Optional[str]:
        return self._description

    def _get_llm(self):
        if self.config.model_name.startswith("pplx-"):
            return PerplexityLLM(
                model_name=self.config.model_name,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
        else:
            raise ValueError(f"Unsupported model: {self.config.model_name}")

    def format(self, **kwargs) -> str:
        """Format the prompt with given variables"""
        prompt = self.template
        for key, value in kwargs.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))
        return prompt

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