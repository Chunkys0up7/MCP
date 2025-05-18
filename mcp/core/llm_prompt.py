from typing import Any, Dict, Optional, List, Union
import os
from dotenv import load_dotenv
import requests
from pydantic import BaseModel

from .base import BaseMCP, MCPConfig

# Load environment variables
load_dotenv()

class LLMPromptConfig(MCPConfig):
    """Configuration for LLM Prompt MCP.
    
    This class defines the configuration structure for LLM-based MCPs, including
    prompt templates, model settings, and output formatting options.
    
    Attributes:
        template (str): The prompt template with variable placeholders using {variable_name} syntax.
        input_variables (list[str]): List of required input variables that must be provided during execution.
        model_name (str): The LLM model to use. Defaults to "claude-3-sonnet-20240229".
        temperature (float): Controls randomness in responses (0.0-1.0). Defaults to 0.7.
        max_tokens (Optional[int]): Maximum number of tokens in the response. Defaults to None.
        system_message (Optional[str]): Optional system message to guide LLM behavior.
        output_format (Optional[Dict[str, Any]]): Optional schema for structured output validation.
        chain_of_thought (bool): Whether to enable step-by-step reasoning. Defaults to False.
        context (Optional[Dict[str, Any]]): Optional persistent context for the MCP.
    """
    template: str
    input_variables: list[str]
    model_name: str = "claude-3-sonnet-20240229"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    system_message: Optional[str] = None
    output_format: Optional[Dict[str, Any]] = None
    chain_of_thought: bool = False
    context: Optional[Dict[str, Any]] = None

    def __init__(self, **data):
        """Initialize the LLM Prompt configuration.
        
        Args:
            **data: Configuration data including template, input variables, and optional settings.
        """
        super().__init__(**data)
        if "model_name" in data:
            self.model_name = data["model_name"]

class ClaudeLLM:
    """Custom LLM implementation for Claude API.
    
    This class handles all communication with the Claude API, including
    connection testing, prompt sending, and response handling.
    
    Attributes:
        model_name (str): The Claude model to use.
        temperature (float): Controls response randomness.
        max_tokens (Optional[int]): Maximum response length.
        api_key (str): The Claude API key from environment variables.
    """
    
    def __init__(self, model_name: str, temperature: float = 0.7, max_tokens: Optional[int] = None):
        """Initialize the Claude LLM client.
        
        Args:
            model_name (str): The Claude model to use.
            temperature (float, optional): Controls response randomness. Defaults to 0.7.
            max_tokens (Optional[int], optional): Maximum response length. Defaults to None.
            
        Raises:
            ValueError: If ANTHROPIC_API_KEY is not set in environment variables.
        """
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

    def test_connection(self) -> bool:
        """Test the connection to the Claude API.
        
        Sends a simple test message to verify API connectivity and key validity.
        
        Returns:
            bool: True if connection is successful.
            
        Raises:
            ValueError: If API key is invalid or request is malformed.
            Exception: If connection fails for other reasons.
        """
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
        """Send a prompt to the Claude API and get the response.
        
        Args:
            prompt (str): The prompt to send to Claude.
            
        Returns:
            str: The text response from Claude.
            
        Raises:
            ValueError: If API key is invalid or request is malformed.
            Exception: If API call fails for other reasons.
        """
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
    """MCP for executing LLM prompts with advanced features.
    
    This class implements the MCP interface for LLM prompts, providing
    features like variable interpolation, system messages, chain of thought,
    and output validation.
    
    Attributes:
        _name (str): The name of the MCP.
        _description (Optional[str]): Optional description of the MCP.
        llm (ClaudeLLM): The LLM client instance.
        template (str): The prompt template.
        system_message (Optional[str]): Optional system message.
        output_format (Optional[Dict[str, Any]]): Optional output schema.
        chain_of_thought (bool): Whether to use chain of thought.
        context (Dict[str, Any]): Persistent context for the MCP.
    """
    
    def __init__(self, config: LLMPromptConfig):
        """Initialize the LLM Prompt MCP.
        
        Args:
            config (LLMPromptConfig): The configuration for this MCP.
        """
        super().__init__(config)
        self._name = config.name
        self._description = config.description
        self.llm = self._get_llm()
        self.template = config.template
        self.system_message = config.system_message
        self.output_format = config.output_format
        self.chain_of_thought = config.chain_of_thought
        self.context = config.context or {}

    @property
    def name(self) -> str:
        """Get the name of the MCP.
        
        Returns:
            str: The MCP's name.
        """
        return self._name

    @property
    def description(self) -> Optional[str]:
        """Get the description of the MCP.
        
        Returns:
            Optional[str]: The MCP's description, if any.
        """
        return self._description

    def _get_llm(self) -> ClaudeLLM:
        """Get the LLM client instance.
        
        Returns:
            ClaudeLLM: The configured LLM client.
            
        Raises:
            ValueError: If the model is not supported.
        """
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

    def _format_prompt(self, inputs: Dict[str, Any]) -> str:
        """Format the prompt template with input variables.
        
        Args:
            inputs (Dict[str, Any]): The input variables to format the template with.
            
        Returns:
            str: The formatted prompt.
            
        Raises:
            ValueError: If a required input variable is missing.
        """
        try:
            # Merge context with inputs
            all_inputs = {**self.context, **inputs}
            return self.template.format(**all_inputs)
        except KeyError as e:
            raise ValueError(f"Missing required input variable: {e}")

    def _build_messages(self, prompt: str) -> List[Dict[str, str]]:
        """Build the messages array for the API call.
        
        Args:
            prompt (str): The formatted prompt.
            
        Returns:
            List[Dict[str, str]]: The messages array for the API call.
        """
        messages = []
        
        # Add system message if provided
        if self.system_message:
            messages.append({
                "role": "system",
                "content": self.system_message
            })
        
        # Add user message
        if self.chain_of_thought:
            prompt = f"Let's solve this step by step:\n\n{prompt}"
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        return messages

    def _parse_output(self, response: str) -> Dict[str, Any]:
        """Parse and validate the LLM output.
        
        Args:
            response (str): The raw response from the LLM.
            
        Returns:
            Dict[str, Any]: The parsed and validated output.
            
        Raises:
            ValueError: If output validation fails or JSON parsing fails.
        """
        if not self.output_format:
            return {"result": response}
            
        try:
            # Try to parse as JSON if output_format is specified
            import json
            result = json.loads(response)
            
            # Validate against output_format
            for key, value_type in self.output_format.items():
                if key not in result:
                    raise ValueError(f"Missing required output field: {key}")
                if not isinstance(result[key], value_type):
                    raise ValueError(f"Invalid type for {key}: expected {value_type}, got {type(result[key])}")
            
            return result
        except json.JSONDecodeError:
            raise ValueError("Failed to parse LLM output as JSON")

    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the prompt with enhanced features.
        
        Args:
            inputs (Dict[str, Any]): The input variables for the prompt.
            
        Returns:
            Dict[str, Any]: The execution result, including:
                - The parsed output or error message
                - Model information
                - Prompt details
                - System message and context
        """
        try:
            # Format the prompt with inputs
            formatted_prompt = self._format_prompt(inputs)
            
            # Build messages array
            messages = self._build_messages(formatted_prompt)
            
            # Call the LLM
            response = self.llm.call(formatted_prompt)
            
            # Parse and validate output
            result = self._parse_output(response)
            
            return {
                **result,
                "model": self.config.model_name,
                "prompt": formatted_prompt,
                "system_message": self.system_message,
                "context": self.context
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            } 