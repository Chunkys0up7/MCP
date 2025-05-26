import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface MLRecommendation {
  id: string;
  title: string;
  description: string;
  confidence: number;
  type: 'component' | 'workflow' | 'template';
}

export interface TrendingComponent {
  id: string;
  name: string;
  description: string;
  usageCount: number;
  rating: number;
}

export interface TeamCollaboration {
  id: string;
  name: string;
  lastModified: string;
  collaborators: string[];
  type: 'workflow' | 'component' | 'document';
}

export const dashboardService = {
  async getMLRecommendations(): Promise<MLRecommendation[]> {
    const response = await axios.get(`${API_BASE_URL}/api/dashboard/recommendations`);
    return response.data;
  },

  async getTrendingComponents(): Promise<TrendingComponent[]> {
    const response = await axios.get(`${API_BASE_URL}/api/dashboard/trending`);
    return response.data;
  },

  async getTeamCollaborations(): Promise<TeamCollaboration[]> {
    const response = await axios.get(`${API_BASE_URL}/api/dashboard/collaborations`);
    return response.data;
  }
}; 