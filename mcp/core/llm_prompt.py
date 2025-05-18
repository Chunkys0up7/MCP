from typing import Any, Dict, Optional
import os
from dotenv import load_dotenv
import requests
from pydantic import BaseModel

from .base import BaseMCP, MCPConfig

# Load environment variables
load_dotenv()

class LLMPromptConfig(MCPConfig):
    """Configuration for LLM Prompt MCP"""
    template: str
    input_variables: list[str]
    model_name: str = "claude-3-sonnet-20240229"  # Default model name
    temperature: float = 0.7
    max_tokens: Optional[int] = None

    def __init__(self, **data):
        super().__init__(**data)
        # Ensure model_name is preserved from input data
        if "model_name" in data:
            self.model_name = data["model_name"]

class ClaudeLLM:
    """Custom LLM implementation for Claude API"""
    def __init__(self, model_name: str, temperature: float = 0.7, max_tokens: Optional[int] = None):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable not set. "
                "Please set your API key in one of these ways:\n"
                "1. Create a .env file in the project root with: ANTHROPIC_API_KEY=your_api_key_here\n"
                "2. Set it as an environment variable: set ANTHROPIC_API_KEY=your_api_key_here (Windows) or export ANTHROPIC_API_KEY=your_api_key_here (Linux/Mac)"
            )
        # Test API connectivity at initialization
        self.test_connection()

    def test_connection(self):
        """Test API connectivity by sending a simple message"""
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        data = {
            "model": self.model_name,
            "max_tokens": 100,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello, this is a connection test."
                }
            ]
        }
        
        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data
            )
            
            if response.status_code == 401:
                raise ValueError(
                    "Invalid Claude API key. Please check your API key and make sure it's correct."
                )
            elif response.status_code == 400:
                error_detail = response.json().get('error', {}).get('message', 'Unknown error')
                raise ValueError(f"Invalid request: {error_detail}")
            
            response.raise_for_status()
            print(f"Successfully connected to Claude API using model: {self.model_name}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error testing API connection: {str(e)}")
            raise Exception(f"Failed to connect to Claude API: {str(e)}")

    def call(self, prompt: str) -> str:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        data = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        # Only add optional parameters if they are set
        if self.temperature is not None:
            data["temperature"] = self.temperature
        if self.max_tokens is not None:
            data["max_tokens"] = self.max_tokens

        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data
            )
            
            # Handle different error cases
            if response.status_code == 401:
                raise ValueError(
                    "Invalid Claude API key. Please check your API key and make sure it's correct.\n"
                    "You can set it in one of these ways:\n"
                    "1. Create a .env file in the project root with: ANTHROPIC_API_KEY=your_api_key_here\n"
                    "2. Set it as an environment variable: set ANTHROPIC_API_KEY=your_api_key_here (Windows) or export ANTHROPIC_API_KEY=your_api_key_here (Linux/Mac)"
                )
            elif response.status_code == 400:
                error_detail = response.json().get('error', {}).get('message', 'Unknown error')
                raise ValueError(f"Invalid request: {error_detail}")
            
            response.raise_for_status()
            return response.json()["content"][0]["text"]
        except requests.exceptions.RequestException as e:
            raise Exception(f"Claude API error: {str(e)}")

class LLMPromptMCP(BaseMCP):
    """MCP for executing LLM prompts"""
    def __init__(self, config: LLMPromptConfig):
        super().__init__(config)
        self._name = config.name
        self._description = config.description
        self.llm = self._get_llm()
        self.template = config.template

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> Optional[str]:
        return self._description

    def _get_llm(self):
        # Get the model name from config
        model_name = self.config.model_name
        print(f"Using model: {model_name}")
        
        # Only allow valid Claude models
        supported_models = [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240229"
        ]
        
        if model_name in supported_models:
            return ClaudeLLM(
                model_name=model_name,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
        else:
            print(f"Unsupported model: {model_name}")
            raise ValueError(
                f"Unsupported model: {model_name}. "
                f"Supported models are: {', '.join(supported_models)}"
            )

    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the prompt"""
        try:
            response = self.llm.call(self.template)
            return {
                "result": response,
                "model": self.config.model_name,
                "prompt": self.template
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            } 