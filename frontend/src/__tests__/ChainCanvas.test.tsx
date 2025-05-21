import { render } from '@testing-library/react';
import '@testing-library/jest-dom';
import ChainCanvas from '../presentation/features/chain-builder/ChainCanvas';
import { describe, it, expect } from 'vitest';

describe('ChainCanvas', () => {
  it('renders without crashing', () => {
    const { container } = render(<ChainCanvas />);
    expect(container.querySelector('.react-flow')).toBeInTheDocument();
  });
}); 