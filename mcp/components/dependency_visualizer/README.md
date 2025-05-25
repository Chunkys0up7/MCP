# Dependency Visualizer

## Overview
The Dependency Visualizer is a powerful tool for analyzing and visualizing component dependencies in the MCP system. It helps identify dependency conflicts, version compatibility issues, and provides visual representations of component relationships.

## Features

### Component Relationship Visualization
- Interactive dependency graph generation
- Customizable graph layouts
- Node and edge styling options
- Export/import functionality

### Dependency Conflict Detection
- Circular dependency detection
- Version conflict identification
- Deprecated component warnings
- Severity-based conflict classification

### Version Compatibility
- Version constraint checking
- Release date tracking
- Deprecation status monitoring
- Compatibility matrix generation

### Visual Mapping
- Graph visualization with matplotlib
- Custom node and edge attributes
- Layout algorithm selection
- Export to various formats

## Usage

### Basic Setup
```python
from mcp.components.dependency_visualizer import DependencyVisualizer

# Initialize the visualizer
visualizer = DependencyVisualizer()

# Add components
visualizer.add_component(
    name="component_a",
    version="1.0.0",
    dependencies={"component_b": ">=2.0.0"},
    release_date=datetime.now()
)

# Generate visualization
visualizer.generate_visualization(output_path="dependencies.png")
```

### Conflict Detection
```python
# Detect conflicts
conflicts = visualizer.detect_conflicts()

# Process conflicts
for conflict in conflicts:
    print(f"Conflict in {conflict.component}: {conflict.description}")
```

## Component Management

### Adding Components
- Specify component name and version
- Define dependencies and constraints
- Set release date and deprecation status
- Update component information

### Version Control
- Track component versions
- Monitor dependency requirements
- Check version compatibility
- Handle deprecation

## Visualization Options

### Graph Layout
- Dot layout (default)
- Spring layout
- Circular layout
- Custom layouts

### Styling
- Node colors and sizes
- Edge styles and arrows
- Label formatting
- Graph size and orientation

## Export/Import

### Graph Export
- Save as PNG/PDF
- Export graph data
- Generate reports
- Create documentation

### Graph Import
- Load from file
- Import from JSON
- Restore saved state
- Merge graphs

## Implementation Details

### Conflict Detection
1. **Circular Dependencies**
   - Graph cycle detection
   - Path analysis
   - Conflict reporting

2. **Version Conflicts**
   - Constraint checking
   - Version comparison
   - Compatibility validation

3. **Deprecation Checks**
   - Status verification
   - Warning generation
   - Migration suggestions

### Visualization
1. **Graph Generation**
   - Node creation
   - Edge connection
   - Attribute assignment

2. **Layout Calculation**
   - Position determination
   - Space optimization
   - Overlap prevention

3. **Rendering**
   - Style application
   - Label placement
   - Output generation

## Testing

Run the test suite:
```bash
python scripts/test_dependency_visualizer.py
```

The test suite verifies:
- Component management
- Conflict detection
- Version compatibility
- Visualization generation

## Integration

### Workflow Builder
- Real-time dependency checking
- Visual feedback
- Conflict resolution
- Version management

### CI/CD Pipeline
- Automated conflict detection
- Version validation
- Documentation generation
- Report creation

## Best Practices

1. **Component Management**
   - Regular version updates
   - Dependency review
   - Deprecation handling
   - Documentation maintenance

2. **Conflict Resolution**
   - Prioritize critical conflicts
   - Document resolutions
   - Update dependencies
   - Monitor changes

3. **Visualization**
   - Choose appropriate layout
   - Optimize graph size
   - Use clear labeling
   - Maintain readability

## Troubleshooting

### Common Issues

1. **Graph Generation**
   - Solution: Check component data
   - Verify dependencies
   - Validate versions
   - Review layout settings

2. **Conflict Detection**
   - Solution: Update version constraints
   - Resolve circular dependencies
   - Handle deprecation
   - Check compatibility

3. **Visualization**
   - Solution: Adjust layout
   - Modify styling
   - Update labels
   - Check output format

## Contributing

1. Follow the project's coding standards
2. Add tests for new features
3. Update documentation
4. Submit pull requests

## License
MIT 