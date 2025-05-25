import { useState, useCallback, useEffect } from 'react';
import { Node, Edge } from 'reactflow';
import { workflowValidationService } from '../../infrastructure/services/workflowValidationService';
import { WorkflowValidationResult, ValidationError } from '../../domain/models/workflow';

export const useWorkflowValidation = (nodes: Node[], edges: Edge[]) => {
  const [validationResult, setValidationResult] = useState<WorkflowValidationResult>({
    isValid: true,
    errors: [],
    warnings: [],
    timestamp: new Date().toISOString()
  });

  const validateWorkflow = useCallback(() => {
    const result = workflowValidationService.validateWorkflow(nodes, edges);
    setValidationResult(result);
    return result;
  }, [nodes, edges]);

  const getErrorsForNode = useCallback((nodeId: string): ValidationError[] => {
    return validationResult.errors.filter(error => error.nodeId === nodeId);
  }, [validationResult]);

  const getWarningsForNode = useCallback((nodeId: string): ValidationError[] => {
    return validationResult.warnings.filter(warning => warning.nodeId === nodeId);
  }, [validationResult]);

  // Automatically validate when nodes or edges change
  useEffect(() => {
    validateWorkflow();
  }, [validateWorkflow]);

  return {
    validationResult,
    validateWorkflow,
    getErrorsForNode,
    getWarningsForNode,
    isValid: validationResult.isValid
  };
}; 