import React, { useState, useEffect } from 'react';

interface Task {
  id: string;
  name: string;
  status: 'Pending' | 'Running' | 'Completed' | 'Failed';
  startTime: Date | null;
  endTime: Date | null;
  duration: string | null; // e.g., '5s', '2m', '1h'
  assignee: string | null;
  progress?: number; // Optional: 0-100
}

// Mock data for running tasks - replace with API data and real-time updates later
const initialMockTasks: Task[] = [
  {
    id: 'task-1',
    name: 'Initialize Data Pipeline',
    status: 'Completed',
    startTime: new Date(Date.now() - 1000 * 60 * 5), // 5 minutes ago
    endTime: new Date(Date.now() - 1000 * 60 * 4),   // 4 minutes ago
    duration: '1m',
    assignee: 'Worker A',
    progress: 100,
  },
  {
    id: 'task-2',
    name: 'Process Batch A001',
    status: 'Running',
    startTime: new Date(Date.now() - 1000 * 60 * 3), // 3 minutes ago
    endTime: null,
    duration: null,
    assignee: 'Worker B',
    progress: 60,
  },
  {
    id: 'task-3',
    name: 'Generate Insights Report',
    status: 'Pending',
    startTime: null,
    endTime: null,
    duration: null,
    assignee: null,
    progress: 0,
  },
  {
    id: 'task-4',
    name: 'External API Call - Weather Service',
    status: 'Failed',
    startTime: new Date(Date.now() - 1000 * 60 * 10),
    endTime: new Date(Date.now() - 1000 * 60 * 9.5),
    duration: '30s',
    assignee: 'Worker C',
    progress: 100, // or some value if it failed mid-way
  },
    {
    id: 'task-5',
    name: 'Data Validation Step',
    status: 'Running',
    startTime: new Date(Date.now() - 1000 * 30), // 30 seconds ago
    endTime: null,
    duration: null,
    assignee: 'Worker A',
    progress: 20,
  },
];

const getStatusColor = (status: Task['status']) => {
  switch (status) {
    case 'Completed': return 'bg-green-100 text-green-700';
    case 'Running': return 'bg-blue-100 text-blue-700';
    case 'Pending': return 'bg-yellow-100 text-yellow-700';
    case 'Failed': return 'bg-red-100 text-red-700';
    default: return 'bg-gray-100 text-gray-700';
  }
};

const ExecutionMonitorScreen: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>(initialMockTasks);
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    // Simulate real-time updates for progress and current time
    const intervalId = setInterval(() => {
      setCurrentTime(new Date());
      setTasks(prevTasks => 
        prevTasks.map(task => {
          if (task.status === 'Running' && task.progress !== undefined && task.progress < 100) {
            return { ...task, progress: Math.min(task.progress + 5, 100) }; // Increment progress
          }
          return task;
        })
      );
    }, 2000); // Update every 2 seconds
    return () => clearInterval(intervalId);
  }, []);

  const formatDateTime = (date: Date | null) => {
    return date ? date.toLocaleTimeString() : 'N/A';
  };

  return (
    <div className="p-4 md:p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl md:text-3xl font-bold">Workflow Execution Monitor</h1>
        <div className="text-sm text-gray-600">
          Current Time: {currentTime.toLocaleTimeString()}
        </div>
      </div>
      
      {/* Placeholder for future Gantt Chart controls (e.g., zoom, workflow selection) */}
      <div className="mb-6 p-3 bg-gray-50 rounded-md shadow-sm flex justify-between items-center">
        <span className="text-gray-700">Workflow: <span className="font-semibold">Demo_CreditApproval_v1.2</span></span>
        <button className="px-3 py-1.5 bg-indigo-600 text-white text-xs font-medium rounded hover:bg-indigo-700">
          Select Workflow
        </button>
      </div>

      {/* Simplified Task List / Gantt Table Placeholder */}
      <div className="overflow-x-auto shadow-lg rounded-lg">
        <table className="min-w-full bg-white">
          <thead className="bg-gray-200 text-gray-700">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider">Task Name</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider">Status</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider">Progress</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider">Start Time</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider">End Time</th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider">Assignee</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {tasks.map(task => (
              <tr key={task.id} className={`hover:bg-gray-50 transition-colors duration-150 ease-in-out ${task.status === 'Failed' ? 'bg-red-50' : ''}`}>
                <td className="px-4 py-3 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{task.name}</div>
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <span className={`px-2.5 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(task.status)}`}>
                    {task.status}
                  </span>
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  {task.progress !== undefined && task.status !== 'Pending' ? (
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                      <div 
                        className={`h-2.5 rounded-full ${task.status === 'Failed' ? 'bg-red-500' : (task.status === 'Completed' ? 'bg-green-500' : 'bg-blue-500')}`}
                        style={{ width: `${task.progress}%` }}
                      ></div>
                    </div>
                  ) : (
                    <span className="text-xs text-gray-500">N/A</span>
                  )}
                  <span className="ml-2 text-xs text-gray-600">{task.progress !== undefined && task.status !== 'Pending' ? `${task.progress}%` : ''}</span>
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-600">{formatDateTime(task.startTime)}</td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-600">{formatDateTime(task.endTime)}</td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-600">{task.assignee || 'N/A'}</td>
              </tr>
            ))}
            {tasks.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                  No tasks currently running or available for this workflow.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ExecutionMonitorScreen; 