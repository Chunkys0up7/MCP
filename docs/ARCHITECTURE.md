# MCP Architecture Documentation

## Overview
MCP (Modular Control Protocol) is a framework for creating and chaining modular components that can perform various tasks, with a focus on LLM (Large Language Model) interactions and data processing.

## Core Components

### Base Classes

#### BaseMCP
The foundation class for all MCP components.
- **Purpose**: Provides common functionality and interface for all MCPs
- **Key Methods**:
  - `execute()`: Abstract method that must be implemented by all MCPs
  - `name`: Property to get the MCP's name
  - `description`: Property to get the MCP's description

#### MCPConfig
Base configuration class for MCPs.
- **Purpose**: Defines the configuration structure for MCPs
- **Key Attributes**:
  - `name`: Name of the MCP
  - `description`: Optional description of the MCP's purpose
  - `type`: Type of the MCP

### LLM Integration

#### LLMPromptConfig
Configuration class for LLM-based MCPs.
- **Purpose**: Defines how LLM prompts should be configured and executed
- **Key Attributes**:
  - `template`: The prompt template with variable placeholders
  - `input_variables`: List of required input variables
  - `model_name`: LLM model to use (default: "claude-3-sonnet-20240229")
  - `temperature`: Controls randomness in responses (0.0-1.0)
  - `max_tokens`: Maximum tokens in response
  - `system_message`: Optional system message to guide LLM behavior
  - `output_format`: Optional schema for structured output
  - `chain_of_thought`: Enable step-by-step reasoning
  - `context`: Optional persistent context for the MCP

#### ClaudeLLM
Implementation of LLM interface for Claude API.
- **Purpose**: Handles communication with Claude API
- **Key Methods**:
  - `test_connection()`: Validates API connectivity
  - `call()`: Sends prompt to Claude API and returns response
- **Features**:
  - Error handling for API issues
  - Support for different Claude models
  - Configurable temperature and token limits

#### LLMPromptMCP
MCP implementation for LLM prompts.
- **Purpose**: Executes LLM prompts with advanced features
- **Key Methods**:
  - `_format_prompt()`: Formats template with input variables
  - `_build_messages()`: Constructs API message array
  - `_parse_output()`: Validates and structures LLM output
  - `execute()`: Main execution method
- **Features**:
  - Variable interpolation
  - System message support
  - Chain of thought prompting
  - Output validation
  - Context management

## Data Flow

1. **Input Processing**:
   - MCP receives input data
   - Input variables are validated
   - Template is formatted with input data

2. **Prompt Execution**:
   - System message is added if configured
   - Chain of thought is enabled if requested
   - Prompt is sent to LLM

3. **Output Processing**:
   - Response is parsed
   - Output is validated against schema
   - Structured result is returned

## Chaining MCPs

MCPs can be chained together by:
1. Using output from one MCP as input to another
2. Maintaining context between executions
3. Structuring output to match next MCP's input requirements

Example:
```python
# First MCP analyzes data
analysis_result = await analysis_mcp.execute({"data": data})

# Second MCP uses analysis for visualization
viz_result = await viz_mcp.execute({"analysis": analysis_result})
```

## Error Handling

The system implements comprehensive error handling:
- API connectivity issues
- Invalid configurations
- Missing required variables
- Output validation failures
- JSON parsing errors

## Configuration

MCPs are configured through:
1. Configuration objects (e.g., LLMPromptConfig)
2. Environment variables (e.g., API keys)
3. Runtime parameters

## Best Practices

1. **Prompt Design**:
   - Use clear, specific templates
   - Include examples when helpful
   - Structure output format carefully

2. **Error Handling**:
   - Always validate inputs
   - Handle API errors gracefully
   - Provide clear error messages

3. **Performance**:
   - Cache results when possible
   - Use appropriate model sizes
   - Set reasonable token limits

4. **Security**:
   - Never expose API keys
   - Validate all inputs
   - Sanitize outputs

## Future Enhancements

Planned improvements:
1. Support for more LLM providers
2. Enhanced caching mechanisms
3. Advanced prompt templates
4. Better error recovery
5. Monitoring and logging 