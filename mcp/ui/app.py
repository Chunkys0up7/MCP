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
        "Prompt",
        help="Enter your prompt here",
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
        "name": st.session_state.get("mcp_name", ""),
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
    with st.form("create_mcp_form"):
        # Basic Information
        name = st.text_input("MCP Name")
        st.session_state["mcp_name"] = name  # Store the name in session state
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