from typing import Dict, Any, List
import streamlit as st
import os
from mcp.core.types import PythonScriptConfig, MCPType
from mcp.core.config import config

def build_script_config() -> PythonScriptConfig:
    """Build Python Script configuration through UI."""
    st.subheader("Python Script Configuration")
    
    # Name
    name = st.text_input(
        "Configuration Name",
        help="Enter a name for this script configuration",
        key="script_config_name"
    )
    
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
                    script_path = os.path.join(config.scripts_dir, f"{script_name}.py")
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
    requirements_list = [r.strip() for r in requirements.split('\n') if r.strip()]
    
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
    
    return PythonScriptConfig(
        name=name,
        type=MCPType.PYTHON_SCRIPT,
        script_path=script_path if file_source == "Use Existing File" else os.path.join(config.scripts_dir, f"{script_name}.py"),
        requirements=requirements_list,
        input_variables=input_variables,
        virtual_env=virtual_env,
        timeout=timeout
    ) 