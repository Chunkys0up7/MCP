import streamlit as st

from mcp.core.types import LLMPromptConfig, MCPType


def build_llm_config() -> LLMPromptConfig:
    """Build LLM configuration through UI."""
    st.subheader("LLM Configuration")

    # Name
    name = st.text_input(
        "Configuration Name", help="Enter a name for this LLM configuration", key="llm_config_name"
    )

    # Model selection
    model_name = st.selectbox(
        "Model",
        ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240229"],
        key="model_name",
    )

    # System prompt
    system_prompt = st.text_area(
        "System Prompt",
        help="Enter a system prompt to guide the model's behavior",
        key="system_prompt",
    )

    # Simple prompt template
    template = st.text_area(
        "Prompt Template",
        help="Enter your prompt template here. Use {variable_name} for input variables.",
        key="template",
    )

    # Input variables configuration
    st.subheader("Input Variables")
    input_vars = st.text_area(
        "Input Variables (one per line)",
        help="Enter input variable names, one per line",
        key="input_variables",
    )
    input_variables = [var.strip() for var in input_vars.split("\n") if var.strip()]

    # Model parameters
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, key="temperature")
    max_tokens = st.number_input("Max Tokens", min_value=1, value=1000, key="max_tokens")

    return LLMPromptConfig(
        name=name,
        type=MCPType.LLM_PROMPT,
        template=template,
        input_variables=input_variables,
        system_prompt=system_prompt if system_prompt else None,
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
    )
