from datetime import datetime
from typing import Any, Dict, List

from mcp.core.types import AIAssistantConfig
from mcp.utils.logging import log_error, log_execution


class AIAssistant:
    """AI Assistant client for handling conversations and tool execution."""

    def __init__(self, config: AIAssistantConfig):
        """Initialize AI Assistant.

        Args:
            config: AI Assistant configuration
        """
        self.config = config
        self.memory: List[Dict[str, Any]] = []
        self.tools = self._validate_tools(config.tools)

    def _validate_tools(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and format tools configuration.

        Args:
            tools: List of tool configurations

        Returns:
            List of validated tool configurations
        """
        validated_tools = []
        for tool in tools:
            if not isinstance(tool, dict):
                raise ValueError("Tool must be a dictionary")

            required_fields = ["name", "description", "parameters"]
            for field in required_fields:
                if field not in tool:
                    raise ValueError(f"Tool must have {field}")

            validated_tools.append(
                {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"],
                }
            )

        return validated_tools

    def add_to_memory(self, message: Dict[str, Any]):
        """Add message to conversation memory.

        Args:
            message: Message to add to memory
        """
        self.memory.append({"timestamp": datetime.now().isoformat(), "message": message})

        # Trim memory if it exceeds size limit
        if len(self.memory) > self.config.memory_size:
            self.memory = self.memory[-self.config.memory_size :]

    def get_memory(self) -> List[Dict[str, Any]]:
        """Get conversation memory.

        Returns:
            List of messages in memory
        """
        return self.memory

    def clear_memory(self):
        """Clear conversation memory."""
        self.memory = []

    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool.

        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters

        Returns:
            Tool execution result
        """
        try:
            # Find tool configuration
            tool_config = next((tool for tool in self.tools if tool["name"] == tool_name), None)

            if not tool_config:
                raise ValueError(f"Tool {tool_name} not found")

            # Validate parameters
            self._validate_parameters(tool_config["parameters"], parameters)

            # Execute tool (placeholder for actual implementation)
            result = {
                "status": "success",
                "result": f"Executed {tool_name} with parameters: {parameters}",
            }

            # Log execution
            log_execution(
                {"type": "tool_execution", "tool": tool_name, "parameters": parameters}, result
            )

            return result

        except Exception as e:
            # Log error
            log_error(e, {"type": "tool_execution", "tool": tool_name, "parameters": parameters})
            raise

    def _validate_parameters(self, schema: Dict[str, Any], parameters: Dict[str, Any]):
        """Validate tool parameters against schema.

        Args:
            schema: Parameter schema
            parameters: Parameters to validate

        Raises:
            ValueError: If parameters are invalid
        """
        # Check required parameters
        for param_name, param_schema in schema.items():
            if param_schema.get("required", False) and param_name not in parameters:
                raise ValueError(f"Required parameter {param_name} not provided")

        # Check parameter types
        for param_name, param_value in parameters.items():
            if param_name not in schema:
                raise ValueError(f"Unknown parameter {param_name}")

            param_type = schema[param_name].get("type")
            if param_type and not isinstance(param_value, eval(param_type)):
                raise ValueError(f"Parameter {param_name} must be of type {param_type}")

    async def process_message(self, message: str) -> Dict[str, Any]:
        """Process a user message.

        Args:
            message: User message

        Returns:
            Assistant response
        """
        try:
            # Add message to memory
            self.add_to_memory({"role": "user", "content": message})

            # Process message (placeholder for actual implementation)
            response = {"role": "assistant", "content": f"Processed message: {message}"}

            # Add response to memory
            self.add_to_memory(response)

            # Log execution
            log_execution({"type": "message_processing", "message": message}, response)

            return response

        except Exception as e:
            # Log error
            log_error(e, {"type": "message_processing", "message": message})
            raise

    def get_tools(self) -> List[Dict[str, Any]]:
        """Get available tools.

        Returns:
            List of tool configurations
        """
        return self.tools

    def add_tool(self, tool: Dict[str, Any]):
        """Add a new tool.

        Args:
            tool: Tool configuration
        """
        validated_tool = self._validate_tools([tool])[0]
        self.tools.append(validated_tool)

    def remove_tool(self, tool_name: str):
        """Remove a tool.

        Args:
            tool_name: Name of the tool to remove
        """
        self.tools = [tool for tool in self.tools if tool["name"] != tool_name]
