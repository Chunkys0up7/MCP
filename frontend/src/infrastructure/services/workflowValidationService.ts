import { Node, Edge } from 'reactflow';
import { ValidationRule, ValidationError, WorkflowValidationResult } from '../../domain/models/workflow';

class WorkflowValidationService {
  private rules: ValidationRule[] = [];

  constructor() {
    // Initialize with default rules
    this.rules = [
      {
        id: 'no-cycles',
        name: 'No Cycles',
        description: 'Workflow should not contain any cycles',
        validate: this.validateNoCycles
      },
      {
        id: 'input-output-connection',
        name: 'Input/Output Connection',
        description: 'All input nodes should be connected to at least one output node',
        validate: this.validateInputOutputConnection
      },
      {
        id: 'required-fields',
        name: 'Required Fields',
        description: 'All nodes should have their required fields filled',
        validate: this.validateRequiredFields
      }
    ];
  }

  private validateNoCycles(nodes: Node[], edges: Edge[]): ValidationError[] {
    const errors: ValidationError[] = [];
    const visited = new Set<string>();
    const recursionStack = new Set<string>();

    const dfs = (nodeId: string) => {
      visited.add(nodeId);
      recursionStack.add(nodeId);

      const outgoingEdges = edges.filter(edge => edge.source === nodeId);
      for (const edge of outgoingEdges) {
        if (!visited.has(edge.target)) {
          if (dfs(edge.target)) {
            return true;
          }
        } else if (recursionStack.has(edge.target)) {
          errors.push({
            type: 'cycle-detected',
            message: `Cycle detected in workflow involving node ${nodeId}`,
            nodeId,
            severity: 'error'
          });
          return true;
        }
      }

      recursionStack.delete(nodeId);
      return false;
    };

    for (const node of nodes) {
      if (!visited.has(node.id)) {
        dfs(node.id);
      }
    }

    return errors;
  }

  private validateInputOutputConnection(nodes: Node[], edges: Edge[]): ValidationError[] {
    const errors: ValidationError[] = [];
    const inputNodes = nodes.filter(node => node.type === 'input');
    const outputNodes = nodes.filter(node => node.type === 'output');

    for (const inputNode of inputNodes) {
      const hasPathToOutput = this.hasPathToOutput(inputNode.id, edges, outputNodes.map(n => n.id));
      if (!hasPathToOutput) {
        errors.push({
          type: 'disconnected-input',
          message: `Input node ${inputNode.id} is not connected to any output node`,
          nodeId: inputNode.id,
          severity: 'error'
        });
      }
    }

    return errors;
  }

  private validateRequiredFields(nodes: Node[]): ValidationError[] {
    const errors: ValidationError[] = [];

    for (const node of nodes) {
      const requiredFields = this.getRequiredFieldsForNodeType(node.type);
      for (const field of requiredFields) {
        if (!node.data?.[field]) {
          errors.push({
            type: 'missing-required-field',
            message: `Node ${node.id} is missing required field: ${field}`,
            nodeId: node.id,
            severity: 'error',
            details: { field }
          });
        }
      }
    }

    return errors;
  }

  private hasPathToOutput(nodeId: string, edges: Edge[], outputNodeIds: string[]): boolean {
    const visited = new Set<string>();
    const queue = [nodeId];

    while (queue.length > 0) {
      const current = queue.shift()!;
      if (outputNodeIds.includes(current)) {
        return true;
      }

      visited.add(current);
      const outgoingEdges = edges.filter(edge => edge.source === current);
      for (const edge of outgoingEdges) {
        if (!visited.has(edge.target)) {
          queue.push(edge.target);
        }
      }
    }

    return false;
  }

  private getRequiredFieldsForNodeType(nodeType: string): string[] {
    switch (nodeType) {
      case 'input':
        return ['name', 'type'];
      case 'output':
        return ['name', 'type'];
      case 'data':
        return ['name', 'dataType'];
      case 'notebook':
        return ['name', 'notebookId'];
      case 'llm':
        return ['name', 'model', 'prompt'];
      default:
        return [];
    }
  }

  validateWorkflow(nodes: Node[], edges: Edge[]): WorkflowValidationResult {
    const errors: ValidationError[] = [];
    const warnings: ValidationError[] = [];

    for (const rule of this.rules) {
      const ruleErrors = rule.validate(nodes, edges);
      ruleErrors.forEach(error => {
        if (error.severity === 'error') {
          errors.push(error);
        } else {
          warnings.push(error);
        }
      });
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
      timestamp: new Date().toISOString()
    };
  }

  addRule(rule: ValidationRule): void {
    this.rules.push(rule);
  }

  removeRule(ruleId: string): void {
    this.rules = this.rules.filter(rule => rule.id !== ruleId);
  }
}

export const workflowValidationService = new WorkflowValidationService(); 