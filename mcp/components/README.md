# MCP Components

This directory contains the core components of the MCP (Mission Control Platform) system.

## Components

### Dependency Visualizer

The Dependency Visualizer (`dependency_visualizer.py`) provides tools for analyzing and visualizing component dependencies in the MCP system.

#### Features
- Component relationship graph generation
- Dependency conflict detection
  - Circular dependencies
  - Version conflicts
  - Deprecated components
- Version compatibility checking
- Visual dependency mapping
- Graph import/export functionality

#### Usage

```python
from mcp.components.dependency_visualizer import DependencyVisualizer
from datetime import datetime

# Create visualizer
visualizer = DependencyVisualizer()

# Add components
visualizer.add_component(
    name="core",
    version="1.0.0",
    dependencies={},
    release_date=datetime.now()
)

# Detect conflicts
conflicts = visualizer.detect_conflicts()

# Generate visualization
visualizer.generate_visualization(output_path="dependency_graph.png")

# Export graph
visualizer.export_graph("dependency_graph.json")
```

#### Testing

Run the test script to verify functionality:
```bash
python scripts/test_dependency_visualizer.py
```

This will:
1. Create a sample component dependency graph
2. Detect dependency conflicts
3. Generate visualizations
4. Test import/export functionality

## Directory Structure

```
mcp/components/
├── README.md
├── dependency_visualizer.py
└── __init__.py
```

## Dependencies

- networkx: For graph operations
- matplotlib: For visualization
- graphviz: For graph layout 