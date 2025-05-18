import streamlit as st
import requests
from typing import Dict, Any
import json

# API Configuration
API_BASE_URL = "http://localhost:8000"

def main():
    st.title("Microservice Control Panel (MCP)")
    
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["MCP Builder", "MCP Registry", "Execute MCP"]
    )
    
    if page == "MCP Builder":
        render_mcp_builder()
    elif page == "MCP Registry":
        render_mcp_registry()
    else:
        render_execution_ui()

def render_mcp_builder():
    """Render the MCP builder interface"""
    st.header("MCP Builder")
    
    # MCP Type Selection
    mcp_type = st.selectbox(
        "Select MCP Type",
        ["LLM Prompt", "Jupyter Notebook"]
    )
    
    # Basic Information
    name = st.text_input("MCP Name")
    description = st.text_area("Description")
    
    # Type-specific configuration
    if mcp_type == "LLM Prompt":
        config = render_llm_config()
    else:
        config = render_notebook_config()
    
    if st.button("Create MCP"):
        if not name:
            st.error("MCP name is required")
            return
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/mcps",
                json={
                    "type": mcp_type.lower().replace(" ", "_"),
                    "config": {
                        "name": name,
                        "description": description,
                        **config
                    }
                }
            )
            response.raise_for_status()
            st.success("MCP created successfully!")
        except Exception as e:
            st.error(f"Error creating MCP: {str(e)}")

def render_llm_config() -> Dict[str, Any]:
    """Render LLM-specific configuration"""
    config = {}
    
    # Model Provider
    config["model_provider"] = st.selectbox(
        "Model Provider",
        ["openai", "anthropic", "huggingface"]
    )
    
    # Model Selection
    if config["model_provider"] == "openai":
        config["model_name"] = st.selectbox(
            "Model",
            ["gpt-3.5-turbo", "gpt-4"]
        )
    elif config["model_provider"] == "anthropic":
        config["model_name"] = st.selectbox(
            "Model",
            ["claude-2", "claude-instant"]
        )
    
    # Prompt Template
    config["prompt_template"] = st.text_area(
        "Prompt Template",
        help="Use {variable_name} for input variables"
    )
    
    # Model Parameters
    config["temperature"] = st.slider("Temperature", 0.0, 1.0, 0.7)
    config["max_tokens"] = st.number_input("Max Tokens", min_value=1, value=1000)
    
    return config

def render_notebook_config() -> Dict[str, Any]:
    """Render Jupyter Notebook-specific configuration"""
    config = {}
    
    # Notebook Path
    config["notebook_path"] = st.text_input(
        "Notebook Path",
        help="Path to the Jupyter notebook file"
    )
    
    # Execution Options
    config["execute_all"] = st.checkbox("Execute All Cells", value=True)
    if not config["execute_all"]:
        config["cells_to_execute"] = st.text_input(
            "Cells to Execute",
            help="Comma-separated list of cell numbers"
        )
    
    config["timeout"] = st.number_input(
        "Timeout (seconds)",
        min_value=60,
        value=600
    )
    
    return config

def render_mcp_registry():
    """Render the MCP registry interface"""
    st.header("MCP Registry")
    
    try:
        response = requests.get(f"{API_BASE_URL}/mcps")
        response.raise_for_status()
        mcps = response.json()
        
        for mcp in mcps:
            with st.expander(f"{mcp['name']} ({mcp['type']})"):
                st.write(f"ID: {mcp['id']}")
                st.write(f"Version: {mcp['version']}")
                
                if st.button("Delete", key=f"delete_{mcp['id']}"):
                    try:
                        response = requests.delete(f"{API_BASE_URL}/mcps/{mcp['id']}")
                        response.raise_for_status()
                        st.success("MCP deleted successfully!")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Error deleting MCP: {str(e)}")
    
    except Exception as e:
        st.error(f"Error fetching MCPs: {str(e)}")

def render_execution_ui():
    """Render the MCP execution interface"""
    st.header("Execute MCP")
    
    try:
        # Get available MCPs
        response = requests.get(f"{API_BASE_URL}/mcps")
        response.raise_for_status()
        mcps = response.json()
        
        if not mcps:
            st.warning("No MCPs available. Create one first!")
            return
        
        # MCP Selection
        selected_mcp = st.selectbox(
            "Select MCP",
            options=mcps,
            format_func=lambda x: f"{x['name']} ({x['type']})"
        )
        
        # Input Parameters
        st.subheader("Input Parameters")
        inputs = {}
        
        # For LLM Prompt MCPs
        if selected_mcp["type"] == "LLMPromptMCP":
            prompt_template = selected_mcp.get("config", {}).get("prompt_template", "")
            input_vars = extract_input_variables(prompt_template)
            
            for var in input_vars:
                inputs[var] = st.text_input(f"Input: {var}")
        
        # For Jupyter Notebook MCPs
        elif selected_mcp["type"] == "JupyterNotebookMCP":
            inputs["parameters"] = st.text_area(
                "Notebook Parameters (JSON)",
                help="Enter parameters as JSON object"
            )
        
        # Execute Button
        if st.button("Execute"):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/mcps/{selected_mcp['id']}/execute",
                    json={"inputs": inputs}
                )
                response.raise_for_status()
                result = response.json()
                
                st.subheader("Results")
                st.json(result)
                
            except Exception as e:
                st.error(f"Error executing MCP: {str(e)}")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

def extract_input_variables(template: str) -> list[str]:
    """Extract input variables from prompt template"""
    import re
    return list(set(re.findall(r'\{([^}]+)\}', template)))

if __name__ == "__main__":
    main() 