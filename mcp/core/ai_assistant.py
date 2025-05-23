from typing import Any, Dict, List, Optional, Union

from .base import BaseMCPServer
from mcp.core.types import AIAssistantConfig
from mcp.core.llm_prompt import ClaudeLLM # Reusing ClaudeLLM for now

# Placeholder for actual tool execution logic if tools are internal
# For external tools, this MCP would describe the call, and another system would execute.

class AIAssistantMCP(BaseMCPServer):
    """
    MCP for managing an AI assistant, potentially with memory and tools.
    """
    def __init__(self, config: AIAssistantConfig):
        super().__init__(config)
        self.config: AIAssistantConfig = config # Type hint for convenience
        self.llm = self._initialize_llm()
        self.history: List[Dict[str, Any]] = [] # In-memory conversation history

    def _initialize_llm(self) -> ClaudeLLM:
        """Initializes the LLM client based on the configuration."""
        # Ensure ANTHROPIC_API_KEY is available, ClaudeLLM constructor handles this.
        return ClaudeLLM(
            model_name=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            system_prompt=self.config.system_prompt # ClaudeLLM can take a system_prompt
        )

    def _add_to_history(self, role: str, content: Union[str, List[Dict[str, Any]]]):
        """Adds a message to the conversation history, respecting memory_size."""
        self.history.append({"role": role, "content": content})
        # Prune history if it exceeds memory_size (simplistic pruning: keep last N turns)
        # A 'turn' is usually a user message and an assistant response.
        # memory_size in config refers to number of turns.
        # If memory_size is 10, we keep 10 user messages and 10 assistant responses roughly.
        max_messages = self.config.memory_size * 2 
        if len(self.history) > max_messages:
            self.history = self.history[-max_messages:]
            
    async def _execute_tool_if_needed(self, assistant_response_content: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
        """
        Checks if the assistant response contains a tool_use request.
        If so, (currently) returns a placeholder for tool execution.
        In a real scenario, this would trigger external tool execution.
        Returns content for the next API call (tool_result) or None if no tool was used.
        """
        tool_results_for_next_call = []
        for content_block in assistant_response_content:
            if content_block.get("type") == "tool_use":
                tool_name = content_block.get("name")
                tool_use_id = content_block.get("id")
                tool_input = content_block.get("input", {})

                # TODO: Implement actual tool execution dispatch here.
                # For now, simulate a tool result.
                print(f"[AIAssistantMCP] Assistant wants to use tool: {tool_name} with input: {tool_input}")
                
                # This is where you'd call your actual tool_executor(tool_name, tool_input)
                # and get the tool_output.
                tool_output_content = f"Placeholder result for tool '{tool_name}' with input {tool_input}"
                
                tool_results_for_next_call.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": tool_output_content,
                    # "is_error": False # Optional: if the tool execution failed
                })
        
        return tool_results_for_next_call if tool_results_for_next_call else None

    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handles a user's turn in the conversation with the AI assistant.
        `inputs` should contain a 'message' field for the user's query.
        """
        user_message_content = inputs.get("message")
        if not user_message_content:
            return {"success": False, "error": "Input 'message' is required.", "result": None}

        # Add user message to history before LLM call
        self._add_to_history(role="user", content=user_message_content)
        
        # Prepare messages for LLM (current history + new user message is already done by _add_to_history)
        # The system prompt is handled by ClaudeLLM constructor

        messages_for_llm = self.history.copy() # Send the current history

        try:
            # First call to the LLM
            # The ClaudeLLM.call method expects a list of messages.
            # It does not directly support the 'tools' parameter in its current form.
            # We need to enhance ClaudeLLM or use the Anthropic SDK more directly if available.
            
            # For now, let's assume ClaudeLLM is basic and doesn't handle tool structures in its response.
            # This means the tool_use flow might be more conceptual here until ClaudeLLM is enhanced.
            # If we were using the Anthropic SDK directly:
            # client = anthropic.Anthropic(api_key=self.llm.api_key)
            # response = client.messages.create(
            # model=self.llm.model_name,
            # system=self.config.system_prompt, # Passed if ClaudeLLM doesn't handle it
            # messages=messages_for_llm,
            # tools=self.config.tools if self.config.tools else None,
            # tool_choice={"type": self.config.tool_choice} if self.config.tools else None, # e.g. {"type": "auto"}
            # max_tokens=self.config.max_tokens,
            # temperature=self.config.temperature
            # )
            # assistant_response_content = response.content # This would be a list of content blocks

            # Using the current simplified ClaudeLLM:
            # It expects just a list of messages and returns a string.
            # This simplified version won't support structured tool calls directly.
            # We'll simulate the flow conceptually.
            
            # To make this testable without full SDK integration yet, let's assume
            # ClaudeLLM.call can return a structured response if we mock/modify it later.
            # For now, let's call it and then manually check for tool-like patterns if possible,
            # or just have a simple conversation.

            # Let's simplify: for now, AIAssistant is conversational only, ignoring tools.
            # Tools would require ClaudeLLM to be more sophisticated or direct SDK use.
            
            raw_assistant_response_text = self.llm.call(messages_for_llm)
            
            # Add assistant's response to history
            self._add_to_history(role="assistant", content=raw_assistant_response_text)

            return {
                "success": True,
                "result": raw_assistant_response_text,
                "error": None
            }

            # --- Conceptual Tool Handling (if ClaudeLLM were more advanced) ---
            # This part is commented out as it depends on a more capable ClaudeLLM/SDK
            #
            # assistant_response_content_list = [] # Assume this is what response.content would give
            #
            # # Check for tool use
            # tool_results_content = await self._execute_tool_if_needed(assistant_response_content_list)
            #
            # if tool_results_content:
            #     # If a tool was (conceptually) used, add tool request and result to history
            #     # The Claude API expects the original assistant message requesting tool use,
            #     # then a user message with tool results.
            #     self._add_to_history(role="assistant", content=assistant_response_content_list) # Save original assistant request
            #     self._add_to_history(role="user", content=tool_results_content) # Save tool results as user message
            #
            #     messages_after_tool_call = self.history.copy()
            #
            #     # Second call to LLM with tool results
            #     # final_assistant_response = self.llm.call_with_tools_results(...)
            #     # For now, assume self.llm.call works conceptually for this too
            #     final_assistant_response_text = self.llm.call(messages_after_tool_call)
            #     self._add_to_history(role="assistant", content=final_assistant_response_text)
            #     final_result = final_assistant_response_text
            # else:
            #     # No tool use, just a direct text response
            #     # The first text block is usually the main message
            #     final_text_response = ""
            #     for block in assistant_response_content_list:
            #         if block.get("type") == "text":
            #             final_text_response += block.get("text", "")
            #             break # Usually take the first text block
            #     if not final_text_response and assistant_response_content_list:
            #         final_text_response = json.dumps(assistant_response_content_list) # Fallback
            #
            #     self._add_to_history(role="assistant", content=final_text_response) # Or structured content
            #     final_result = final_text_response
            #
            # return {"success": True, "result": final_result, "error": None}
            # --- End Conceptual Tool Handling ---

        except Exception as e:
            import traceback
            error_message = f"Error executing AI Assistant: {str(e)}\n{traceback.format_exc()}"
            print(error_message)
            # Do not add to history if LLM call fails catastrophically before a response
            return {"success": False, "error": error_message, "result": None}

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def description(self) -> Optional[str]:
        return self.config.description

    # version and other properties can be added if needed by BaseMCPServer contract 