import streamlit as st
import json
from typing import Dict, List, Any
import uuid

class ChainBuilder:
    def __init__(self):
        self.chain_id = str(uuid.uuid4())
        if 'selected_mcps' not in st.session_state:
            st.session_state.selected_mcps = []
        
    def render(self):
        st.title("MCP Chain Composer")
        
        # Step 1: Chain Metadata
        with st.expander("Chain Information", expanded=True):
            chain_name = st.text_input("Chain Name", key="chain_name")
            chain_description = st.text_area("Description", key="chain_description")
        
        # Step 2: MCP Selection and Arrangement
        with st.expander("MCP Workflow", expanded=True):
            # Load available MCPs
            available_mcps = self._load_mcp_catalog()
            
            # Create columns for drag-and-drop interface
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("Available MCPs")
                for mcp in available_mcps:
                    if mcp not in st.session_state.selected_mcps:
                        if st.button(f"➕ {mcp['name']}", key=f"add_{mcp['id']}"):
                            st.session_state.selected_mcps.append(mcp)
                            st.rerun()
            
            with col2:
                st.subheader("Workflow Design")
                if st.session_state.selected_mcps:
                    for i, mcp in enumerate(st.session_state.selected_mcps):
                        with st.container():
                            cols = st.columns([3, 1])
                            with cols[0]:
                                st.write(f"**{mcp['name']}**")
                                st.write(f"Type: {mcp['type']}")
                            with cols[1]:
                                if st.button("❌", key=f"remove_{i}"):
                                    st.session_state.selected_mcps.pop(i)
                                    st.rerun()
        
        # Step 3: Input Mapping
        if st.session_state.selected_mcps:
            st.subheader("Input Configuration")
            for mcp in st.session_state.selected_mcps:
                st.write(f"**Inputs for {mcp['name']}**")
                self._render_input_mapping(mcp)
                st.markdown("---")
        
        # Step 4: Chain Configuration
        with st.expander("Chain Configuration", expanded=True):
            error_handling = st.selectbox(
                "Error Handling Strategy",
                ["Retry with Backoff", "Fallback Chain", "Stop on Error"],
                key="error_handling"
            )
            
            if error_handling == "Retry with Backoff":
                max_retries = st.number_input("Max Retries", min_value=1, max_value=5, value=3)
                backoff_factor = st.number_input("Backoff Factor (seconds)", min_value=1, max_value=10, value=2)
            
            execution_mode = st.selectbox(
                "Execution Mode",
                ["Sequential", "Parallel"],
                key="execution_mode"
            )
        
        # Step 5: Save Chain
        if st.button("Save Chain"):
            chain_config = self._create_chain_config(
                chain_name,
                chain_description,
                st.session_state.selected_mcps,
                error_handling,
                execution_mode
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
            with open("mcp_storage.json", "r") as f:
                mcp_data = json.load(f)
            return [
                {
                    "id": mcp_id,
                    "name": data["name"],
                    "type": data["type"],
                    "description": data.get("description", ""),
                    "config": data["config"]
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
                st.text_input(
                    f"Map {input_var}",
                    key=f"input_{mcp['id']}_{input_var}",
                    help=f"Enter the value or reference for {input_var}"
                )
    
    def _create_chain_config(
        self,
        name: str,
        description: str,
        mcps: List[Dict[str, Any]],
        error_handling: str,
        execution_mode: str
    ) -> Dict[str, Any]:
        """Create chain configuration dictionary."""
        return {
            "chain_id": self.chain_id,
            "name": name,
            "description": description,
            "steps": [
                {
                    "mcp_id": mcp["id"],
                    "inputs": {
                        var: st.session_state.get(f"input_{mcp['id']}_{var}", "")
                        for var in mcp["config"].get("input_variables", [])
                    }
                }
                for mcp in mcps
            ],
            "error_handling": {
                "strategy": error_handling,
                "max_retries": st.session_state.get("max_retries", 3) if error_handling == "Retry with Backoff" else None,
                "backoff_factor": st.session_state.get("backoff_factor", 2) if error_handling == "Retry with Backoff" else None
            },
            "execution_mode": execution_mode
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
            # Load existing chains
            try:
                with open("chain_storage.json", "r") as f:
                    chains = json.load(f)
            except FileNotFoundError:
                chains = {}
            
            # Add new chain
            chains[chain_config["chain_id"]] = chain_config
            
            # Save updated chains
            with open("chain_storage.json", "w") as f:
                json.dump(chains, f, indent=2)
                
        except Exception as e:
            st.error(f"Error saving chain: {str(e)}")
            raise 