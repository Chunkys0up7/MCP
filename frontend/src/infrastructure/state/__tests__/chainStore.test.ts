import { renderHook, act } from '@testing-library/react';
import { useChainStore } from '../chainStore';
import { ChainService } from '../../services/chainService';
import { ChainInfo, ChainNode, ChainEdge } from '../../types/chain';

const mockChainInfo: ChainInfo = {
  id: 'test-chain',
  name: 'Test Chain',
  description: 'A test chain',
  config: {
    errorHandling: {
      strategy: 'retry',
      maxRetries: 3,
      backoffFactor: 2
    },
    executionMode: 'sequential'
  },
  nodes: [],
  edges: [],
  createdAt: '2024-01-01T00:00:00Z',
  updatedAt: '2024-01-01T00:00:00Z'
};

const mockChainService: ChainService = {
  getChain: jest.fn().mockResolvedValue(mockChainInfo),
  updateChainConfig: jest.fn().mockResolvedValue(mockChainInfo),
  executeChain: jest.fn().mockResolvedValue(undefined),
  stopExecution: jest.fn().mockResolvedValue(undefined)
};

describe('useChainStore', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    const { result } = renderHook(() => useChainStore());
    act(() => {
      result.current.chainService = mockChainService;
    });
  });

  it('should load a chain', async () => {
    const { result } = renderHook(() => useChainStore());

    await act(async () => {
      await result.current.loadChain('test-chain');
    });

    expect(result.current.chainInfo).toEqual(mockChainInfo);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('should handle load chain error', async () => {
    const error = new Error('Failed to load chain');
    (mockChainService.getChain as jest.Mock).mockRejectedValueOnce(error);

    const { result } = renderHook(() => useChainStore());

    await act(async () => {
      await result.current.loadChain('test-chain');
    });

    expect(result.current.error).toBe('Failed to load chain');
    expect(result.current.isLoading).toBe(false);
  });

  it('should save a chain', async () => {
    const { result } = renderHook(() => useChainStore());

    await act(async () => {
      await result.current.loadChain('test-chain');
      await result.current.saveChain();
    });

    expect(mockChainService.updateChainConfig).toHaveBeenCalledWith(
      'test-chain',
      {
        config: mockChainInfo.config,
        nodes: [],
        edges: []
      }
    );
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('should execute a chain', async () => {
    const { result } = renderHook(() => useChainStore());

    await act(async () => {
      await result.current.loadChain('test-chain');
      await result.current.executeChain();
    });

    expect(mockChainService.executeChain).toHaveBeenCalledWith('test-chain');
    expect(result.current.isExecuting).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('should stop execution', async () => {
    const { result } = renderHook(() => useChainStore());

    await act(async () => {
      await result.current.loadChain('test-chain');
      await result.current.stopExecution();
    });

    expect(mockChainService.stopExecution).toHaveBeenCalledWith('test-chain');
    expect(result.current.isExecuting).toBe(false);
  });

  it('should update a node', () => {
    const { result } = renderHook(() => useChainStore());
    const node: ChainNode = {
      id: 'node-1',
      type: 'test',
      position: { x: 0, y: 0 },
      data: { label: 'Test Node', config: {} }
    };

    act(() => {
      result.current.addNode(node);
      result.current.updateNode('node-1', { data: { label: 'Updated Node' } });
    });

    expect(result.current.nodes[0].data.label).toBe('Updated Node');
  });

  it('should update an edge', () => {
    const { result } = renderHook(() => useChainStore());
    const edge: ChainEdge = {
      id: 'edge-1',
      source: 'node-1',
      target: 'node-2'
    };

    act(() => {
      result.current.addEdge(edge);
      result.current.updateEdge('edge-1', { animated: true });
    });

    expect(result.current.edges[0].animated).toBe(true);
  });

  it('should remove a node and its connected edges', () => {
    const { result } = renderHook(() => useChainStore());
    const node: ChainNode = {
      id: 'node-1',
      type: 'test',
      position: { x: 0, y: 0 },
      data: { label: 'Test Node', config: {} }
    };
    const edge: ChainEdge = {
      id: 'edge-1',
      source: 'node-1',
      target: 'node-2'
    };

    act(() => {
      result.current.addNode(node);
      result.current.addEdge(edge);
      result.current.removeNode('node-1');
    });

    expect(result.current.nodes).toHaveLength(0);
    expect(result.current.edges).toHaveLength(0);
  });

  it('should remove an edge', () => {
    const { result } = renderHook(() => useChainStore());
    const edge: ChainEdge = {
      id: 'edge-1',
      source: 'node-1',
      target: 'node-2'
    };

    act(() => {
      result.current.addEdge(edge);
      result.current.removeEdge('edge-1');
    });

    expect(result.current.edges).toHaveLength(0);
  });

  it('should clear error', () => {
    const { result } = renderHook(() => useChainStore());

    act(() => {
      result.current.error = 'Test error';
      result.current.clearError();
    });

    expect(result.current.error).toBeNull();
  });
}); 