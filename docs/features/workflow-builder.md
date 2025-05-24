# Workflow Builder

The Workflow Builder is a visual tool for creating and managing MCP workflows. It provides an intuitive interface for connecting different components and configuring their properties.

## Features

### Visual Canvas
- Drag-and-drop interface for adding nodes
- Interactive node connections
- Real-time validation
- Mini-map for navigation
- Background grid for alignment
- Zoom and pan controls

### Node Types
1. **LLM Node**
   - Model selection
   - Temperature control
   - Max tokens configuration
   - System prompt customization

2. **Notebook Node**
   - Notebook path selection
   - Kernel configuration
   - Timeout settings
   - Environment variables

3. **Data Node**
   - Data type selection
   - Source configuration
   - Format specification
   - Schema validation

### Node Configuration
- Property panel for node configuration
- Real-time validation of node properties
- Support for different data types
- Environment variable management

### Validation
- Real-time workflow validation
- Node property validation
- Connection validation
- Cycle detection
- Disconnected node detection

## Usage

1. **Adding Nodes**
   - Drag nodes from the palette to the canvas
   - Configure node properties in the side panel
   - Connect nodes by dragging from one handle to another

2. **Configuring Nodes**
   - Click on a node to open the configuration panel
   - Set required properties
   - Add environment variables if needed
   - Save changes to update the node

3. **Connecting Nodes**
   - Drag from a node's output handle to another node's input handle
   - Add labels to connections
   - Validate connections in real-time

4. **Validating Workflow**
   - View validation errors in the validation panel
   - Fix errors by configuring nodes or adjusting connections
   - Ensure all required properties are set

## Implementation Details

### Components
- `WorkflowCanvas`: Main canvas component
- `NodePalette`: Node selection and drag source
- `NodeConfigPanel`: Node configuration interface
- `ValidationPanel`: Workflow validation display
- `WorkflowValidator`: Validation logic

### State Management
- Uses Zustand for state management
- Tracks nodes, edges, and selected items
- Manages node and edge updates
- Handles validation state

### Node Types
- Custom node components for each type
- Type-specific configuration options
- Validation rules per node type
- Environment variable support

## Future Enhancements

1. **Advanced Features**
   - Node templates
   - Workflow templates
   - Import/export functionality
   - Version control integration

2. **UI Improvements**
   - Custom node styling
   - Connection animations
   - Better error visualization
   - Improved navigation

3. **Validation**
   - More comprehensive validation rules
   - Custom validation rules
   - Validation history
   - Auto-fix suggestions

4. **Performance**
   - Large workflow optimization
   - Better state management
   - Improved rendering
   - Caching strategies 