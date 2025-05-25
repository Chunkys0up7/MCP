import json
from typing import Any, Dict, List

import streamlit as st

from mcp.core.types import AIAssistantConfig, MCPType


def build_assistant_config() -> AIAssistantConfig:
    """Build AI assistant configuration UI.

    Returns:
        AIAssistantConfig: Assistant configuration
    """
    st.subheader("AI Assistant Configuration")

    # Name
    name = st.text_input(
        "Configuration Name",
        help="Enter a name for this assistant configuration",
        key="assistant_config_name",
    )

    # Model configuration
    model_name = st.selectbox(
        "Model", ["claude-3-sonnet-20240229", "claude-3-opus-20240229"], index=0
    )

    # System prompt
    system_prompt = st.text_area(
        "System Prompt",
        value="You are a helpful AI assistant.",
        help="Instructions for the AI assistant's behavior",
    )

    # Temperature
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Controls randomness in responses",
    )

    # Max tokens
    max_tokens = st.number_input(
        "Max Tokens", min_value=1, value=1000, help="Maximum number of tokens in response"
    )

    # Memory size
    memory_size = st.number_input(
        "Memory Size", min_value=1, value=10, help="Number of messages to keep in memory"
    )

    # Tools configuration
    st.subheader("Tools")
    tools = build_tools_config()

    # Tool choice
    tool_choice = st.radio("Tool Choice", ["auto", "none"], index=0, help="When to use tools")

    # Response format
    st.subheader("Response Format")
    response_format = build_response_format_config()

    # Metadata
    st.subheader("Metadata")
    metadata = build_metadata_config()

    # Create configuration
    config = AIAssistantConfig(
        name=name,
        type=MCPType.AI_ASSISTANT,
        input_variables=[],  # No input variables for assistant
        model_name=model_name,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        memory_size=memory_size,
        tools=tools,
        tool_choice=tool_choice,
        response_format=response_format,
        metadata=metadata,
    )

    return config


def build_tools_config() -> List[Dict[str, Any]]:
    """Build tools configuration UI.

    Returns:
        List[Dict[str, Any]]: List of tool configurations
    """
    tools = []

    # Add tool button
    if st.button("Add Tool"):
        st.session_state.tool_count = st.session_state.get("tool_count", 0) + 1

    # Tool count
    tool_count = st.session_state.get("tool_count", 0)

    # Build tool configurations
    for i in range(tool_count):
        st.subheader(f"Tool {i + 1}")

        # Tool name
        name = st.text_input("Name", key=f"tool_name_{i}", help="Tool name")

        # Tool description
        description = st.text_area(
            "Description", key=f"tool_description_{i}", help="Tool description"
        )

        # Tool parameters
        st.subheader("Parameters")
        parameters = build_parameters_config(i)

        if name and description and parameters:
            tools.append({"name": name, "description": description, "parameters": parameters})

    return tools


def build_parameters_config(tool_index: int) -> Dict[str, Any]:
    """Build parameters configuration UI.

    Args:
        tool_index: Index of the tool

    Returns:
        Dict[str, Any]: Parameter configuration
    """
    parameters = {}

    # Add parameter button
    if st.button("Add Parameter", key=f"add_param_{tool_index}"):
        st.session_state[f"param_count_{tool_index}"] = (
            st.session_state.get(f"param_count_{tool_index}", 0) + 1
        )

    # Parameter count
    param_count = st.session_state.get(f"param_count_{tool_index}", 0)

    # Build parameter configurations
    for i in range(param_count):
        st.subheader(f"Parameter {i + 1}")

        # Parameter name
        name = st.text_input("Name", key=f"param_name_{tool_index}_{i}", help="Parameter name")

        # Parameter type
        param_type = st.selectbox(
            "Type",
            ["str", "int", "float", "bool", "dict", "list"],
            key=f"param_type_{tool_index}_{i}",
            help="Parameter type",
        )

        # Required flag
        required = st.checkbox(
            "Required", key=f"param_required_{tool_index}_{i}", help="Whether parameter is required"
        )

        if name and param_type:
            parameters[name] = {"type": param_type, "required": required}

    return parameters


def build_response_format_config() -> Dict[str, Any]:
    """Build response format configuration UI.

    Returns:
        Dict[str, Any]: Response format configuration
    """
    response_format = {}

    # Type
    format_type = st.selectbox("Type", ["text", "json", "markdown"], help="Response format type")

    if format_type == "json":
        # JSON schema
        schema = st.text_area("JSON Schema", help="JSON schema for response format")
        try:
            response_format["schema"] = json.loads(schema)
        except json.JSONDecodeError:
            st.error("Invalid JSON schema")

    return response_format


def build_metadata_config() -> Dict[str, Any]:
    """Build metadata configuration UI.

    Returns:
        Dict[str, Any]: Metadata configuration
    """
    metadata = {}

    # Add metadata button
    if st.button("Add Metadata"):
        st.session_state.metadata_count = st.session_state.get("metadata_count", 0) + 1

    # Metadata count
    metadata_count = st.session_state.get("metadata_count", 0)

    # Build metadata configurations
    for i in range(metadata_count):
        st.subheader(f"Metadata {i + 1}")

        # Key
        key = st.text_input("Key", key=f"metadata_key_{i}", help="Metadata key")

        # Value
        value = st.text_input("Value", key=f"metadata_value_{i}", help="Metadata value")

        if key and value:
            metadata[key] = value

    return metadata
