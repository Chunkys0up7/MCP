# MCP Chain Builder UI Documentation

> **Note:** This documentation is being updated for the new React (MUI/ReactFlow) UI. The previous Streamlit UI is deprecated and no longer supported.

## Overview
The MCP Chain Builder is a visual interface for creating, managing, and executing workflows of Managed Component Providers (MCPs). The interface is built using React (MUI/ReactFlow) and provides an intuitive way to compose complex workflows.

## UI Components

### 1. Navigation Sidebar
**Location**: Left side of the screen
**Components**:
- Dashboard
- Create MCP
- Manage MCPs
- Test MCPs
- Chain Builder
- Settings

### 2. Chain Builder Interface

#### 2.1 Chain Information Section
**Location**: Top of the main content area
**Components**:
- Chain Name (Text Input)
  - Label: "Chain Name"
  - Type: Text input field
  - Required: Yes
  - Validation: Non-empty string

- Description (Text Area)
  - Label: "Description"
  - Type: Multi-line text area
  - Height: 100 pixels
  - Required: No

#### 2.2 MCP Workflow Section
**Location**: Below Chain Information
**Layout**: Two-column design

##### Left Column - Available MCPs
**Components**:
- Header: "Available MCPs"
- MCP Cards:
  - Background: Light gray (#f8f9fa)
  - Border: 1px solid #ddd
  - Border Radius: 5px
  - Padding: 10px
  - Margin: 10px bottom
  - Content:
    - MCP Name (h4)
    - MCP Type (p, gray text)
    - Description (p, smaller font)
  - Action Button: "Add to Chain"

##### Right Column - Workflow Design
**Components**:
- Header: "Workflow Design"
- MCP Nodes:
  - Background: Light blue (#e3f2fd)
  - Border: 2px solid #2196f3
  - Border Radius: 8px
  - Padding: 15px
  - Margin: 15px bottom
  - Content:
    - MCP Name (h3)
    - MCP Type (p, gray text)
  - Controls:
    - Up Arrow (⬆️): Move node up
    - Down Arrow (⬇️): Move node down
    - Remove Button (❌): Delete node
  - Connection Line:
    - Position: Bottom center
    - Style: 2px solid #2196f3
    - Height: 20px

#### 2.3 Input Configuration Section
**Location**: Below Workflow Design
**Components**:
- Header: "Input Configuration"
- Expandable Sections:
  - Title: "Inputs for [MCP Name]"
  - Layout: Two columns
    - Left: Input variable name (bold)
    - Right: Input mapping field
      - Type: Text input
      - Label: Hidden
      - Help text: "Enter the value or reference for [variable]"

#### 2.4 Chain Configuration Section
**Location**: Below Input Configuration
**Components**:
- Header: "Chain Configuration"
- Layout: Two columns

##### Left Column
- Error Handling Strategy (Select Box)
  - Options:
    - "Retry with Backoff"
    - "Fallback Chain"
    - "Stop on Error"
  - Conditional Fields (when "Retry with Backoff" selected):
    - Max Retries (Number Input)
      - Range: 1-5
      - Default: 3
    - Backoff Factor (Number Input)
      - Range: 1-10
      - Default: 2
      - Unit: seconds

##### Right Column
- Execution Mode (Select Box)
  - Options:
    - "Sequential"
    - "Parallel"

#### 2.5 Save Chain Button
**Location**: Bottom of the interface
**Type**: Primary button
**Label**: "Save Chain"
**Action**: Validates and saves chain configuration

## User Flows

### 1. Creating a New Chain
1. Enter chain name and description
2. Add MCPs from the available list
3. Arrange MCPs in desired order
4. Configure inputs for each MCP
5. Set chain-wide configuration
6. Save the chain

### 2. Modifying an Existing Chain
1. Select chain from the list
2. Modify MCP order using up/down arrows
3. Add/remove MCPs as needed
4. Update input configurations
5. Adjust chain settings
6. Save changes

### 3. Error Handling
- Validation errors display in red
- Success messages display in green
- Chain validation checks:
  - Non-empty chain name
  - At least one MCP in chain
  - Valid input mappings

## Data Flow

### 1. MCP Loading
- Source: mcp_storage.json
- Format: JSON
- Structure:
  ```json
  {
    "mcp_id": {
      "name": "string",
      "type": "string",
      "description": "string",
      "config": {
        "input_variables": ["string"]
      }
    }
  }
  ```

### 2. Chain Saving
- Destination: chain_storage.json
- Format: JSON
- Structure:
  ```json
  {
    "chain_id": {
      "name": "string",
      "description": "string",
      "steps": [
        {
          "mcp_id": "string",
          "inputs": {
            "variable": "value"
          }
        }
      ],
      "error_handling": {
        "strategy": "string",
        "max_retries": number,
        "backoff_factor": number
      },
      "execution_mode": "string"
    }
  }
  ```

## State Management

### Session State Variables
- `selected_mcps`: List of selected MCPs
- `node_positions`: Dictionary of node positions
- `chain_id`: Unique identifier for current chain
- Input mapping states: `input_{mcp_id}_{variable}`

## Error Handling

### 1. Validation Errors
- Chain name required
- At least one MCP required
- Invalid input mappings

### 2. System Errors
- File not found errors
- JSON parsing errors
- Connection errors

## Responsive Design
- Two-column layout for desktop
- Single-column layout for mobile
- Collapsible sections for better space management
- Scrollable content areas

## Accessibility
- Clear visual hierarchy
- Consistent color coding
- Keyboard navigation support
- Screen reader friendly labels
- High contrast text
- Adequate touch targets 