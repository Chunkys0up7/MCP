import json
import uuid
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st


class ChainBuilder:
    def __init__(self):
        # Initialize all session state variables with unified, robust defaults
        if "chain_id" not in st.session_state:
            st.session_state.chain_id = str(uuid.uuid4())
        if "selected_mcps" not in st.session_state:
            st.session_state.selected_mcps = []
        if "node_positions" not in st.session_state:
            st.session_state.node_positions = {}
        if "chain_name" not in st.session_state:
            st.session_state.chain_name = ""
        if "chain_description" not in st.session_state:
            st.session_state.chain_description = ""
        # Unified error handling options
        valid_error_handling = ["Stop on Error", "Retry with Backoff", "Fallback Chain"]
        if (
            "error_handling" not in st.session_state
            or st.session_state.error_handling not in valid_error_handling
        ):
            st.session_state.error_handling = "Stop on Error"
        # Unified execution mode options (lowercase)
        valid_execution_modes = ["sequential", "parallel"]
        if (
            "execution_mode" not in st.session_state
            or str(st.session_state.execution_mode).lower() not in valid_execution_modes
        ):
            st.session_state.execution_mode = "sequential"
        if "max_retries" not in st.session_state:
            st.session_state.max_retries = 3
        if "backoff_factor" not in st.session_state:
            st.session_state.backoff_factor = 2

    def render(self):
        """Render the chain builder interface."""
        st.subheader("Chain Builder")

        # Chain configuration
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.chain_name = st.text_input(
                "Chain Name",
                value=st.session_state.chain_name,
                help="Enter a name for your chain",
            )

        with col2:
            st.session_state.execution_mode = st.selectbox(
                "Execution Mode",
                options=["sequential", "parallel"],
                index=["sequential", "parallel"].index(
                    str(st.session_state.execution_mode).lower()
                ),
                help="Choose how to execute the chain",
            )

        st.session_state.chain_description = st.text_area(
            "Description",
            value=st.session_state.chain_description,
            help="Describe what this chain does",
        )

        # Error handling configuration
        st.subheader("Error Handling")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.session_state.error_handling = st.selectbox(
                "Error Handling Strategy",
                options=["Stop on Error", "Retry with Backoff", "Fallback Chain"],
                index=["Stop on Error", "Retry with Backoff", "Fallback Chain"].index(
                    st.session_state.error_handling
                ),
                help="Choose how to handle errors in the chain",
            )

        with col2:
            st.session_state.max_retries = st.number_input(
                "Max Retries",
                min_value=0,
                max_value=10,
                value=st.session_state.max_retries,
                help="Maximum number of retry attempts",
            )

        with col3:
            st.session_state.backoff_factor = st.number_input(
                "Backoff Factor",
                min_value=1.0,
                max_value=5.0,
                value=st.session_state.backoff_factor,
                step=0.1,
                help="Multiplier for retry delay",
            )

        # Step 2: MCP Workflow
        with st.expander("MCP Workflow", expanded=True):
            # Load available MCPs
            available_mcps = self._load_mcp_catalog()

            # Warn if referenced files are missing
            for mcp in available_mcps:
                if mcp["type"] == "python_script":
                    script_path = mcp["config"].get("script_path")
                    if script_path and not Path(script_path).exists():
                        st.warning(
                            f"Script not found: {script_path} (referenced by {mcp['name']})"
                        )
                if mcp["type"] == "jupyter_notebook":
                    notebook_path = mcp["config"].get("notebook_path")
                    if notebook_path and not Path(notebook_path).exists():
                        st.warning(
                            f"Notebook not found: {notebook_path} (referenced by {mcp['name']})"
                        )

            # Create a visual workflow interface
            col1, col2 = st.columns([1, 2])

            with col1:
                st.subheader("Available MCPs")
                for mcp in available_mcps:
                    if mcp not in st.session_state.selected_mcps:
                        with st.container():
                            st.markdown(
                                f"""
                            <div style="
                                padding: 10px;
                                border: 1px solid #ddd;
                                border-radius: 5px;
                                margin-bottom: 10px;
                                background-color: #f8f9fa;
                                cursor: pointer;
                            ">
                                <h4 style="margin: 0;">{mcp['name']}</h4>
                                <p style="margin: 5px 0; color: #666;">{mcp['type']}</p>
                                <p style="margin: 0; font-size: 0.9em;">{mcp.get('description', '')}</p>
                            </div>
                            """,
                                unsafe_allow_html=True,
                            )
                            if st.button("Add to Chain", key=f"add_{mcp['id']}"):
                                st.session_state.selected_mcps.append(mcp)
                                st.rerun()

            with col2:
                st.subheader("Workflow Design")
                if st.session_state.selected_mcps:
                    for i, mcp in enumerate(st.session_state.selected_mcps):
                        with st.container():
                            st.markdown(
                                f"""
                            <div style="
                                padding: 15px;
                                border: 2px solid #2196f3;
                                border-radius: 8px;
                                margin-bottom: 15px;
                                background-color: #e3f2fd;
                                position: relative;
                            ">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div>
                                        <h3 style="margin: 0;">{mcp['name']}</h3>
                                        <p style="margin: 5px 0; color: #666;">{mcp['type']}</p>
                                    </div>
                                    <div>
                                        {'⬆️' if i > 0 else ''}
                                        {'⬇️' if i < len(st.session_state.selected_mcps) - 1 else ''}
                                        <button onclick="removeNode({i})" style="
                                            background: none;
                                            border: none;
                                            color: #f44336;
                                            cursor: pointer;
                                            font-size: 1.2em;
                                        ">❌</button>
                                    </div>
                                </div>
                                <div style="
                                    position: absolute;
                                    bottom: -10px;
                                    left: 50%;
                                    transform: translateX(-50%);
                                    width: 2px;
                                    height: 20px;
                                    background-color: #2196f3;
                                "></div>
                            </div>
                            """,
                                unsafe_allow_html=True,
                            )

        # Step 3: Input Configuration
        if st.session_state.selected_mcps:
            st.subheader("Input Configuration")
            for mcp in st.session_state.selected_mcps:
                with st.expander(f"Inputs for {mcp['name']}", expanded=True):
                    self._render_input_mapping(mcp)

        # Step 4: Chain Configuration
        with st.expander("Chain Configuration", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.error_handling = st.selectbox(
                    "Error Handling Strategy",
                    ["Retry with Backoff", "Fallback Chain", "Stop on Error"],
                    index=[
                        "Retry with Backoff",
                        "Fallback Chain",
                        "Stop on Error",
                    ].index(st.session_state.error_handling),
                )

                if st.session_state.error_handling == "Retry with Backoff":
                    st.session_state.max_retries = st.number_input(
                        "Max Retries",
                        min_value=1,
                        max_value=5,
                        value=st.session_state.max_retries,
                    )
                    st.session_state.backoff_factor = st.number_input(
                        "Backoff Factor (seconds)",
                        min_value=1,
                        max_value=10,
                        value=st.session_state.backoff_factor,
                    )

            with col2:
                st.session_state.execution_mode = st.selectbox(
                    "Execution Mode",
                    ["sequential", "parallel"],
                    index=["sequential", "parallel"].index(
                        str(st.session_state.execution_mode).lower()
                    ),
                )

        # Step 5: Save Chain
        if st.button("Save Chain", type="primary"):
            chain_config = self._create_chain_config(
                st.session_state.chain_name,
                st.session_state.chain_description,
                st.session_state.selected_mcps,
                st.session_state.error_handling,
                st.session_state.execution_mode,
            )

            if self._validate_chain(chain_config):
                self._save_chain(chain_config)
                st.success("Chain saved successfully!")
                # Clear selected MCPs after successful save
                st.session_state.selected_mcps = []
                st.rerun()
            else:
                st.error("Chain validation failed. Please check the configuration.")

    def _load_mcp_catalog(self) -> List[Dict[str, Any]]:
        """Load available MCPs from storage."""
        try:
            # Get the project root directory
            project_root = Path(__file__).parent.parent.parent.parent
            storage_path = project_root / "mcp_storage.json"

            if not storage_path.exists():
                st.warning("No MCPs found. Create some MCPs first!")
                return []

            with open(storage_path, "r") as f:
                mcp_data = json.load(f)
            return [
                {
                    "id": mcp_id,
                    "name": data["name"],
                    "type": data["type"],
                    "description": data.get("description", ""),
                    "config": data["config"],
                }
                for mcp_id, data in mcp_data.items()
            ]
        except Exception as e:
            st.error(f"Error loading MCP catalog: {str(e)}")
            return []

    def _render_input_mapping(self, mcp: Dict[str, Any]):
        """Render input mapping interface for an MCP."""
        if "input_variables" in mcp["config"]:
            for input_var in mcp["config"]["input_variables"]:
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown(f"**{input_var}**")
                with col2:
                    st.text_input(
                        f"Map {input_var}",
                        key=f"input_{mcp['id']}_{input_var}",
                        help=f"Enter the value or reference for {input_var}",
                        label_visibility="collapsed",
                    )

    def _create_chain_config(
        self,
        name: str,
        description: str,
        mcps: List[Dict[str, Any]],
        error_handling: str,
        execution_mode: str,
    ) -> Dict[str, Any]:
        """Create chain configuration dictionary."""
        return {
            "chain_id": st.session_state.chain_id,
            "name": name,
            "description": description,
            "steps": [
                {
                    "mcp_id": mcp["id"],
                    "inputs": {
                        var: st.session_state.get(f"input_{mcp['id']}_{var}", "")
                        for var in mcp["config"].get("input_variables", [])
                    },
                }
                for mcp in mcps
            ],
            "error_handling": {
                "strategy": error_handling,
                "max_retries": (
                    st.session_state.max_retries
                    if error_handling == "Retry with Backoff"
                    else None
                ),
                "backoff_factor": (
                    st.session_state.backoff_factor
                    if error_handling == "Retry with Backoff"
                    else None
                ),
            },
            "execution_mode": execution_mode,
        }

    def _validate_chain(self, chain_config: Dict[str, Any]) -> bool:
        """Validate chain configuration."""
        if not chain_config["name"]:
            st.error("Chain name is required")
            return False

        if not chain_config["steps"]:
            st.error("At least one MCP must be added to the chain")
            return False

        return True

    def _save_chain(self, chain_config: Dict[str, Any]):
        """Save chain configuration to storage."""
        try:
            # Get the project root directory
            project_root = Path(__file__).parent.parent.parent.parent
            storage_path = project_root / "chain_storage.json"

            # Load existing chains
            try:
                with open(storage_path, "r") as f:
                    chains = json.load(f)
            except FileNotFoundError:
                chains = {}

            # Add new chain
            chains[chain_config["chain_id"]] = chain_config

            # Save updated chains
            with open(storage_path, "w") as f:
                json.dump(chains, f, indent=2)

        except Exception as e:
            st.error(f"Error saving chain: {str(e)}")
            raise
