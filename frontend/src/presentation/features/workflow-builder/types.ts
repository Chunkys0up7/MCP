export interface ValidationError {
  type: 'node' | 'edge' | 'workflow';
  id?: string;
  message: string;
} 