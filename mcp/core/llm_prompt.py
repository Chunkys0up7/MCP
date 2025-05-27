import json
import os
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

from mcp.core.types import LLMPromptConfig

from .base import BaseMCPServer

# Load environment variables
load_dotenv()


class ClaudeLLM:
    """Custom LLM implementation for Claude API.

    This class handles all communication with the Claude API, including
    connection testing, prompt sending, and response handling.

    Attributes:
        model_name (str): The Claude model to use.
        temperature (float): Controls response randomness.
        max_tokens (Optional[int]): Maximum response length.
        system_prompt (Optional[str]): Optional system message for Claude API.
        api_key (str): The Claude API key from environment variables.
    """

    def __init__(
        self,
        model_name: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
    ):
        """Initialize the Claude LLM client.

        Args:
            model_name (str): The Claude model to use.
            temperature (float, optional): Controls response randomness. Defaults to 0.7.
            max_tokens (Optional[int], optional): Maximum response length. Defaults to None.
            system_prompt (Optional[str], optional): Optional system message for Claude API.

        Raises:
            ValueError: If ANTHROPIC_API_KEY is not set in environment variables.
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt
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
            "content-type": "application/json",
        }
        data = {
            "model": self.model_name,
            "max_tokens": 10,
            "messages": [{"role": "user", "content": "Connection test"}],
        }

        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages", headers=headers, json=data
            )

            if response.status_code == 401:
                raise ValueError("Invalid Claude API key.")
            elif response.status_code == 400:
                error_detail = (
                    response.json().get("error", {}).get("message", "Unknown error")
                )
                raise ValueError(f"Invalid request: {error_detail}")

            response.raise_for_status()
            print(
                f"Successfully connected to Claude API using model: {self.model_name}"
            )
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error testing API connection: {str(e)}")
            raise Exception(f"Failed to connect to Claude API: {str(e)}")

    def call(self, messages: List[Dict[str, str]]) -> str:
        """Send a prompt or messages to the Claude API and get the response.

        Args:
            messages (List[Dict[str, str]]): A list of messages for conversation history.

        Returns:
            str: The text response from Claude.

        Raises:
            ValueError: If API key is invalid or request is malformed.
            Exception: If API call fails for other reasons.
        """
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        request_data: Dict[str, Any] = {"model": self.model_name, "messages": messages}

        if self.system_prompt:
            request_data["system"] = self.system_prompt

        if self.temperature is not None:
            request_data["temperature"] = self.temperature
        if self.max_tokens is not None:
            request_data["max_tokens"] = self.max_tokens

        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=request_data,
            )

            if response.status_code == 401:
                raise ValueError("Invalid Claude API key.")
            elif response.status_code == 400:
                error_detail = (
                    response.json().get("error", {}).get("message", "Unknown error")
                )
                raise ValueError(f"Invalid request: {error_detail}")

            response.raise_for_status()

            content = response.json().get("content")
            if (
                content
                and isinstance(content, list)
                and len(content) > 0
                and "text" in content[0]
            ):
                return content[0]["text"]
            else:
                print(
                    f"[ClaudeLLM Warning] Unexpected response structure: {response.json()}"
                )
                return "Error: Could not parse LLM response."

        except requests.exceptions.RequestException as e:
            raise Exception(f"Claude API error: {str(e)}")


class LLMPromptMCP(BaseMCPServer):
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
        self.config: LLMPromptConfig = config  # Ensure type for self.config
        self.llm = self._get_llm()

    @property
    def name(self) -> str:
        """Get the name of the MCP.

        Returns:
            str: The MCP's name.
        """
        return self.config.name

    @property
    def description(self) -> Optional[str]:
        """Get the description of the MCP.

        Returns:
            Optional[str]: The MCP's description, if any.
        """
        return self.config.description

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
            "claude-3-haiku-20240229",
        ]

        if model_name in supported_models:
            return ClaudeLLM(
                model_name=model_name,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                system_prompt=self.config.system_prompt,
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
        if hasattr(self.config, "input_variables") and self.config.input_variables:
            missing_vars = [
                var for var in self.config.input_variables if var not in inputs
            ]
            if missing_vars:
                raise ValueError(f"Missing input variables: {', '.join(missing_vars)}")
        try:
            return self.config.template.format(**inputs)
        except KeyError as e:
            raise ValueError(
                f"Error formatting prompt: Missing key {str(e)} in inputs for template: '{self.config.template}'"
            )

    def _build_messages(self, formatted_prompt: str) -> List[Dict[str, str]]:
        """Build the messages array for the API call.

        Args:
            formatted_prompt (str): The formatted prompt.

        Returns:
            List[Dict[str, str]]: The messages array for the API call.
        """
        messages = [{"role": "user", "content": formatted_prompt}]
        return messages

    def _parse_output(self, response_text: str) -> Any:
        """Parse and validate the LLM output.

        Args:
            response_text (str): The raw response from the LLM.

        Returns:
            Any: The parsed and validated output.

        Raises:
            ValueError: If output validation fails or JSON parsing fails.
        """
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            return response_text  # Return as plain text if not JSON

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
            response_text = self.llm.call(messages=messages)

            # Parse and validate output
            result = self._parse_output(response_text)

            return {
                **result,
                "model": self.config.model_name,
                "prompt": formatted_prompt,
                "system_message": self.config.system_prompt,
            }
        except ValueError as ve:
            return {"success": False, "result": None, "error": str(ve)}
        except Exception as e:
            import traceback

            return {
                "success": False,
                "result": None,
                "error": f"LLM execution failed: {str(e)}\n{traceback.format_exc()}",
            }
