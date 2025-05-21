import axios from 'axios';
import type { Node, Edge } from 'reactflow';

const API_BASE = '/api/flow';

export async function loadWorkflow(id: string): Promise<{ nodes: Node[]; edges: Edge[] }> {
  const res = await axios.get(`${API_BASE}/${id}`);
  return res.data;
}

export async function saveWorkflow(id: string, nodes: Node[], edges: Edge[]): Promise<void> {
  await axios.post(`${API_BASE}/${id}`, { nodes, edges });
}

export async function executeWorkflow(id: string): Promise<{ logs: string[]; result: any }> {
  const res = await axios.post(`${API_BASE}/${id}/execute`);
  return res.data;
} 