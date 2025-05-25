import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export interface ComponentFilter {
  type?: string[];
  tags?: string[];
  minRating?: number;
  minUsage?: number;
  searchTerm?: string;
}

export interface Component {
  id: string;
  name: string;
  description: string;
  type: string;
  tags: string[];
  rating: number;
  usageCount: number;
  author: string;
  lastUpdated: string;
  version: string;
  documentation: string;
  dependencies: string[];
}

export interface SearchResponse {
  components: Component[];
  total: number;
  page: number;
  pageSize: number;
  facets: {
    types: { [key: string]: number };
    tags: { [key: string]: number };
  };
}

export interface Review {
  id: string;
  component_id: string;
  user_id: string;
  rating: number;
  review_text?: string;
  created_at: string;
  updated_at: string;
}

export interface ReviewCreate {
  component_id: string;
  user_id: string;
  rating: number;
  review_text?: string;
}

export const componentRegistryService = {
  async searchComponents(
    filters: ComponentFilter,
    page: number = 1,
    pageSize: number = 10
  ): Promise<SearchResponse> {
    const response = await axios.get(`${API_BASE_URL}/api/components/search`, {
      params: {
        ...filters,
        page,
        pageSize,
      },
    });
    return response.data;
  },

  async getComponentById(id: string): Promise<Component> {
    const response = await axios.get(`${API_BASE_URL}/api/components/${id}`);
    return response.data;
  },

  async getAvailableTypes(): Promise<string[]> {
    const response = await axios.get(`${API_BASE_URL}/api/components/types`);
    return response.data;
  },

  async getPopularTags(): Promise<string[]> {
    const response = await axios.get(`${API_BASE_URL}/api/components/tags`);
    return response.data;
  },

  async getReviewsForComponent(componentId: string): Promise<Review[]> {
    const response = await axios.get(`${API_BASE_URL}/reviews/component/${componentId}`);
    return response.data;
  },

  async addReview(review: ReviewCreate): Promise<Review> {
    const response = await axios.post(`${API_BASE_URL}/reviews/`, review);
    return response.data;
  },

  async deleteReview(reviewId: string): Promise<void> {
    await axios.delete(`${API_BASE_URL}/reviews/${reviewId}`);
  }
}; 