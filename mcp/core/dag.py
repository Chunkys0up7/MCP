"""
DAG (Directed Acyclic Graph) Module

This module provides functionality for working with workflow DAGs, including:
1. Cycle detection
2. Cost estimation
3. Parallel execution optimization
4. Topological sorting
"""

from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, deque
import networkx as nx
from mcp.schemas.workflow import Workflow, WorkflowStep

class DAGOptimizer:
    """
    Optimizes workflow DAGs for execution by:
    1. Detecting cycles
    2. Estimating execution costs
    3. Optimizing parallel execution
    4. Validating dependencies
    """

    def __init__(self):
        self.graph = nx.DiGraph()

    def build_graph(self, workflow: Workflow) -> None:
        """
        Builds a directed graph from the workflow steps.
        
        Args:
            workflow (Workflow): The workflow to build the graph from.
        """
        self.graph.clear()
        
        # Add nodes
        for step in workflow.steps:
            self.graph.add_node(step.step_id, step=step)
        
        # Add edges based on dependencies
        for step in workflow.steps:
            for input_config in step.inputs.values():
                if input_config.source_type == "STEP_OUTPUT" and input_config.source_step_id:
                    self.graph.add_edge(input_config.source_step_id, step.step_id)

    def detect_cycles(self) -> List[List[str]]:
        """
        Detects cycles in the workflow DAG.
        
        Returns:
            List[List[str]]: List of cycles found, where each cycle is a list of step IDs.
        """
        try:
            cycles = list(nx.simple_cycles(self.graph))
            return cycles
        except nx.NetworkXNoCycle:
            return []

    def estimate_execution_cost(self, step_costs: Dict[str, float]) -> Dict[str, float]:
        """
        Estimates the execution cost for each step in the workflow.
        
        Args:
            step_costs (Dict[str, float]): Dictionary mapping step IDs to their individual costs.
            
        Returns:
            Dict[str, float]: Dictionary mapping step IDs to their total costs (including dependencies).
        """
        total_costs = {}
        
        # Calculate total cost for each node
        for node in nx.topological_sort(self.graph):
            # Base cost of the node
            node_cost = step_costs.get(node, 0.0)
            
            # Add costs of all dependencies
            for pred in self.graph.predecessors(node):
                node_cost += total_costs.get(pred, 0.0)
            
            total_costs[node] = node_cost
        
        return total_costs

    def optimize_parallel_execution(self) -> List[List[str]]:
        """
        Optimizes the workflow for parallel execution by grouping steps that can run in parallel.
        
        Returns:
            List[List[str]]: List of execution groups, where each group contains step IDs that can run in parallel.
        """
        # Get topological levels
        levels = defaultdict(list)
        in_degree = {node: 0 for node in self.graph.nodes()}
        
        # Calculate in-degree for each node
        for u, v in self.graph.edges():
            in_degree[v] += 1
        
        # Find nodes with no incoming edges (level 0)
        queue = deque([node for node, degree in in_degree.items() if degree == 0])
        level = 0
        
        while queue:
            level_size = len(queue)
            for _ in range(level_size):
                node = queue.popleft()
                levels[level].append(node)
                
                # Update in-degree for neighbors
                for neighbor in self.graph.successors(node):
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
            
            level += 1
        
        return [levels[l] for l in range(level)]

    def validate_dependencies(self) -> List[str]:
        """
        Validates that all dependencies in the workflow are valid.
        
        Returns:
            List[str]: List of error messages for invalid dependencies.
        """
        errors = []
        step_ids = {step.step_id for step in self.graph.nodes()}
        
        for step in self.graph.nodes():
            for input_config in self.graph.nodes[step]['step'].inputs.values():
                if input_config.source_type == "STEP_OUTPUT":
                    if input_config.source_step_id not in step_ids:
                        errors.append(
                            f"Step {step} depends on non-existent step {input_config.source_step_id}"
                        )
        
        return errors

    def get_execution_order(self) -> List[str]:
        """
        Gets the optimal execution order for the workflow.
        
        Returns:
            List[str]: List of step IDs in optimal execution order.
        """
        return list(nx.topological_sort(self.graph))

    def get_step_dependencies(self, step_id: str) -> Tuple[Set[str], Set[str]]:
        """
        Gets the dependencies and dependents of a step.
        
        Args:
            step_id (str): The ID of the step to analyze.
            
        Returns:
            Tuple[Set[str], Set[str]]: Tuple containing (dependencies, dependents) sets.
        """
        if step_id not in self.graph:
            return set(), set()
        
        dependencies = set(self.graph.predecessors(step_id))
        dependents = set(self.graph.successors(step_id))
        
        return dependencies, dependents 