"""
Dependency Visualizer

This module provides functionality for:
1. Component relationship visualization
2. Dependency conflict detection
3. Version compatibility checking
4. Visual dependency mapping
"""

from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt
import logging
from datetime import datetime
import json
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ComponentVersion:
    """Component version information."""
    version: str
    dependencies: Dict[str, str]  # component_name -> version_constraint
    release_date: datetime
    is_deprecated: bool = False

@dataclass
class DependencyConflict:
    """Information about a dependency conflict."""
    component: str
    required_versions: List[str]
    conflict_type: str  # 'version_mismatch', 'circular', 'deprecated'
    severity: str  # 'error', 'warning'
    description: str

class DependencyVisualizer:
    """
    Component dependency visualization and analysis system.
    
    This class provides:
    1. Component relationship graph generation
    2. Dependency conflict detection
    3. Version compatibility checking
    4. Visual dependency mapping
    """
    
    def __init__(self):
        """Initialize the dependency visualizer."""
        self.graph = nx.DiGraph()
        self.components: Dict[str, Dict[str, ComponentVersion]] = {}
        self.conflicts: List[DependencyConflict] = []
    
    def add_component(
        self,
        name: str,
        version: str,
        dependencies: Dict[str, str],
        release_date: datetime,
        is_deprecated: bool = False
    ) -> None:
        """
        Add a component to the dependency graph.
        
        Args:
            name: Component name
            version: Component version
            dependencies: Component dependencies
            release_date: Release date
            is_deprecated: Whether the component is deprecated
        """
        if name not in self.components:
            self.components[name] = {}
        
        self.components[name][version] = ComponentVersion(
            version=version,
            dependencies=dependencies,
            release_date=release_date,
            is_deprecated=is_deprecated
        )
        
        # Add node to graph
        node_id = f"{name}@{version}"
        self.graph.add_node(
            node_id,
            name=name,
            version=version,
            release_date=release_date,
            is_deprecated=is_deprecated
        )
        
        # Add edges for dependencies
        for dep_name, dep_version in dependencies.items():
            dep_node_id = f"{dep_name}@{dep_version}"
            self.graph.add_edge(node_id, dep_node_id)
    
    def detect_conflicts(self) -> List[DependencyConflict]:
        """
        Detect dependency conflicts in the graph.
        
        Returns:
            List[DependencyConflict]: List of detected conflicts
        """
        self.conflicts = []
        
        # Check for circular dependencies
        self._detect_circular_dependencies()
        
        # Check for version conflicts
        self._detect_version_conflicts()
        
        # Check for deprecated dependencies
        self._detect_deprecated_dependencies()
        
        return self.conflicts
    
    def _detect_circular_dependencies(self) -> None:
        """Detect circular dependencies in the graph."""
        try:
            cycles = list(nx.simple_cycles(self.graph))
            for cycle in cycles:
                self.conflicts.append(
                    DependencyConflict(
                        component=cycle[0].split('@')[0],
                        required_versions=[node.split('@')[1] for node in cycle],
                        conflict_type='circular',
                        severity='error',
                        description=f"Circular dependency detected: {' -> '.join(cycle)}"
                    )
                )
        except nx.NetworkXNoCycle:
            pass
    
    def _detect_version_conflicts(self) -> None:
        """Detect version conflicts in dependencies."""
        for node in self.graph.nodes():
            component_name, version = node.split('@')
            
            # Get all dependencies of this component
            dependencies = self.graph.successors(node)
            
            # Check each dependency for version conflicts
            for dep in dependencies:
                dep_name, dep_version = dep.split('@')
                
                # Check if the dependency version satisfies the requirement
                if not self._check_version_compatibility(
                    dep_name,
                    dep_version,
                    self.components[component_name][version].dependencies.get(dep_name, '')
                ):
                    self.conflicts.append(
                        DependencyConflict(
                            component=component_name,
                            required_versions=[dep_version],
                            conflict_type='version_mismatch',
                            severity='error',
                            description=f"Version conflict: {component_name} requires {dep_name} {self.components[component_name][version].dependencies[dep_name]}, but found {dep_version}"
                        )
                    )
    
    def _detect_deprecated_dependencies(self) -> None:
        """Detect deprecated dependencies."""
        for node in self.graph.nodes():
            component_name, version = node.split('@')
            
            # Check if this component is deprecated
            if self.components[component_name][version].is_deprecated:
                self.conflicts.append(
                    DependencyConflict(
                        component=component_name,
                        required_versions=[version],
                        conflict_type='deprecated',
                        severity='warning',
                        description=f"Deprecated component: {component_name}@{version}"
                    )
                )
    
    def _check_version_compatibility(
        self,
        component_name: str,
        version: str,
        constraint: str
    ) -> bool:
        """
        Check if a version satisfies a version constraint.
        
        Args:
            component_name: Component name
            version: Version to check
            constraint: Version constraint
        
        Returns:
            bool: True if version satisfies constraint
        """
        if not constraint:
            return True
        
        # TODO: Implement proper version constraint checking
        # For now, just check exact version match
        return version == constraint
    
    def generate_visualization(
        self,
        output_path: Optional[str] = None,
        show_labels: bool = True,
        layout: str = 'dot'
    ) -> None:
        """
        Generate a visual representation of the dependency graph.
        
        Args:
            output_path: Path to save the visualization
            show_labels: Whether to show node labels
            layout: Graph layout algorithm
        """
        plt.figure(figsize=(12, 8))
        
        # Generate layout
        pos = graphviz_layout(self.graph, prog=layout)
        
        # Draw nodes
        nx.draw_networkx_nodes(
            self.graph,
            pos,
            node_color='lightblue',
            node_size=2000,
            alpha=0.6
        )
        
        # Draw edges
        nx.draw_networkx_edges(
            self.graph,
            pos,
            edge_color='gray',
            arrows=True,
            arrowsize=20
        )
        
        # Draw labels
        if show_labels:
            labels = {
                node: f"{self.graph.nodes[node]['name']}\n{self.graph.nodes[node]['version']}"
                for node in self.graph.nodes()
            }
            nx.draw_networkx_labels(
                self.graph,
                pos,
                labels,
                font_size=8
            )
        
        plt.title("Component Dependency Graph")
        plt.axis('off')
        
        if output_path:
            plt.savefig(output_path, format='png', dpi=300, bbox_inches='tight')
        else:
            plt.show()
    
    def export_graph(self, output_path: str) -> None:
        """
        Export the dependency graph to a file.
        
        Args:
            output_path: Path to save the graph
        """
        graph_data = {
            'nodes': [
                {
                    'id': node,
                    'name': self.graph.nodes[node]['name'],
                    'version': self.graph.nodes[node]['version'],
                    'release_date': self.graph.nodes[node]['release_date'].isoformat(),
                    'is_deprecated': self.graph.nodes[node]['is_deprecated']
                }
                for node in self.graph.nodes()
            ],
            'edges': [
                {
                    'source': source,
                    'target': target
                }
                for source, target in self.graph.edges()
            ],
            'conflicts': [
                {
                    'component': conflict.component,
                    'required_versions': conflict.required_versions,
                    'conflict_type': conflict.conflict_type,
                    'severity': conflict.severity,
                    'description': conflict.description
                }
                for conflict in self.conflicts
            ]
        }
        
        with open(output_path, 'w') as f:
            json.dump(graph_data, f, indent=2)
    
    def import_graph(self, input_path: str) -> None:
        """
        Import a dependency graph from a file.
        
        Args:
            input_path: Path to the graph file
        """
        with open(input_path, 'r') as f:
            graph_data = json.load(f)
        
        # Clear existing graph
        self.graph.clear()
        self.components.clear()
        self.conflicts.clear()
        
        # Add nodes
        for node in graph_data['nodes']:
            component_name, version = node['id'].split('@')
            self.add_component(
                name=component_name,
                version=version,
                dependencies={},  # Dependencies will be added with edges
                release_date=datetime.fromisoformat(node['release_date']),
                is_deprecated=node['is_deprecated']
            )
        
        # Add edges
        for edge in graph_data['edges']:
            self.graph.add_edge(edge['source'], edge['target'])
        
        # Add conflicts
        for conflict in graph_data['conflicts']:
            self.conflicts.append(
                DependencyConflict(
                    component=conflict['component'],
                    required_versions=conflict['required_versions'],
                    conflict_type=conflict['conflict_type'],
                    severity=conflict['severity'],
                    description=conflict['description']
                )
            ) 