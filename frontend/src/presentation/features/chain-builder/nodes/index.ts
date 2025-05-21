import { NodeTypes } from 'reactflow';

// Basic node types
export const nodeTypes: NodeTypes = {
  input: {
    type: 'input',
    data: { label: 'Input Node' },
  },
  default: {
    type: 'default',
    data: { label: 'Default Node' },
  },
  output: {
    type: 'output',
    data: { label: 'Output Node' },
  },
}; 