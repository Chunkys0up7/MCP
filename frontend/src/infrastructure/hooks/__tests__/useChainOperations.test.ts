import { renderHook, act } from '@testing-library/react';
import { useChainOperations } from '../useChainOperations';
import { useChainStore } from '../../state/chainStore';
import { useNotification } from '../useNotification';

// Mock the dependencies
jest.mock('../../state/chainStore');
jest.mock('../useNotification');

describe('useChainOperations', () => {
  const mockShowNotification = jest.fn();
  const mockLoadChain = jest.fn();
  const mockSaveChain = jest.fn();
  const mockExecuteChain = jest.fn();
  const mockAddNode = jest.fn();
  const mockUpdateNode = jest.fn();
  const mockRemoveNode = jest.fn();
  const mockAddEdge = jest.fn();
  const mockRemoveEdge = jest.fn();
  const mockClearError = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useNotification as jest.Mock).mockReturnValue({ showNotification: mockShowNotification });
    (useChainStore as jest.Mock).mockReturnValue({
      nodes: [],
      edges: [],
      chainInfo: null,
      isLoading: false,
      error: null,
      loadChain: mockLoadChain,
      saveChain: mockSaveChain,
      executeChain: mockExecuteChain,
      addNode: mockAddNode,
      updateNode: mockUpdateNode,
      removeNode: mockRemoveNode,
      addEdge: mockAddEdge,
      removeEdge: mockRemoveEdge,
      clearError: mockClearError,
    });
  });

  it('should handle loadChain successfully', async () => {
    const { result } = renderHook(() => useChainOperations());
    mockLoadChain.mockResolvedValueOnce(undefined);

    await act(async () => {
      await result.current.handleLoadChain('test-id');
    });

    expect(mockLoadChain).toHaveBeenCalledWith('test-id');
    expect(mockShowNotification).toHaveBeenCalledWith('Chain loaded successfully', 'success');
  });

  it('should handle loadChain failure', async () => {
    const { result } = renderHook(() => useChainOperations());
    mockLoadChain.mockRejectedValueOnce(new Error('Failed to load'));

    await act(async () => {
      await result.current.handleLoadChain('test-id');
    });

    expect(mockLoadChain).toHaveBeenCalledWith('test-id');
    expect(mockShowNotification).toHaveBeenCalledWith('Failed to load chain', 'error');
  });

  it('should handle saveChain successfully', async () => {
    const { result } = renderHook(() => useChainOperations());
    mockSaveChain.mockResolvedValueOnce(undefined);

    await act(async () => {
      await result.current.handleSaveChain();
    });

    expect(mockSaveChain).toHaveBeenCalled();
    expect(mockShowNotification).toHaveBeenCalledWith('Chain saved successfully', 'success');
  });

  it('should handle executeChain successfully', async () => {
    const { result } = renderHook(() => useChainOperations());
    mockExecuteChain.mockResolvedValueOnce('execution-id');

    await act(async () => {
      await result.current.handleExecuteChain();
    });

    expect(mockExecuteChain).toHaveBeenCalled();
    expect(mockShowNotification).toHaveBeenCalledWith('Chain execution started', 'success');
  });

  it('should handle addNode successfully', () => {
    const { result } = renderHook(() => useChainOperations());
    const testNode = { id: 'test-node', type: 'mcp', position: { x: 0, y: 0 }, data: {} };

    act(() => {
      result.current.handleAddNode(testNode);
    });

    expect(mockAddNode).toHaveBeenCalledWith(testNode);
    expect(mockShowNotification).toHaveBeenCalledWith('Node added successfully', 'success');
  });

  it('should handle updateNode successfully', () => {
    const { result } = renderHook(() => useChainOperations());
    const testData = { label: 'Updated Node' };

    act(() => {
      result.current.handleUpdateNode('test-node', testData);
    });

    expect(mockUpdateNode).toHaveBeenCalledWith('test-node', testData);
    expect(mockShowNotification).toHaveBeenCalledWith('Node updated successfully', 'success');
  });

  it('should handle removeNode successfully', () => {
    const { result } = renderHook(() => useChainOperations());

    act(() => {
      result.current.handleRemoveNode('test-node');
    });

    expect(mockRemoveNode).toHaveBeenCalledWith('test-node');
    expect(mockShowNotification).toHaveBeenCalledWith('Node removed successfully', 'success');
  });

  it('should handle addEdge successfully', () => {
    const { result } = renderHook(() => useChainOperations());
    const testEdge = { id: 'test-edge', source: 'node1', target: 'node2' };

    act(() => {
      result.current.handleAddEdge(testEdge);
    });

    expect(mockAddEdge).toHaveBeenCalledWith(testEdge);
    expect(mockShowNotification).toHaveBeenCalledWith('Edge added successfully', 'success');
  });

  it('should handle removeEdge successfully', () => {
    const { result } = renderHook(() => useChainOperations());

    act(() => {
      result.current.handleRemoveEdge('test-edge');
    });

    expect(mockRemoveEdge).toHaveBeenCalledWith('test-edge');
    expect(mockShowNotification).toHaveBeenCalledWith('Edge removed successfully', 'success');
  });
}); 