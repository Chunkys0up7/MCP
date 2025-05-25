import json
import os

import streamlit as st

from mcp.core.config import config
from mcp.core.types import JupyterNotebookConfig, MCPType


def build_notebook_config() -> JupyterNotebookConfig:
    """Build Jupyter Notebook configuration through UI."""
    st.subheader("Notebook Configuration")

    # Name
    name = st.text_input(
        "Configuration Name",
        help="Enter a name for this notebook configuration",
        key="notebook_config_name",
    )

    # Initialize notebook_path
    notebook_path = None

    # File source selection
    file_source = st.radio(
        "Notebook Source", ["Use Existing File", "Create New Notebook"], key="notebook_source"
    )

    if file_source == "Use Existing File":
        notebook_path = st.text_input(
            "Notebook Path", help="Path to the Jupyter notebook file", key="notebook_path"
        )
    else:
        # Create new notebook
        notebook_name = st.text_input(
            "Notebook Name",
            help="Name for the new notebook (without .ipynb extension)",
            key="new_notebook_name",
        )

        # Notebook editor with cells
        st.subheader("Notebook Editor")

        # Initialize cells in session state if not present
        if "notebook_cells" not in st.session_state:
            st.session_state.notebook_cells = [
                {"type": "markdown", "content": "# New Notebook\n\nAdd your cells below."},
                {"type": "code", "content": "# Your first code cell"},
            ]

        # Add new cell buttons
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
                key=f"cell_type_{i}",
            )

            # Cell content editor
            cell_content = st.text_area(
                "Cell Content", value=cell["content"], height=150, key=f"cell_content_{i}"
            )

            # Update cell in session state
            st.session_state.notebook_cells[i] = {"type": cell_type, "content": cell_content}

            # Delete cell button
            if st.button("Delete Cell", key=f"delete_cell_{i}"):
                st.session_state.notebook_cells.pop(i)
                st.rerun()

            st.markdown("---")

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
                                "outputs": [],
                            }
                            for cell in st.session_state.notebook_cells
                        ],
                        "metadata": {
                            "kernelspec": {
                                "display_name": "Python 3",
                                "language": "python",
                                "name": "python3",
                            }
                        },
                        "nbformat": 4,
                        "nbformat_minor": 4,
                    }

                    notebook_path = os.path.join(config.notebooks_dir, f"{notebook_name}.ipynb")
                    os.makedirs(os.path.dirname(notebook_path), exist_ok=True)
                    with open(notebook_path, "w") as f:
                        json.dump(notebook_content, f, indent=2)
                    st.success(f"Notebook saved to {notebook_path}")
                except Exception as e:
                    st.error(f"Error saving notebook: {str(e)}")
            else:
                st.error("Please provide a notebook name")

    # Execution settings
    execute_all = st.checkbox("Execute All Cells", value=True, key="execute_all")
    if not execute_all:
        cells_to_execute = st.text_input(
            "Cells to Execute",
            help="Comma-separated list of cell numbers (e.g., 1,2,3)",
            key="cells_to_execute",
        )
        cells_to_execute = [int(c.strip()) for c in cells_to_execute.split(",") if c.strip()]
    else:
        cells_to_execute = None

    # Input variables configuration
    st.subheader("Input Variables")
    input_vars = st.text_area(
        "Input Variables (one per line)",
        help="Enter input variable names that will be available in the notebook",
        key="notebook_input_variables",
    )
    input_variables = [var.strip() for var in input_vars.split("\n") if var.strip()]

    # Timeout setting
    timeout = st.number_input(
        "Timeout (seconds)",
        min_value=60,
        value=600,
        help="Maximum execution time for the notebook",
        key="notebook_timeout",
    )

    # Ensure notebook_path is set for new notebooks
    if file_source == "Create New Notebook" and notebook_name:
        notebook_path = os.path.join(config.notebooks_dir, f"{notebook_name}.ipynb")

    return JupyterNotebookConfig(
        name=name,
        type=MCPType.JUPYTER_NOTEBOOK,
        notebook_path=notebook_path,
        execute_all=execute_all,
        cells_to_execute=cells_to_execute,
        input_variables=input_variables,
        timeout=timeout,
    )
