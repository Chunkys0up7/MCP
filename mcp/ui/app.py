import streamlit as st
import requests
from typing import Dict, Any
import json
import os

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
page = st.sidebar.radio("Go to", ["Dashboard", "Create MCP", "Manage MCPs", "Chain MCPs"])

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
                "type": config["type"],
                "config": config
            }
        )
        if response.status_code == 400:
            st.error(f"Error creating MCP: {response.json().get('detail', 'Unknown error')}")
            return None
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
        data = response.json()
        return data.get("mcps", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching MCPs: {str(e)}")
        return []

def build_llm_config() -> Dict[str, Any]:
    """Build LLM configuration through UI"""
    st.subheader("LLM Configuration")
    
    # Model selection
    model_provider = st.selectbox(
        "Model Provider",
        ["perplexity"],
        key="model_provider"
    )
    
    # Model name based on provider
    if model_provider == "perplexity":
        model_name = st.selectbox(
            "Model",
            [
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240229"
            ],
            key="model_name"
        )
    
    # System prompt
    system_prompt = st.text_area(
        "System Prompt",
        help="Enter a system prompt to guide the model's behavior",
        key="system_prompt"
    )
    
    # Simple prompt template
    template = st.text_area(
        "Prompt Template",
        help="Enter your prompt template here. Use {variable_name} for input variables.",
        key="template"
    )
    
    # Input variables configuration
    st.subheader("Input Variables")
    input_vars = st.text_area(
        "Input Variables (one per line)",
        help="Enter input variable names, one per line",
        key="input_variables"
    )
    input_variables = [var.strip() for var in input_vars.split('\n') if var.strip()]
    
    # Model parameters
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, key="temperature")
    max_tokens = st.number_input("Max Tokens", min_value=1, value=1000, key="max_tokens")
    
    return {
        "type": "llm_prompt",
        "template": template,
        "input_variables": input_variables,
        "system_prompt": system_prompt,
        "model_name": model_name,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

def build_notebook_config() -> Dict[str, Any]:
    """Build Jupyter Notebook configuration through UI"""
    st.subheader("Notebook Configuration")
    
    # File source selection
    file_source = st.radio(
        "Notebook Source",
        ["Use Existing File", "Create New Notebook"],
        key="notebook_source"
    )
    
    if file_source == "Use Existing File":
        notebook_path = st.text_input(
            "Notebook Path",
            help="Path to the Jupyter notebook file",
            key="notebook_path"
        )
    else:
        # Create new notebook
        notebook_name = st.text_input(
            "Notebook Name",
            help="Name for the new notebook (without .ipynb extension)",
            key="new_notebook_name"
        )
        
        # Basic notebook template
        notebook_content = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": ["# New Notebook\n\nAdd your cells below."]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "source": ["# Your first code cell"],
                    "outputs": []
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }
        
        # Save notebook button
        if st.button("Save Notebook"):
            if notebook_name:
                notebook_path = f"mcp/notebooks/{notebook_name}.ipynb"
                os.makedirs(os.path.dirname(notebook_path), exist_ok=True)
                with open(notebook_path, 'w') as f:
                    json.dump(notebook_content, f, indent=2)
                st.success(f"Notebook saved to {notebook_path}")
            else:
                st.error("Please provide a notebook name")
    
    execute_all = st.checkbox("Execute All Cells", value=True, key="execute_all")
    if not execute_all:
        cells_to_execute = st.text_input(
            "Cells to Execute",
            help="Comma-separated list of cell numbers (e.g., 1,2,3)",
            key="cells_to_execute"
        )
    
    # Input variables configuration
    st.subheader("Input Variables")
    input_vars = st.text_area(
        "Input Variables (one per line)",
        help="Enter input variable names that will be available in the notebook",
        key="notebook_input_variables"
    )
    input_variables = [var.strip() for var in input_vars.split('\n') if var.strip()]
    
    timeout = st.number_input(
        "Timeout (seconds)",
        min_value=60,
        value=600,
        help="Maximum execution time for the notebook",
        key="notebook_timeout"
    )
    
    return {
        "type": "jupyter_notebook",
        "notebook_path": notebook_path if file_source == "Use Existing File" else f"mcp/notebooks/{notebook_name}.ipynb",
        "execute_all": execute_all,
        "cells_to_execute": cells_to_execute if not execute_all else None,
        "input_variables": input_variables,
        "timeout": timeout
    }

def build_python_script_config() -> Dict[str, Any]:
    """Build Python Script configuration through UI"""
    st.subheader("Python Script Configuration")
    
    # File source selection
    file_source = st.radio(
        "Script Source",
        ["Use Existing File", "Create New Script"],
        key="script_source"
    )
    
    if file_source == "Use Existing File":
        script_path = st.text_input(
            "Script Path",
            help="Path to the Python script file",
            key="script_path"
        )
    else:
        # Create new script
        script_name = st.text_input(
            "Script Name",
            help="Name for the new script (without .py extension)",
            key="new_script_name"
        )
        
        # Script editor
        st.subheader("Script Editor")
        script_content = st.text_area(
            "Script Content",
            value="""# Your Python script
import sys

def main():
    # Your code here
    print("Hello, World!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
""",
            height=400,
            key="script_content"
        )
        
        # Save script button
        if st.button("Save Script"):
            if script_name:
                script_path = f"mcp/scripts/{script_name}.py"
                os.makedirs(os.path.dirname(script_path), exist_ok=True)
                with open(script_path, 'w') as f:
                    f.write(script_content)
                st.success(f"Script saved to {script_path}")
            else:
                st.error("Please provide a script name")
    
    # Requirements configuration
    st.subheader("Python Requirements")
    requirements = st.text_area(
        "Package Requirements",
        help="List of Python package requirements (one per line, e.g., requests==2.31.0)",
        key="requirements"
    )
    
    # Input variables configuration
    st.subheader("Input Variables")
    input_vars = st.text_area(
        "Input Variables",
        help="List of input variables that will be available in the script (one per line)",
        key="script_input_variables"
    )
    input_variables = [var.strip() for var in input_vars.split('\n') if var.strip()]
    
    # Execution settings
    st.subheader("Execution Settings")
    virtual_env = st.checkbox(
        "Use Virtual Environment",
        value=True,
        help="Whether to execute the script in a virtual environment",
        key="virtual_env"
    )
    
    timeout = st.number_input(
        "Timeout (seconds)",
        min_value=60,
        value=600,
        help="Maximum execution time for the script",
        key="script_timeout"
    )
    
    return {
        "type": "python_script",
        "script_path": script_path if file_source == "Use Existing File" else f"mcp/scripts/{script_name}.py",
        "requirements": [r.strip() for r in requirements.split("\n") if r.strip()],
        "input_variables": input_variables,
        "virtual_env": virtual_env,
        "timeout": timeout
    }

def execute_mcp(mcp_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Execute an MCP instance with given inputs"""
    try:
        response = requests.post(
            f"{API_URL}/mcps/{mcp_id}/execute",
            json=inputs
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error executing MCP: {str(e)}")
        return None

# Main content based on selected page
if page == "Dashboard":
    st.header("Dashboard")
    mcps = get_mcps()
    if mcps:
        st.write(f"Active MCPs: {len(mcps)}")
        for mcp in mcps:
            with st.expander(f"{mcp['name']} ({mcp['type']})"):
                st.write("Description:", mcp.get('description', 'No description'))
                st.write("Configuration:", mcp.get('config', {}))
    else:
        st.info("No MCPs found. Create one to get started!")

elif page == "Create MCP":
    st.header("Create New MCP")
    
    # Basic Information
    name = st.text_input("MCP Name")
    st.session_state["mcp_name"] = name  # Store the name in session state
    description = st.text_area("Description")
    
    # MCP Type Selection
    mcp_type = st.selectbox(
        "Select MCP Type",
        ["LLM Prompt", "Jupyter Notebook", "Python Script"]
    )
    
    # Type-specific configuration
    config = None
    if mcp_type == "LLM Prompt":
        with st.form("llm_config_form"):
            config = build_llm_config()
            submitted = st.form_submit_button("Create MCP")
    elif mcp_type == "Jupyter Notebook":
        with st.form("notebook_config_form"):
            config = build_notebook_config()
            submitted = st.form_submit_button("Create MCP")
    else:  # Python Script
        with st.form("python_script_config_form"):
            config = build_python_script_config()
            submitted = st.form_submit_button("Create MCP")
    
    # Show the final JSON configuration
    if config:
        st.subheader("Configuration Preview")
        st.json(config)
        
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
                st.write("Type:", mcp.get('type', 'Unknown'))
                st.subheader("Execute MCP")
                mcp_inputs = {}
                if 'input_variables' in mcp['config'] and mcp['config']['input_variables']:
                    for var in mcp['config']['input_variables']:
                        mcp_inputs[var] = st.text_input(f"Input: {var}", key=f"{mcp['id']}_{var}")
                if st.button(f"Execute {mcp['name']}", key=f"execute_{mcp['id']}"):
                    with st.spinner("Executing..."):
                        result = execute_mcp(mcp['id'], mcp_inputs)
                        if result:
                            if "error" in result:
                                st.error(f"Error: {result['error']}")
                            else:
                                st.success("Execution completed!")
                                st.write("Result:")
                                st.write(result.get('result', 'No result'))
                                st.write("Model:", result.get('model', 'Unknown'))
                                st.write("Prompt:", result.get('prompt', 'Unknown'))
                if mcp['type'] == 'jupyter_notebook':
                    if st.button(f"Execute {mcp['name']} Notebook", key=f"execute_nb_{mcp['id']}"):
                        with st.spinner("Executing notebook..."):
                            result = execute_mcp(mcp['id'], mcp_inputs)
                            if result:
                                st.success("Notebook execution completed!")
                                st.json(result)
                if st.button(f"Delete {mcp['name']}", key=f"delete_{mcp['id']}"):
                    st.warning("Delete functionality not implemented yet")
    else:
        st.info("No MCPs to manage. Create one first!")

elif page == "Chain MCPs":
    st.header("Chain MCPs")
    mcps = get_mcps()
    if len(mcps) < 2:
        st.info("You need at least two MCPs to create a chain.")
    else:
        mcp_names = [f"{m['name']} ({m['type']})" for m in mcps]
        mcp1_idx = st.selectbox("Select first MCP", range(len(mcps)), format_func=lambda i: mcp_names[i], key="chain_mcp1")
        mcp2_idx = st.selectbox("Select second MCP", range(len(mcps)), format_func=lambda i: mcp_names[i], key="chain_mcp2")
        mcp1 = mcps[mcp1_idx]
        mcp2 = mcps[mcp2_idx]
        st.write(f"Chaining '{mcp1['name']}' → '{mcp2['name']}'")

        # Input fields for first MCP
        mcp1_inputs = {}
        if 'input_variables' in mcp1['config'] and mcp1['config']['input_variables']:
            st.subheader(f"Inputs for {mcp1['name']}")
            for var in mcp1['config']['input_variables']:
                mcp1_inputs[var] = st.text_input(f"{mcp1['name']} input: {var}", key=f"chain_{mcp1['id']}_{var}")
        else:
            st.info(f"No input variables for {mcp1['name']}")

        if st.button("Run First MCP", key="run_chain_mcp1"):
            with st.spinner("Running first MCP..."):
                mcp1_result = execute_mcp(mcp1['id'], mcp1_inputs)
                if mcp1_result:
                    st.success("First MCP executed!")
                    st.json(mcp1_result)
                    st.session_state['last_chain_result'] = mcp1_result

        # If first MCP has been run, allow mapping to second MCP
        if 'last_chain_result' in st.session_state:
            mcp1_result = st.session_state['last_chain_result']
            st.subheader(f"Map output from {mcp1['name']} to inputs for {mcp2['name']}")
            mcp2_inputs = {}
            if 'input_variables' in mcp2['config'] and mcp2['config']['input_variables']:
                for var in mcp2['config']['input_variables']:
                    # Let user pick a value from mcp1_result or enter manually
                    options = list(mcp1_result.keys())
                    selected = st.selectbox(f"Map to {var}", options + ["<manual input>"], key=f"chain_map_{var}")
                    if selected != "<manual input>":
                        mcp2_inputs[var] = mcp1_result[selected]
                    else:
                        mcp2_inputs[var] = st.text_input(f"Manual input for {var}", key=f"chain_manual_{var}")
            else:
                st.info(f"No input variables for {mcp2['name']}")
            if st.button("Run Second MCP", key="run_chain_mcp2"):
                with st.spinner("Running second MCP..."):
                    mcp2_result = execute_mcp(mcp2['id'], mcp2_inputs)
                    if mcp2_result:
                        st.success("Second MCP executed!")
                        st.json(mcp2_result) 