export interface ComponentSummary {
  id: string;
  name: string;
  version: string;
  description: string;
  type: string;
  tags?: string[];
  rating?: number;
}

export interface ComponentDetail extends ComponentSummary {
  input_schema?: object;
  output_schema?: object;
  compliance?: string[];
  // Add more fields as needed
}

const MOCK_DELAY = 500;

const mockComponents: ComponentSummary[] = [
  {
    id: 'comp1',
    name: 'GPT-4 Turbo',
    version: '1.2',
    description: 'Advanced LLM for text generation.',
    type: 'LLM',
    tags: ['LLM', 'OpenAI'],
    rating: 4.8,
  },
  {
    id: 'comp2',
    name: 'Data Validator',
    version: '2.0',
    description: 'Validates input data schemas.',
    type: 'Data',
    tags: ['Data', 'Utility', 'SOC2'],
    rating: 4.2,
  },
  // Add more mock components as needed
];

export const searchComponents = async (params: {
  type?: string;
  compliance?: string[];
  cost?: string;
  query?: string;
}): Promise<ComponentSummary[]> => {
  // Simulate filtering and search
  let results = mockComponents;
  if (params.type) {
    results = results.filter(c => c.type === params.type);
  }
  if (params.compliance && params.compliance.length > 0) {
    results = results.filter(c =>
      params.compliance?.every(comp => c.tags?.includes(comp))
    );
  }
  if (params.query) {
    const q = params.query.toLowerCase();
    results = results.filter(c =>
      c.name.toLowerCase().includes(q) ||
      c.description.toLowerCase().includes(q)
    );
  }
  // Cost filter is ignored in mock
  return new Promise(resolve => setTimeout(() => resolve(results), MOCK_DELAY));
};

export const getComponentDetails = async (id: string): Promise<ComponentDetail> => {
  const found = mockComponents.find(c => c.id === id);
  if (!found) throw new Error('Component not found');
  // Add more detail fields as needed
  return new Promise(resolve => setTimeout(() => resolve({
    ...found,
    input_schema: {},
    output_schema: {},
    compliance: found.tags?.filter(tag => ['SOC2', 'GDPR', 'HIPAA'].includes(tag)),
  }), MOCK_DELAY));
}; 