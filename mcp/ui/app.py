import streamlit as st
import requests
from typing import Dict, Any
import json
import os
import time
from pathlib import Path

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

# Add WebSocket error handling
def handle_websocket_error(func):
    """Decorator to handle WebSocket errors and implement reconnection logic."""
    def wrapper(*args, **kwargs):
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if "WebSocketClosedError" in str(e) or "StreamClosedError" in str(e):
                    if attempt < max_retries - 1:
                        st.warning(f"Connection lost. Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        st.error("Failed to establish connection after multiple attempts. Please refresh the page.")
                        raise
                else:
                    raise
    return wrapper

def get_api_url():
    """Get the API URL, trying different ports if needed"""
    ports = range(8000, 9000)
    for port in ports:
        try:
            response = requests.get(f"http://localhost:{port}/mcps")
            if response.status_code == 200:
                return f"http://localhost:{port}"
        except requests.exceptions.RequestException:
            continue
    return "http://localhost:8000"  # Default fallback

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
        
        # Notebook editor with cells
        st.subheader("Notebook Editor")
        
        # Initialize cells in session state if not present
        if 'notebook_cells' not in st.session_state:
            st.session_state.notebook_cells = [
                {"type": "markdown", "content": "# New Notebook\n\nAdd your cells below."},
                {"type": "code", "content": "# Your first code cell"}
            ]
        
        # Add new cell button
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Add Code Cell"):
                st.session_state.notebook_cells.append({"type": "code", "content": ""})
        with col2:
            if st.button("Add Markdown Cell"):
                st.session_state.notebook_cells.append({"type": "markdown", "content": ""})
        
        # Display and edit cells
        for i, cell in enumerate(st.session_state.notebook_cells):
            st.subheader(f"Cell {i+1} ({cell['type']})")
            # Cell type selector
            cell_type = st.radio(
                "Cell Type",
                ["code", "markdown"],
                index=0 if cell["type"] == "code" else 1,
                key=f"cell_type_{i}"
            )
            
            # Cell content editor
            cell_content = st.text_area(
                "Cell Content",
                value=cell["content"],
                height=150,
                key=f"cell_content_{i}"
            )
            
            # Update cell in session state
            st.session_state.notebook_cells[i] = {
                "type": cell_type,
                "content": cell_content
            }
            
            # Delete cell button
            if st.button("Delete Cell", key=f"delete_cell_{i}"):
                st.session_state.notebook_cells.pop(i)
                st.rerun()
            
            st.markdown("---")  # Add a separator between cells
        
        # Save notebook button
        if st.button("Save Notebook"):
            if notebook_name:
                try:
                    # Convert cells to notebook format
                    notebook_content = {
                        "cells": [
                            {
                                "cell_type": cell["type"],
                                "metadata": {},
                                "source": [cell["content"]],
                                "execution_count": None,
                                "outputs": []
                            }
                            for cell in st.session_state.notebook_cells
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
                    
                    notebook_path = f"mcp/notebooks/{notebook_name}.ipynb"
                    os.makedirs(os.path.dirname(notebook_path), exist_ok=True)
                    with open(notebook_path, 'w') as f:
                        json.dump(notebook_content, f, indent=2)
                    st.success(f"Notebook saved to {notebook_path}")
                except Exception as e:
                    st.error(f"Error saving notebook: {str(e)}")
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
                try:
                    script_path = f"mcp/scripts/{script_name}.py"
                    os.makedirs(os.path.dirname(script_path), exist_ok=True)
                    with open(script_path, 'w') as f:
                        f.write(script_content)
                    st.success(f"Script saved to {script_path}")
                except Exception as e:
                    st.error(f"Error saving script: {str(e)}")
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

@handle_websocket_error
def execute_mcp(mcp_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Execute an MCP instance with given inputs"""
    try:
        response = requests.post(
            f"http://127.0.0.1:8000/api/mcps/{mcp_id}/execute",
            json=inputs
        )
        response.raise_for_status()
        result = response.json()
        
        if "error" in result:
            st.error(f"Error executing MCP: {result['error']}")
            return None
        elif "result" in result:
            # LLM prompt response
            return result
        else:
            # Generic response
            return {
                "result": result,
                "success": True
            }
    except requests.exceptions.RequestException as e:
        st.error(f"Error executing MCP: {str(e)}")
        return None

def build_ai_assistant(mcp_type: str, current_config: Dict[str, Any] = None) -> None:
    """
    Build AI assistant component to help users create MCPs.
    Visually enhanced: shows MCP type badge, uses a styled container, and clarifies that help is specific to the MCP type.
    Args:
        mcp_type (str): The type of MCP being created (LLM Prompt, Jupyter Notebook, Python Script).
        current_config (Dict[str, Any], optional): The current MCP configuration.
    """
    # Sidebar container for the assistant
    with st.sidebar:
        with st.container():
            # MCP type badge and description
            mcp_type_map = {
                "LLM Prompt": ("🧠 LLM Prompt", "Help for language model prompt MCPs."),
                "Jupyter Notebook": ("📓 Jupyter Notebook", "Help for notebook-based MCPs."),
                "Python Script": ("🐍 Python Script", "Help for Python script MCPs.")
            }
            badge, desc = mcp_type_map.get(mcp_type, ("❓ Unknown", "Help for this MCP type."))
            st.markdown(f"<div style='display:flex;align-items:center;gap:0.5em;'><span style='background:#262730;color:#fff;padding:0.2em 0.7em;border-radius:1em;font-weight:bold;font-size:1em;'>{badge}</span><span style='color:#aaa;font-size:0.9em;'>{desc}</span></div>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:0.5em 0;' />", unsafe_allow_html=True)
            st.markdown("<span style='color:#aaa;font-size:0.9em;'>AI Assistant help is <b>specific to the type of MCP</b> you are creating.</span>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            # Initialize chat history in session state if not present
            if 'assistant_messages' not in st.session_state:
                st.session_state.assistant_messages = []
            if 'last_assistant_response' not in st.session_state:
                st.session_state.last_assistant_response = None

            # Display chat history with icons
            for message in st.session_state.assistant_messages:
                icon = "🧑‍💻" if message["role"] == "user" else "🤖"
                st.markdown(f"<div style='margin-bottom:0.5em;'><span style='font-size:1.2em;'>{icon}</span> <span style='background:#23242b;padding:0.5em 0.8em;border-radius:0.7em;color:#fff;'>{message['content']}</span></div>", unsafe_allow_html=True)

            # Input form
            with st.form(key="assistant_form"):
                user_input = st.text_input("Ask for help", key="assistant_input")
                submit_button = st.form_submit_button("Send")

            if submit_button and user_input:
                # Prevent repeated generic questions
                if (st.session_state.last_assistant_response and 
                    user_input.lower() in ["help me", "help", "what can you do", "show options"]):
                    st.warning("I've already shown you the available help topics. Please ask a specific question about what you'd like to know more about.")
                    return
                # Add user message
                st.session_state.assistant_messages.append({"role": "user", "content": user_input})
                # Generate response
                if mcp_type == "LLM Prompt":
                    response = generate_llm_prompt_help(user_input, current_config)
                elif mcp_type == "Jupyter Notebook":
                    response = generate_notebook_help(user_input, current_config)
                else:
                    response = generate_script_help(user_input, current_config)
                st.session_state.last_assistant_response = response
                st.session_state.assistant_messages.append({"role": "assistant", "content": response})
                st.rerun()

def generate_llm_prompt_help(user_input: str, current_config: Dict[str, Any] = None) -> str:
    """Generate help for LLM prompt creation"""
    # Common help topics
    help_topics = {
        "template": "Your prompt template should be clear and specific. Use {variable_name} for input variables.",
        "system_prompt": "The system prompt helps set the context and behavior of the model. Make it specific to your use case.",
        "input_variables": "Input variables should be descriptive and match the {variable_name} placeholders in your template.",
        "model": "Choose the model based on your needs:\n- Opus: Best for complex tasks\n- Sonnet: Good balance of capability and speed\n- Haiku: Fastest, good for simple tasks",
        "temperature": "Temperature controls randomness:\n- 0.0-0.3: Very focused and deterministic\n- 0.4-0.7: Balanced creativity\n- 0.8-1.0: More creative and varied",
        "max_tokens": "Max tokens limits response length. Consider your use case:\n- Short responses: 100-500\n- Medium responses: 500-2000\n- Long responses: 2000+"
    }
    
    # Analyze user input for keywords
    input_lower = user_input.lower()
    response = []
    
    # Check for specific help requests
    if "template" in input_lower or "prompt" in input_lower:
        response.append(help_topics["template"])
    if "system" in input_lower:
        response.append(help_topics["system_prompt"])
    if "input" in input_lower or "variable" in input_lower:
        response.append(help_topics["input_variables"])
    if "model" in input_lower:
        response.append(help_topics["model"])
    if "temperature" in input_lower:
        response.append(help_topics["temperature"])
    if "token" in input_lower or "length" in input_lower:
        response.append(help_topics["max_tokens"])
    
    # If no specific help was requested, provide general guidance
    if not response:
        if input_lower in ["help me", "help", "what can you do", "show options"]:
            response = [
                "I can help you with:\n",
                "- Writing effective prompt templates",
                "- Setting up system prompts",
                "- Defining input variables",
                "- Choosing the right model",
                "- Configuring temperature and max tokens",
                "\nPlease ask a specific question about any of these topics!"
            ]
        else:
            response = [
                "I'm not sure what you're asking about. Could you please be more specific?",
                "For example, you could ask about:",
                "- How to write a good prompt template",
                "- What temperature setting to use",
                "- How to define input variables",
                "- Which model to choose for your use case"
            ]
    
    return "\n".join(response)

def generate_notebook_help(user_input: str, current_config: Dict[str, Any] = None) -> str:
    """Generate help for notebook creation"""
    # Common help topics
    help_topics = {
        "structure": "A good notebook structure includes:\n- Introduction and setup cells\n- Data loading and preprocessing\n- Analysis and visualization\n- Results and conclusions",
        "cells": "Use different cell types effectively:\n- Markdown cells for documentation\n- Code cells for execution\n- Raw cells for special content",
        "execution": "Execution settings:\n- Execute All: Runs all cells in sequence\n- Specific Cells: Run only selected cells\n- Timeout: Set appropriate execution time",
        "variables": "Input variables should be:\n- Clearly named\n- Documented in markdown\n- Used consistently throughout the notebook",
        "dependencies": "Make sure to include all required packages in your notebook's first code cell"
    }
    
    # Analyze user input for keywords
    input_lower = user_input.lower()
    response = []
    
    # Check for specific help requests
    if "structure" in input_lower or "organize" in input_lower:
        response.append(help_topics["structure"])
    if "cell" in input_lower:
        response.append(help_topics["cells"])
    if "execute" in input_lower or "run" in input_lower:
        response.append(help_topics["execution"])
    if "variable" in input_lower or "input" in input_lower:
        response.append(help_topics["variables"])
    if "package" in input_lower or "dependency" in input_lower:
        response.append(help_topics["dependencies"])
    
    # If no specific help was requested, provide general guidance
    if not response:
        if input_lower in ["help me", "help", "what can you do", "show options"]:
            response = [
                "I can help you with:\n",
                "- Structuring your notebook",
                "- Using different cell types",
                "- Setting up execution",
                "- Managing input variables",
                "- Handling dependencies",
                "\nPlease ask a specific question about any of these topics!"
            ]
        else:
            response = [
                "I'm not sure what you're asking about. Could you please be more specific?",
                "For example, you could ask about:",
                "- How to structure your notebook",
                "- How to use different cell types",
                "- How to set up execution",
                "- How to manage input variables"
            ]
    
    return "\n".join(response)

def generate_script_help(user_input: str, current_config: Dict[str, Any] = None) -> str:
    """Generate help for Python script creation"""
    # Common help topics
    help_topics = {
        "structure": "A well-structured script includes:\n- Imports at the top\n- Configuration and constants\n- Main function\n- Helper functions\n- if __name__ == '__main__' block",
        "requirements": "List all required packages with versions:\n- Use requirements.txt format\n- Specify exact versions for stability\n- Include all dependencies",
        "variables": "Input variables should be:\n- Clearly typed\n- Documented with docstrings\n- Validated when possible",
        "virtual_env": "Virtual environment benefits:\n- Isolated dependencies\n- Reproducible environment\n- Clean execution",
        "timeout": "Set appropriate timeout based on:\n- Script complexity\n- Expected execution time\n- Resource requirements"
    }
    
    # Analyze user input for keywords
    input_lower = user_input.lower()
    response = []
    
    # Check for specific help requests
    if "structure" in input_lower or "organize" in input_lower:
        response.append(help_topics["structure"])
    if "requirement" in input_lower or "package" in input_lower:
        response.append(help_topics["requirements"])
    if "variable" in input_lower or "input" in input_lower:
        response.append(help_topics["variables"])
    if "virtual" in input_lower or "environment" in input_lower:
        response.append(help_topics["virtual_env"])
    if "timeout" in input_lower or "execution" in input_lower:
        response.append(help_topics["timeout"])
    
    # If no specific help was requested, provide general guidance
    if not response:
        if input_lower in ["help me", "help", "what can you do", "show options"]:
            response = [
                "I can help you with:\n",
                "- Structuring your Python script",
                "- Managing requirements",
                "- Handling input variables",
                "- Setting up virtual environments",
                "- Configuring execution settings",
                "\nPlease ask a specific question about any of these topics!"
            ]
        else:
            response = [
                "I'm not sure what you're asking about. Could you please be more specific?",
                "For example, you could ask about:",
                "- How to structure your script",
                "- How to manage requirements",
                "- How to handle input variables",
                "- How to set up a virtual environment"
            ]
    
    return "\n".join(response)

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
        config = build_notebook_config()
        submitted = st.button("Create MCP")
    else:  # Python Script
        config = build_python_script_config()
        submitted = st.button("Create MCP")
    
    # Add AI Assistant
    build_ai_assistant(mcp_type, config)
    
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
                            if "error" in result and result["error"]:
                                st.error(f"Error: {result['error']}")
                            else:
                                st.success("Execution completed!")
                                
                                # Display the main result
                                st.subheader("Results")
                                if isinstance(result.get('result'), dict):
                                    for key, value in result['result'].items():
                                        st.write(f"**{key}**: {value}")
                                else:
                                    st.write("Result:", result.get('result', 'No result'))
                                
                                # Display standard output/error in separate sections
                                if result.get('stdout'):
                                    st.subheader("Standard Output")
                                    st.code(result['stdout'])
                                if result.get('stderr'):
                                    st.subheader("Error Output")
                                    st.code(result['stderr'])
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