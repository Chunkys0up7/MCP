import React from 'react';
import { render, screen, act } from '@testing-library/react';
import ExecutionMonitorScreen from './ExecutionMonitorScreen';

// Mock Date.now() for consistent time in tests
const mockDateNow = 1678886400000; // March 15, 2023 12:00:00 PM UTC
jest.spyOn(Date, 'now').mockImplementation(() => mockDateNow);

// Mock setInterval and clearInterval to control time-based updates in tests
jest.useFakeTimers();

describe('ExecutionMonitorScreen', () => {
  beforeEach(() => {
    // Reset window.alert if it was mocked elsewhere or provide a Jest mock
    // window.alert = jest.fn(); 
    // Reset any other global mocks if necessary
  });

  afterEach(() => {
    jest.clearAllTimers(); // Clear all timers after each test
  });

  it('renders the main title and current time', () => {
    render(<ExecutionMonitorScreen />);
    expect(screen.getByText('Workflow Execution Monitor')).toBeInTheDocument();
    // Check for current time display (exact format might vary, so check for a part)
    // The initial time will be based on mockDateNow
    const expectedTime = new Date(mockDateNow).toLocaleTimeString();
    expect(screen.getByText(`Current Time: ${expectedTime}`)).toBeInTheDocument();
  });

  it('renders initial mock tasks with their names and statuses', () => {
    render(<ExecutionMonitorScreen />);
    // Check for a few sample tasks from initialMockTasks
    expect(screen.getByText('Initialize Data Pipeline')).toBeInTheDocument();
    expect(screen.getByText('Completed')).toBeInTheDocument(); 

    expect(screen.getByText('Process Batch A001')).toBeInTheDocument();
    // There might be multiple 'Running' statuses, so we get all and check length if needed
    // For simplicity, just check one is present
    expect(screen.getAllByText('Running').length).toBeGreaterThanOrEqual(1);

    expect(screen.getByText('Generate Insights Report')).toBeInTheDocument();
    expect(screen.getByText('Pending')).toBeInTheDocument();

    expect(screen.getByText('External API Call - Weather Service')).toBeInTheDocument();
    expect(screen.getByText('Failed')).toBeInTheDocument();
  });

  it('updates progress for running tasks over time', () => {
    render(<ExecutionMonitorScreen />);
    
    // Initial progress for 'Process Batch A001' is 60%
    // Task 'Data Validation Step' is 20%
    const task2Row = screen.getByText('Process Batch A001').closest('tr');
    expect(task2Row).toHaveTextContent('60%');

    const task5Row = screen.getByText('Data Validation Step').closest('tr');
    expect(task5Row).toHaveTextContent('20%');

    // Advance timers by 2 seconds (one interval)
    act(() => {
      jest.advanceTimersByTime(2000);
    });

    // Check updated progress
    expect(task2Row).toHaveTextContent('65%'); // 60 + 5
    expect(task5Row).toHaveTextContent('25%'); // 20 + 5

    // Advance timers by another 2 seconds
    act(() => {
      jest.advanceTimersByTime(2000);
    });
    expect(task2Row).toHaveTextContent('70%'); // 65 + 5
    expect(task5Row).toHaveTextContent('30%'); // 25 + 5
  });

  it('displays N/A for progress of pending tasks', () => {
    render(<ExecutionMonitorScreen />);
    const pendingTaskRow = screen.getByText('Generate Insights Report').closest('tr');
    // The cell with progress should contain N/A
    // We find the cell by its role or more specific query if needed.
    // Assuming the progress cell is the 3rd td (index 2)
    const progressCell = pendingTaskRow?.querySelectorAll('td')[2];
    expect(progressCell).toHaveTextContent('N/A');
  });

  it('displays workflow selection placeholder', () => {
    render(<ExecutionMonitorScreen />);
    expect(screen.getByText(/Workflow: Demo_CreditApproval_v1.2/)).toBeInTheDocument();
    expect(screen.getByRole('button', {name: 'Select Workflow'})).toBeInTheDocument();
  });

  it('displays correct status colors and progress bar fill', () => {
    render(<ExecutionMonitorScreen />);
    
    const completedTaskStatus = screen.getByText('Initialize Data Pipeline').closest('tr')?.querySelector('span.bg-green-100');
    expect(completedTaskStatus).toBeInTheDocument();
    const completedProgressBar = screen.getByText('Initialize Data Pipeline').closest('tr')?.querySelector('div.bg-green-500');
    expect(completedProgressBar).toHaveStyle('width: 100%');

    const runningTaskStatus = screen.getByText('Process Batch A001').closest('tr')?.querySelector('span.bg-blue-100');
    expect(runningTaskStatus).toBeInTheDocument();
    const runningProgressBar = screen.getByText('Process Batch A001').closest('tr')?.querySelector('div.bg-blue-500');
    expect(runningProgressBar).toHaveStyle('width: 60%'); // Initial progress

    const failedTaskRow = screen.getByText('External API Call - Weather Service').closest('tr');
    expect(failedTaskRow?.querySelector('span.bg-red-100')).toBeInTheDocument();
    // Check for specific styling on the row itself if applied
    expect(failedTaskRow).toHaveClass('bg-red-50');
    const failedProgressBar = failedTaskRow?.querySelector('div.bg-red-500');
    expect(failedProgressBar).toHaveStyle('width: 100%');
  });
}); 