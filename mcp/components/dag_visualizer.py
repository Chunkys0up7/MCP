"""
DAG Visualization Component

This module provides functionality to visualize workflow DAGs using networkx and matplotlib.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import networkx as nx

from mcp.core.dag_engine import DAGWorkflowEngine, StepStatus
from mcp.core.workflow_engine import WorkflowStep
from mcp.db.models import WorkflowDefinition


class DAGVisualizer:
    """Component for visualizing workflow DAGs."""

    def __init__(self):
        self.colors = {
            StepStatus.PENDING: "lightgray",
            StepStatus.RUNNING: "yellow",
            StepStatus.COMPLETED: "green",
            StepStatus.FAILED: "red",
            StepStatus.SKIPPED: "blue",
        }

    def create_graph(self, engine: DAGWorkflowEngine) -> nx.DiGraph:
        """
        Create a networkx graph from the DAG engine.

        Args:
            engine: The DAG workflow engine

        Returns:
            nx.DiGraph: The graph representation of the DAG
        """
        G = nx.DiGraph()

        # Add nodes
        for step_id, dag_step in engine.steps.items():
            G.add_node(
                step_id,
                name=dag_step.step.name,
                status=dag_step.status,
                start_time=dag_step.start_time,
                end_time=dag_step.end_time,
            )

        # Add edges
        for step_id, dag_step in engine.steps.items():
            for dep_id in dag_step.dependencies:
                G.add_edge(dep_id, step_id)

        return G

    def visualize(
        self, engine: DAGWorkflowEngine, output_path: Optional[str] = None, show: bool = True
    ) -> None:
        """
        Visualize the DAG using matplotlib.

        Args:
            engine: The DAG workflow engine
            output_path: Optional path to save the visualization
            show: Whether to display the visualization
        """
        G = self.create_graph(engine)

        # Create figure
        plt.figure(figsize=(12, 8))

        # Calculate node positions using hierarchical layout
        pos = nx.spring_layout(G, k=1, iterations=50)

        # Draw nodes
        node_colors = [self.colors[G.nodes[node]["status"]] for node in G.nodes()]
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=2000, alpha=0.8)

        # Draw edges
        nx.draw_networkx_edges(G, pos, edge_color="gray", arrows=True, arrowsize=20)

        # Add labels
        labels = {node: f"{node}\n{G.nodes[node]['name']}" for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_weight="bold")

        # Add status legend
        legend_elements = [
            plt.Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor=color,
                markersize=15,
                label=status.value,
            )
            for status, color in self.colors.items()
        ]
        plt.legend(handles=legend_elements, loc="upper right", bbox_to_anchor=(1.15, 1))

        plt.title("Workflow DAG Visualization")
        plt.axis("off")

        if output_path:
            plt.savefig(output_path, bbox_inches="tight", dpi=300)

        if show:
            plt.show()
        else:
            plt.close()

    def get_execution_times(
        self, engine: DAGWorkflowEngine
    ) -> Dict[str, Tuple[datetime, datetime]]:
        """
        Get execution times for each step.

        Args:
            engine: The DAG workflow engine

        Returns:
            Dict[str, Tuple[datetime, datetime]]: Mapping of step IDs to (start_time, end_time)
        """
        return {
            step_id: (dag_step.start_time, dag_step.end_time)
            for step_id, dag_step in engine.steps.items()
            if dag_step.start_time and dag_step.end_time
        }

    def get_critical_path(self, engine: DAGWorkflowEngine) -> List[str]:
        """
        Calculate the critical path of the workflow.

        Args:
            engine: The DAG workflow engine

        Returns:
            List[str]: List of step IDs in the critical path
        """
        G = self.create_graph(engine)

        # Calculate earliest start times
        earliest_start = {}
        for node in nx.topological_sort(G):
            if not list(G.predecessors(node)):
                earliest_start[node] = 0
            else:
                earliest_start[node] = max(
                    earliest_start[pred] + 1 for pred in G.predecessors(node)
                )

        # Calculate latest start times
        latest_start = {}
        for node in reversed(list(nx.topological_sort(G))):
            if not list(G.successors(node)):
                latest_start[node] = earliest_start[node]
            else:
                latest_start[node] = min(latest_start[succ] - 1 for succ in G.successors(node))

        # Find critical path
        critical_path = []
        for node in nx.topological_sort(G):
            if earliest_start[node] == latest_start[node]:
                critical_path.append(node)

        return critical_path

    def get_parallel_steps(self, engine: DAGWorkflowEngine) -> List[List[str]]:
        """
        Get groups of steps that can be executed in parallel.

        Args:
            engine: The DAG workflow engine

        Returns:
            List[List[str]]: List of step groups that can be executed in parallel
        """
        G = self.create_graph(engine)
        levels = {}

        # Assign levels to nodes
        for node in nx.topological_sort(G):
            if not list(G.predecessors(node)):
                levels[node] = 0
            else:
                levels[node] = max(levels[pred] + 1 for pred in G.predecessors(node))

        # Group nodes by level
        parallel_groups = []
        if not levels:
            return parallel_groups
        max_level = max(levels.values())
        for level in range(max_level + 1):
            group = [node for node, lvl in levels.items() if lvl == level]
            if group:
                parallel_groups.append(group)
        return parallel_groups
