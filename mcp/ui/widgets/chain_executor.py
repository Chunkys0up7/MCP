import streamlit as st
import json
from typing import Dict, List, Any
import time
import requests
from concurrent.futures import ThreadPoolExecutor

class ChainExecutor:
    def __init__(self):
        self.server_url = "http://localhost:8000"  # Updated server URL
        
    def render(self):
        st.title("MCP Chain Executor")
        
        # Load available chains
        chains = self._load_chains()
        if not chains:
            st.warning("No chains available. Please create a chain first.")
            return
        
        # Chain selection
        selected_chain_id = st.selectbox(
            "Select Chain",
            options=list(chains.keys()),
            format_func=lambda x: chains[x]["name"]
        )
        
        if selected_chain_id:
            chain = chains[selected_chain_id]
            st.write(f"**Description:** {chain['description']}")
            
            # Display chain steps
            st.subheader("Chain Steps")
            for i, step in enumerate(chain["steps"], 1):
                st.write(f"{i}. {self._get_mcp_name(step['mcp_id'])}")
            
            # Input parameters
            st.subheader("Input Parameters")
            input_params = {}
            for step in chain["steps"]:
                mcp = self._get_mcp(step["mcp_id"])
                if mcp and "input_variables" in mcp["config"]:
                    for var in mcp["config"]["input_variables"]:
                        if var not in input_params:
                            input_params[var] = st.text_input(
                                f"Input for {var}",
                                key=f"input_{var}"
                            )
            
            # Execution controls
            st.subheader("Execution")
            if st.button("Execute Chain"):
                with st.spinner("Executing chain..."):
                    try:
                        results = self._execute_chain(chain, input_params)
                        self._display_results(results)
                    except Exception as e:
                        st.error(f"Error executing chain: {str(e)}")
    
    def _load_chains(self) -> Dict[str, Any]:
        """Load chain configurations from storage."""
        try:
            with open("chain_storage.json", "r") as f:
                data = json.load(f)
                return data.get("chains", {})
        except FileNotFoundError:
            return {}
    
    def _get_mcp(self, mcp_id: str) -> Dict[str, Any]:
        """Get MCP configuration by ID."""
        try:
            with open("mcp_storage.json", "r") as f:
                mcp_data = json.load(f)
            return mcp_data.get(mcp_id, {})
        except Exception:
            return {}
    
    def _get_mcp_name(self, mcp_id: str) -> str:
        """Get MCP name by ID."""
        mcp = self._get_mcp(mcp_id)
        return mcp.get("name", "Unknown MCP")
    
    def _execute_chain(
        self,
        chain: Dict[str, Any],
        input_params: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Execute the chain and return results."""
        results = []
        
        if chain["execution_mode"] == "Sequential":
            results = self._execute_sequential(chain, input_params)
        else:  # Parallel execution
            results = self._execute_parallel(chain, input_params)
        
        return results
    
    def _execute_sequential(
        self,
        chain: Dict[str, Any],
        input_params: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Execute chain steps sequentially."""
        results = []
        for step in chain["steps"]:
            result = self._execute_step(step, input_params)
            results.append(result)
            
            # Update input parameters with step output
            if result.get("output"):
                input_params.update(result["output"])
        
        return results
    
    def _execute_parallel(
        self,
        chain: Dict[str, Any],
        input_params: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Execute chain steps in parallel."""
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self._execute_step, step, input_params)
                for step in chain["steps"]
            ]
            return [future.result() for future in futures]
    
    def _execute_step(
        self,
        step: Dict[str, Any],
        input_params: Dict[str, str]
    ) -> Dict[str, Any]:
        """Execute a single chain step."""
        mcp_id = step["mcp_id"]
        inputs = step["inputs"]
        
        # Replace input references with actual values
        resolved_inputs = {}
        for key, value in inputs.items():
            if value in input_params:
                resolved_inputs[key] = input_params[value]
            else:
                resolved_inputs[key] = value
        
        # Execute MCP
        try:
            response = requests.post(
                f"{self.server_url}/context/{mcp_id}/execute",
                json=resolved_inputs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": str(e),
                "status": "error",
                "mcp_id": mcp_id
            }
    
    def _display_results(self, results: List[Dict[str, Any]]):
        """Display chain execution results."""
        st.subheader("Execution Results")
        
        for i, result in enumerate(results, 1):
            with st.expander(f"Step {i} Result", expanded=True):
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    st.success("Step completed successfully")
                    if "result" in result:
                        st.write("Output:")
                        try:
                            # Try to parse as JSON first
                            if isinstance(result["result"], str):
                                json_output = json.loads(result["result"])
                                st.json(json_output)
                            else:
                                st.json(result["result"])
                        except json.JSONDecodeError:
                            # If not valid JSON, display as text
                            st.text(result["result"])
                    if "stdout" in result and result["stdout"]:
                        st.write("Standard Output:")
                        st.code(result["stdout"])
                    if "stderr" in result and result["stderr"]:
                        st.write("Standard Error:")
                        st.code(result["stderr"]) 