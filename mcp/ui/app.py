import streamlit as st
import requests
from typing import Dict, Any
import json

# Configure the page
st.set_page_config(
    page_title="MCP Dashboard",
    page_icon="🤖",
    layout="wide"
)

# Title and description
st.title("Microservice Control Panel")
st.markdown("""
This dashboard allows you to manage and monitor your microservices.
""")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Create MCP", "Manage MCPs"])

# API endpoint
API_URL = "http://localhost:8000"

def create_mcp(name: str, description: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new MCP instance"""
    try:
        response = requests.post(
            f"{API_URL}/mcps",
            json={
                "name": name,
                "description": description,
                "config": config
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error creating MCP: {str(e)}")
        return None

def get_mcps() -> list:
    """Get all MCP instances"""
    try:
        response = requests.get(f"{API_URL}/mcps")
        response.raise_for_status()
        return response.json()["mcps"]
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching MCPs: {str(e)}")
        return []

def build_llm_config() -> Dict[str, Any]:
    """Build LLM configuration through UI"""
    st.subheader("LLM Configuration")
    
    # Model selection
    model_provider = st.selectbox(
        "Model Provider",
        ["perplexity", "openai", "anthropic"],
        key="model_provider"
    )
    
    # Model name based on provider
    if model_provider == "perplexity":
        model_name = st.selectbox(
            "Model",
            ["pplx-7b-online", "pplx-70b-online", "pplx-7b-chat", "pplx-70b-chat"],
            key="model_name"
        )
    elif model_provider == "openai":
        model_name = st.selectbox(
            "Model",
            ["gpt-3.5-turbo", "gpt-4"],
            key="model_name"
        )
    else:  # anthropic
        model_name = st.selectbox(
            "Model",
            ["claude-2", "claude-instant"],
            key="model_name"
        )
    
    # Prompt template
    template = st.text_area(
        "Prompt Template",
        help="Use {variable_name} for input variables",
        key="template"
    )
    
    # Extract input variables from template
    import re
    input_vars = list(set(re.findall(r'\{([^}]+)\}', template)))
    
    # Model parameters
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, key="temperature")
    max_tokens = st.number_input("Max Tokens", min_value=1, value=1000, key="max_tokens")
    
    return {
        "type": "llm_prompt",
        "template": template,
        "input_variables": input_vars,
        "model_name": model_name,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

def build_notebook_config() -> Dict[str, Any]:
    """Build Jupyter Notebook configuration through UI"""
    st.subheader("Notebook Configuration")
    
    notebook_path = st.text_input(
        "Notebook Path",
        help="Path to the Jupyter notebook file",
        key="notebook_path"
    )
    
    execute_all = st.checkbox("Execute All Cells", value=True, key="execute_all")
    if not execute_all:
        cells_to_execute = st.text_input(
            "Cells to Execute",
            help="Comma-separated list of cell numbers",
            key="cells_to_execute"
        )
    
    timeout = st.number_input(
        "Timeout (seconds)",
        min_value=60,
        value=600,
        key="timeout"
    )
    
    return {
        "type": "jupyter_notebook",
        "notebook_path": notebook_path,
        "execute_all": execute_all,
        "cells_to_execute": cells_to_execute if not execute_all else None,
        "timeout": timeout
    }

# Main content based on selected page
if page == "Dashboard":
    st.header("Dashboard")
    mcps = get_mcps()
    if mcps:
        st.write("Active MCPs:", len(mcps))
        for mcp in mcps:
            st.write(f"- {mcp['name']}: {mcp.get('description', 'No description')}")
    else:
        st.info("No MCPs found. Create one to get started!")

elif page == "Create MCP":
    st.header("Create New MCP")
    with st.form("create_mcp_form"):
        # Basic Information
        name = st.text_input("MCP Name")
        description = st.text_area("Description")
        
        # MCP Type Selection
        mcp_type = st.selectbox(
            "Select MCP Type",
            ["LLM Prompt", "Jupyter Notebook"]
        )
        
        # Type-specific configuration
        if mcp_type == "LLM Prompt":
            config = build_llm_config()
        else:
            config = build_notebook_config()
        
        # Show the final JSON configuration
        st.subheader("Configuration Preview")
        st.json(config)
        
        submitted = st.form_submit_button("Create MCP")
        if submitted:
            if name:
                try:
                    result = create_mcp(name, description, config)
                    if result:
                        st.success(f"Successfully created MCP: {name}")
                except Exception as e:
                    st.error(f"Error creating MCP: {str(e)}")
            else:
                st.error("Please provide a name for the MCP")

elif page == "Manage MCPs":
    st.header("Manage MCPs")
    mcps = get_mcps()
    if mcps:
        for mcp in mcps:
            with st.expander(f"{mcp['name']}"):
                st.write("Description:", mcp.get('description', 'No description'))
                st.write("Configuration:", mcp.get('config', {}))
                if st.button(f"Delete {mcp['name']}", key=f"delete_{mcp['name']}"):
                    st.warning("Delete functionality not implemented yet")
    else:
        st.info("No MCPs to manage. Create one first!") 