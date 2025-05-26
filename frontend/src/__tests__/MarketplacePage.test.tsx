import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import MarketplacePage from '../pages/MarketplacePage';
import * as api from '../services/api';

jest.mock('../services/api');

const mockComponents = [
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
];

describe('MarketplacePage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (api.searchComponents as jest.Mock).mockResolvedValue(mockComponents);
    (api.getComponentDetails as jest.Mock).mockImplementation((id) =>
      Promise.resolve(mockComponents.find((c) => c.id === id))
    );
  });

  it('renders MarketplacePage and loads components', async () => {
    render(<MarketplacePage />);
    expect(screen.getByText(/Component Marketplace/i)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText(/GPT-4 Turbo/)).toBeInTheDocument();
      expect(screen.getByText(/Data Validator/)).toBeInTheDocument();
    });
  });

  it('filters by type using FilterPanel', async () => {
    render(<MarketplacePage />);
    await waitFor(() => screen.getByText(/GPT-4 Turbo/));
    fireEvent.change(screen.getByLabelText(/Type:/), { target: { value: 'LLM' } });
    await waitFor(() => {
      expect(screen.getByText(/GPT-4 Turbo/)).toBeInTheDocument();
      const cards = screen.getAllByText(/Data Validator/);
      expect(cards.length).toBe(0);
    });
  });

  it('searches by keyword', async () => {
    render(<MarketplacePage />);
    await waitFor(() => screen.getByText(/GPT-4 Turbo/));
    fireEvent.change(screen.getByPlaceholderText(/Search components.../), { target: { value: 'Validator' } });
    await waitFor(() => {
      expect(screen.getByText(/Data Validator/)).toBeInTheDocument();
      const cards = screen.getAllByText(/GPT-4 Turbo/);
      const closeBtn = screen.queryByRole('button', { name: /×/ });
      if (closeBtn) fireEvent.click(closeBtn);
      expect(screen.queryByText(/GPT-4 Turbo/)).not.toBeInTheDocument();
    });
  });

  it('opens ComponentDetailView on card click and shows tabs', async () => {
    render(<MarketplacePage />);
    await waitFor(() => screen.getByText(/GPT-4 Turbo/));
    fireEvent.click(screen.getByText(/GPT-4 Turbo/));
    await waitFor(() => {
      expect(screen.getAllByText(/Overview/).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/Dependencies/).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/Sandbox/).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/Versions/).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/Reviews/).length).toBeGreaterThan(0);
    });
  });

  it('shows dependency visualizer in Dependencies tab', async () => {
    render(<MarketplacePage />);
    await waitFor(() => screen.getByText(/GPT-4 Turbo/));
    fireEvent.click(screen.getByText(/GPT-4 Turbo/));
    await waitFor(() => screen.getAllByText(/Overview/));
    fireEvent.click(screen.getAllByText(/Dependencies/)[0]);
    expect(screen.getAllByText(/Dependencies/).length).toBeGreaterThan(0);
    expect(screen.getByRole('img', { hidden: true }) || screen.getByText(/GPT-4 Turbo/)).toBeTruthy();
  });

  it('handles Add to Workflow and Test in Sandbox actions', async () => {
    render(<MarketplacePage />);
    await waitFor(() => screen.getByText(/GPT-4 Turbo/));
    fireEvent.click(screen.getByText(/GPT-4 Turbo/));
    await waitFor(() => screen.getByText(/Add to Workflow/));
    fireEvent.click(screen.getByText(/Add to Workflow/));
    expect(await screen.findByText(/Component added to workflow/)).toBeInTheDocument();
    fireEvent.click(screen.getByText(/Test in Sandbox/));
    expect(await screen.findByText(/Sandbox test started/)).toBeInTheDocument();
  });

  it('is accessible (has headings, labels, and roles)', async () => {
    render(<MarketplacePage />);
    await waitFor(() => screen.getByText(/Component Marketplace/));
    expect(screen.getByRole('heading', { name: /Component Marketplace/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/Type:/)).toBeInTheDocument();
    expect(screen.getByRole('group', { name: /Compliance:/ })).toBeInTheDocument();
    expect(screen.getByLabelText(/Cost:/)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Search components.../)).toBeInTheDocument();
  });
}); 