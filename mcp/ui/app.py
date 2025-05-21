import streamlit as st
import json
from typing import Dict, Any, List
import os
import sys
from pathlib import Path
import time
import logging
import uuid
import traceback

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
from mcp.config.settings import settings
from mcp.config.logging import setup_logging
from mcp.db.session import SessionLocal
from mcp.db.operations import DatabaseOperations
from mcp.cache.redis_manager import RedisCacheManager

# Initialize logging
setup_logging()

# Initialize Redis cache
cache = RedisCacheManager(
    host=settings.redis.host,
    port=settings.redis.port,
    db=settings.redis.db,
    password=settings.redis.password
)

# Initialize the MCP client
client = MCPClient(base_url=config.api_base_url)

# Configure the page
st.set_page_config(
    page_title=settings.streamlit.page_title,
    page_icon=settings.streamlit.page_icon,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme and fonts (approximating Tailwind styles from mockup)
# Using common sans-serif stack as Inter/Noto Sans might not be universally available
# and Streamlit's CSS injection capabilities are limited.
st.markdown(
    """
<style>
    /* Base Streamlit theming for dark mode */
    /* This can be set in .streamlit/config.toml for persistence */
    /* [theme]
    /* base="dark"
    /* primaryColor="#0b79ee" # Blue from mockup button
    /* backgroundColor="#101923" # Dark background from mockup
    /* secondaryBackgroundColor="#1f2937" # Slightly lighter dark for elements
    /* textColor="#ffffff"
    /* font="sans serif"
    
    /* Attempt to apply font globally - Inter is preferred, falls back to sans-serif */
    html, body, [class*="st-"], .stApp {
        font-family: "Inter", "Noto Sans", sans-serif !important;
        background-color: #101923 !important; /* Enforce dark background */
        color: #ffffff !important; /* Enforce light text */
    }
    .stButton>button {
        background-color: #0b79ee !important;
        color: white !important; 
        border-radius: 9999px !important; /* pill shape */
        /* font-weight: bold !important; */ /* Temporarily remove to test */
        border: none !important; 
        padding: 0.5em 1em !important; /* Add explicit padding */
    }
    .stButton>button * { /* Target ALL child elements of the button */
        color: white !important;
        background-color: transparent !important;
        font-weight: bold !important; /* Apply bold here if desired */
    }
    .stButton>button:hover {
        background-color: #0056b3 !important; 
        color: white !important;
    }
    .stButton>button:hover * { /* Ensure hover text color is also white */
        color: white !important;
    }
    .stButton>button:active {
        background-color: #004085 !important; 
        color: white !important;
    }
    .stButton>button:active * { /* Ensure active text color is also white */
        color: white !important;
    }

    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #1f2937 !important;
        color: white !important;
        border-color: #314c68 !important;
    }
    .stSelectbox>div>div {
        background-color: #1f2937 !important;
        border-color: #314c68 !important;
    }
    .stSelectbox>div>div>div>div { /* Dropdown arrow color */
        color: white !important;
    }
     /* Style expanders to look more like cards */
    .streamlit-expanderHeader {
        background-color: #1f2937 !important;
        color: white !important;
        border-radius: 8px !important;
        border: 1px solid #314c68 !important;
        margin-bottom: 10px !important;
    }
    .streamlit-expanderContent {
        background-color: #101923 !important; /* Match main background */
        border-radius: 0 0 8px 8px !important;
        border: 1px solid #314c68 !important;
        border-top: none !important;
        padding: 1rem !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important; /* Ensure headers are white */
    }
    /* Customize radio buttons in sidebar */
    .stRadio>label>div>p {
        color: #e5e7eb !important; /* Lighter gray for sidebar text */
    }
     /* More specific styling for elements if needed */
</style>
    """,
    unsafe_allow_html=True
)

def init_session_state():
    """Initialize session state variables with default values."""
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    
    if "chain_id" not in st.session_state:
        st.session_state.chain_id = None
    
    if "chain_data" not in st.session_state:
        st.session_state.chain_data = {}
    
    if "selected_mcps" not in st.session_state:
        st.session_state.selected_mcps = []
    
    if "node_positions" not in st.session_state:
        st.session_state.node_positions = {}
    
    if "chain_name" not in st.session_state:
        st.session_state.chain_name = ""
    
    if "chain_description" not in st.session_state:
        st.session_state.chain_description = ""
    
    if "execution_mode" not in st.session_state:
        st.session_state.execution_mode = "Sequential"
    
    if "max_retries" not in st.session_state:
        st.session_state.max_retries = 3
    
    if "backoff_factor" not in st.session_state:
        st.session_state.backoff_factor = 1.5
    
    if "error_handling" not in st.session_state:
        st.session_state.error_handling = "Stop on Error"  # Changed from "stop" to match UI options

# Initialize session state at the start of the app
init_session_state()

# Title and description
st.title("Model Context Protocol Dashboard")
st.markdown("""
This dashboard allows you to manage and monitor your MCP servers.
""")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Create MCP", "Manage", "Test", "Chain Builder", "Chain Executor"])

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def render_dashboard() -> None:
    """Display the dashboard page with a summary of active MCPs."""
    st.header("Dashboard")
    logger.debug("Attempting to fetch servers in render_dashboard.")
    try:
        servers = client.get_servers()
        logger.debug(f"Successfully fetched servers. Type: {type(servers)}, Content: {servers}")
        
        if not servers:
            st.info("No MCPs found. Create one to get started!")
            logger.debug("No servers found or list is empty.")
            return
        
        st.markdown(f"<h3 style='color: #e5e7eb;'>Active MCPs ({len(servers)})</h3>", unsafe_allow_html=True)
        st.write("") # Spacer

        # Define number of columns for the card layout
        num_columns = 3 # You can adjust this
        cols = st.columns(num_columns)

        for i, server_item in enumerate(servers):
            logger.debug(f"Processing server at index {i}. Type: {type(server_item)}, Content: {server_item}")
            if not isinstance(server_item, dict):
                logger.error(f"Server item at index {i} is NOT a dictionary. Type: {type(server_item)}, Content: {server_item}")
                # Display the error within the column for visibility
                with cols[i % num_columns]:
                    st.error(f"Error: Invalid server data at index {i}.")
                continue
            
            server_name = server_item.get('name', f'Unnamed Server {i}')
            server_type = server_item.get('type', 'Unknown Type').replace("_", " ").title()
            server_description = server_item.get('description', 'No description available.')
            server_id = server_item.get('id', 'N/A')

            with cols[i % num_columns]:
                # Card-like container using markdown for styling
                st.markdown(f"""
                <div style="
                    background-color: #1f2937; 
                    padding: 20px; 
                    border-radius: 10px; 
                    border: 1px solid #314c68;
                    min-height: 250px; /* Ensure cards have a minimum height */
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    margin-bottom: 20px; /* Add space between cards in the same column */
                ">
                    <div>
                        <h4 style="color: #ffffff; margin-bottom: 5px;">{server_name}</h4>
                        <p style="color: #0b79ee; font-size: 0.9em; margin-bottom: 10px;">Type: {server_type}</p>
                        <p style="color: #d1d5db; font-size: 0.95em; margin-bottom: 15px; height: 60px; overflow-y: auto;">{server_description}</p>
                    </div>
                    <div style="text-align: right;">
                        <small style="color: #6b7280;">ID: {server_id}</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                # Add an expander for more details within the card's column, if desired
                # with st.expander("View Configuration"):
                # st.json(server_item.get('config', {}))

    except AttributeError as ae:
        logger.error(f"AttributeError in render_dashboard: {str(ae)}")
        logger.error(traceback.format_exc())
        st.error(f"An AttributeError occurred: {str(ae)}")
        st.code(traceback.format_exc(), language="text")
    except Exception as e:
        logger.error(f"An unexpected error occurred in render_dashboard: {str(e)}")
        logger.error(traceback.format_exc())
        st.error(f"An unexpected error occurred: {str(e)}")
        st.code(traceback.format_exc(), language="text")

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
                        st.code(traceback.format_exc(), language="python")

def render_chain_builder() -> None:
    """Display the chain builder interface."""
    st.title("Chain Builder")
    
    # Initialize ChainBuilder
    chain_builder = ChainBuilder()
    
    # Render the chain builder interface
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