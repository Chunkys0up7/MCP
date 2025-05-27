"""
Dependency Visualizer Test Script

This script tests the dependency visualization functionality by:
1. Creating a sample component dependency graph
2. Detecting dependency conflicts
3. Generating visualizations
4. Testing import/export functionality
"""

import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from mcp.components.dependency_visualizer import DependencyVisualizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_graph() -> DependencyVisualizer:
    """
    Create a sample component dependency graph.

    Returns:
        DependencyVisualizer: Visualizer with sample graph
    """
    visualizer = DependencyVisualizer()

    # Add components with their dependencies
    now = datetime.now()

    # Core components
    visualizer.add_component(
        name="core",
        version="1.0.0",
        dependencies={},
        release_date=now - timedelta(days=30),
    )

    visualizer.add_component(
        name="core",
        version="1.1.0",
        dependencies={},
        release_date=now - timedelta(days=15),
    )

    # Database components
    visualizer.add_component(
        name="database",
        version="1.0.0",
        dependencies={"core": "1.0.0"},
        release_date=now - timedelta(days=25),
    )

    visualizer.add_component(
        name="database",
        version="1.1.0",
        dependencies={"core": "1.1.0"},
        release_date=now - timedelta(days=10),
    )

    # API components
    visualizer.add_component(
        name="api",
        version="1.0.0",
        dependencies={"core": "1.0.0", "database": "1.0.0"},
        release_date=now - timedelta(days=20),
    )

    visualizer.add_component(
        name="api",
        version="1.1.0",
        dependencies={"core": "1.1.0", "database": "1.1.0"},
        release_date=now - timedelta(days=5),
    )

    # UI components
    visualizer.add_component(
        name="ui",
        version="1.0.0",
        dependencies={"api": "1.0.0"},
        release_date=now - timedelta(days=15),
    )

    visualizer.add_component(
        name="ui",
        version="1.1.0",
        dependencies={"api": "1.1.0"},
        release_date=now - timedelta(days=2),
    )

    # Add some deprecated components
    visualizer.add_component(
        name="legacy",
        version="0.9.0",
        dependencies={"core": "1.0.0"},
        release_date=now - timedelta(days=60),
        is_deprecated=True,
    )

    # Add a component with version conflict
    visualizer.add_component(
        name="plugin",
        version="1.0.0",
        dependencies={
            "core": "1.0.0",
            "api": "1.1.0",  # This will cause a version conflict
        },
        release_date=now - timedelta(days=1),
    )

    return visualizer


def test_visualizer() -> None:
    """Test the dependency visualizer."""
    try:
        # Create sample graph
        visualizer = create_sample_graph()
        logger.info("Created sample dependency graph")

        # Detect conflicts
        conflicts = visualizer.detect_conflicts()
        logger.info(f"\nDetected {len(conflicts)} conflicts:")
        for conflict in conflicts:
            logger.info(f"  [{conflict.severity}] {conflict.description}")

        # Generate visualization
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        visualizer.generate_visualization(
            output_path=str(output_dir / "dependency_graph.png")
        )
        logger.info("\nGenerated dependency graph visualization")

        # Test export/import
        graph_path = str(output_dir / "dependency_graph.json")
        visualizer.export_graph(graph_path)
        logger.info("Exported dependency graph to JSON")

        # Create new visualizer and import graph
        new_visualizer = DependencyVisualizer()
        new_visualizer.import_graph(graph_path)
        logger.info("Imported dependency graph from JSON")

        # Verify imported graph
        imported_conflicts = new_visualizer.detect_conflicts()
        assert len(imported_conflicts) == len(
            conflicts
        ), "Import/export verification failed"
        logger.info("Verified imported graph matches original")

    except Exception as e:
        logger.error(f"Error in visualizer test: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    test_visualizer()
