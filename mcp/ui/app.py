import streamlit as st
import json
from typing import Dict, Any, List
import os
import sys
from pathlib import Path
import time
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from mcp.core.models import MCPResult
from mcp.api.client import MCPClient
from mcp.core.config import config
from mcp.core.types import MCPType, LLMPromptConfig, JupyterNotebookConfig, PythonScriptConfig
from mcp.mcp_types.llm_prompt import LLMPromptMCP
from mcp.mcp_types.jupyter import JupyterNotebookMCP
from mcp.mcp_types.python_script import PythonScriptMCP
from mcp.ui.widgets.chain_builder import ChainBuilder
from mcp.ui.widgets.chain_executor import ChainExecutor

# Initialize the MCP client
client = MCPClient(base_url=config.api_base_url)

# Configure the page
st.set_page_config(
    page_title="MCP Dashboard",
    page_icon="🤖",
    layout="wide"
)

# Title and description
st.title("Model Context Protocol Dashboard")
st.markdown("""
This dashboard allows you to manage and monitor your MCP servers.
""")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Create MCP", "Manage", "Test", "Chain Builder", "Chain Executor"])

def render_dashboard() -> None:
    """Display the dashboard page with a summary of active MCPs."""
    st.header("Dashboard")
    servers = client.get_servers()
    
    if not servers:
        st.info("No MCPs found. Create one to get started!")
        return
    
    st.write(f"Active MCPs: {len(servers)}")
    for server in servers:
        with st.expander(f"{server['name']} ({server['type']})"):
            st.write("Description:", server.get('description', 'No description'))
            st.write("Configuration:", server.get('config', {}))

def render_create_mcp() -> None:
    """Display the page for creating a new MCP."""
    st.header("Create New MCP")
    
    # Basic Information
    name = st.text_input("MCP Name")
    description = st.text_area("Description")
    
    # MCP Type Selection
    mcp_type = st.selectbox(
        "Select MCP Type",
        [t.value for t in MCPType]
    )
    
    # Type-specific configuration
    if mcp_type == MCPType.LLM_PROMPT:
        config = build_llm_config()
    elif mcp_type == MCPType.JUPYTER_NOTEBOOK:
        config = build_notebook_config()
    else:  # Python Script
        config = build_script_config()
    
    if st.button("Create MCP"):
        if not name:
            st.error("Please provide a name for the MCP")
            return
        
        try:
            # Create appropriate MCP instance
            if mcp_type == MCPType.LLM_PROMPT:
                mcp = LLMPromptMCP(config)
            elif mcp_type == MCPType.JUPYTER_NOTEBOOK:
                mcp = JupyterNotebookMCP(config)
            else:
                mcp = PythonScriptMCP(config)
            
            if mcp.create():
                st.success(f"Successfully created MCP: {name}")
            else:
                st.error("Failed to create MCP")
        except Exception as e:
            st.error(f"Error creating MCP: {str(e)}")

def render_manage_mcps() -> None:
    """Display the page for managing (deleting) MCPs."""
    st.header("Manage MCPs")
    servers = client.get_servers()
    
    if not servers:
        st.info("No MCPs to manage. Create one first!")
        return
    
    for server in servers:
        with st.expander(f"{server['name']} ({server['type']})"):
            st.write("Description:", server.get('description', 'No description'))
            st.write("Type:", server.get('type', 'Unknown'))
            
            # Delete button
            if st.button("Delete", key=f"delete_{server['id']}"):
                if client.delete_server(server['id']):
                    st.success(f"Server {server['name']} deleted successfully!")
                    st.experimental_rerun()
                else:
                    st.error("Failed to delete server")

def render_test_mcps() -> None:
    """Display the page for testing MCPs and viewing results."""
    st.header("Test MCPs")
    servers = client.get_servers()
    
    if not servers:
        st.info("No MCPs to test. Create one first!")
        return
    
    for server in servers:
        with st.expander(f"{server['name']} ({server['type']})"):
            st.write("Description:", server.get('description', 'No description'))
            st.write("Type:", server.get('type', 'Unknown'))
            
            # Always show input fields for execution
            inputs = {}
            input_vars = server['config'].get('input_variables', [])
            if input_vars:
                st.subheader("Execute MCP")
                for var in input_vars:
                    inputs[var] = st.text_input(
                        f"Input: {var}",
                        key=f"input_{server['id']}_{var}"
                    )
            else:
                st.info("No input variables required for this MCP.")
            
            if st.button("Execute", key=f"execute_{server['id']}"):
                st.write("Button pressed!")
                with st.spinner("Executing..."):
                    try:
                        st.code(f"[DEBUG] Executing MCP {server['name']} with inputs: {inputs}", language="text")
                        st.code(f"[DEBUG] Server config: {server['config']}", language="text")
                        data = client.execute_server(server['id'], inputs)
                        st.code(f"[DEBUG] Raw backend response: {data}", language="text")
                        result = MCPResult(**data) if isinstance(data, dict) else data
                        if hasattr(result, 'success') and result.success:
                            st.success("Execution completed!")
                            if getattr(result, 'result', None):
                                st.markdown(f"**Result:**\n\n```\n{result.result}\n```")
                            if getattr(result, 'stdout', None):
                                st.markdown(f"<details><summary>Show stdout</summary>\n\n```\n{result.stdout}\n```\n</details>", unsafe_allow_html=True)
                            if getattr(result, 'stderr', None):
                                st.markdown(f"<details><summary>Show stderr</summary>\n\n```\n{result.stderr}\n```\n</details>", unsafe_allow_html=True)
                        else:
                            error_msg = getattr(result, 'error', 'Unknown error')
                            st.code(f"[ERROR] Execution failed with error: {error_msg}", language="text")
                            st.error(f"Error: {error_msg}")
                    except Exception as e:
                        st.code(f"[EXCEPTION] Execution failed: {str(e)}", language="text")
                        import traceback
                        st.code(traceback.format_exc(), language="python")

def render_chain_builder() -> None:
    """Display the chain builder interface."""
    chain_builder = ChainBuilder()
    chain_builder.render()

def render_chain_executor() -> None:
    """Display the chain executor interface."""
    chain_executor = ChainExecutor()
    chain_executor.render()

def build_llm_config() -> Dict[str, Any]:
    """Build configuration for LLM Prompt MCP."""
    template = st.text_area(
        "Prompt Template",
        help="Use {variable_name} for input variables"
    )
    
    input_vars = st.text_input(
        "Input Variables (comma-separated)",
        help="List of required input variables, e.g., text,tone,style"
    )
    input_variables = [var.strip() for var in input_vars.split(",")] if input_vars else []
    
    model_name = st.selectbox(
        "Model",
        ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240229"],
        index=1
    )
    
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Higher values make output more random, lower values more deterministic"
    )
    
    max_tokens = st.number_input(
        "Max Tokens",
        min_value=100,
        max_value=4000,
        value=1000,
        help="Maximum number of tokens in the response"
    )
    
    system_prompt = st.text_area(
        "System Prompt (Optional)",
        help="Optional system message to guide LLM behavior"
    )
    
    return {
        "type": "llm_prompt",
        "template": template,
        "input_variables": input_variables,
        "model_name": model_name,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "system_prompt": system_prompt if system_prompt else None
    }

# Main content based on selected page
if page == "Dashboard":
    render_dashboard()
elif page == "Create MCP":
    render_create_mcp()
elif page == "Manage":
    render_manage_mcps()
elif page == "Test":
    render_test_mcps()
elif page == "Chain Builder":
    render_chain_builder()
elif page == "Chain Executor":
    render_chain_executor()

# Sidebar with monitoring links
st.sidebar.title("Monitoring")
st.sidebar.markdown("### Dashboards")
st.sidebar.markdown("[Health Check](http://localhost:8000/health)")
st.sidebar.markdown("[Server Stats](http://localhost:8000/stats)")
st.sidebar.markdown("[Prometheus Metrics](http://localhost:8000/metrics)") 