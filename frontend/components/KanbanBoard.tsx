'use client';

import React, { useState, useEffect } from 'react';
import { KanbanColumn } from './KanbanColumn';
import { AddTaskModal } from './AddTaskModal';
import { Task, Column, CreateTaskData } from '@/types/kanban';
import { Search, Filter, Settings, Users, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { supabase } from '@/lib/supabase';
import { useKanban } from '@/hooks/useKanban';

const defaultColumns: Column[] = [
  {
    id: 'todo',
    statusId: 1,
    title: 'To Do',
    color: 'bg-blue-500',
    limit: 5,
    orderIndex: 10,
  },
  {
    id: 'in-progress',
    statusId: 2,
    title: 'In Progress',
    color: 'bg-yellow-500',
    limit: 3,
    orderIndex: 20,
  },
  {
    id: 'review',
    statusId: 3,
    title: 'In Review',
    color: 'bg-purple-500',
    orderIndex: 30,
  },
  {
    id: 'done',
    statusId: 4,
    title: 'Done',
    color: 'bg-green-500',
    orderIndex: 40,
  },
];

export const KanbanBoard: React.FC<{ projectId?: string }> = ({ projectId }) => {
  const {
    tasks,
    stories,
    isLoading,
    addTask,
    updateTask,
    deleteTask,
    moveTask,
    getTasksByStatus,
  } = useKanban(projectId);

  const [columns, setColumns] = useState<Column[]>(defaultColumns);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterPriority, setFilterPriority] = useState<string>('all');
  const [projectName, setProjectName] = useState<string>('');

  // Fetch task statuses and project name from database
  useEffect(() => {
    const fetchBoardData = async () => {
      if (!projectId) return;

      try {
        // Fetch task statuses
        const { data: statusData, error: statusError } = await supabase
          .from('task_status')
          .select('id, status_name, order_index')
          .order('order_index');

        if (!statusError && statusData) {
          // Create columns from database statuses
          const dbColumns: Column[] = statusData.map((status, index) => ({
            id: status.status_name.toLowerCase().replace(' ', '-'),
            statusId: status.id,
            title: status.status_name,
            color: getStatusColor(status.status_name),
            orderIndex: status.order_index,
            limit: getStatusLimit(status.status_name),
          }));
          setColumns(dbColumns);
        }

        // Fetch project name
        const { data: projectData, error: projectError } = await supabase
          .from('projects')
          .select('name')
          .eq('id', projectId)
          .single();

        if (!projectError && projectData) {
          setProjectName(projectData.name);
        } else {
          setProjectName(projectId);
        }
      } catch (error) {
        console.error('Error fetching board data:', error);
        setProjectName(projectId || 'Project Board');
      }
    };

    fetchBoardData();
  }, [projectId]);

  // Helper functions
  const getStatusColor = (statusName: string): string => {
    switch (statusName.toLowerCase()) {
      case 'to do': return 'bg-blue-500';
      case 'in progress': return 'bg-yellow-500';
      case 'in review': return 'bg-purple-500';
      case 'done': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusLimit = (statusName: string): number | undefined => {
    switch (statusName.toLowerCase()) {
      case 'to do': return 5;
      case 'in progress': return 3;
      default: return undefined;
    }
  };

  const handleTaskEdit = (task: Task) => {
    setSelectedTask(task);
    // Here you could open an edit modal similar to AddTaskModal
    console.log('Edit task:', task);
  };

  const handleTaskDelete = (taskId: string) => {
    if (confirm('Are you sure you want to delete this task?')) {
      deleteTask(taskId);
    }
  };

  const filteredTasks = tasks.filter(task => {
    const matchesSearch = task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         task.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesPriority = filterPriority === 'all' || task.priority === filterPriority;
    return matchesSearch && matchesPriority;
  });

  const getFilteredTasksByStatus = (statusId: number) => {
    return filteredTasks.filter(task => task.statusId === statusId);
  };

  const totalTasks = tasks.length;
  const completedTasks = tasks.filter(task => task.statusId === 4).length; // Assuming statusId 4 is 'done'
  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-gray-100 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link
              href="/projects"
              className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              <ArrowLeft size={18} />
              <span className="text-sm font-medium">Back to Projects</span>
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {projectName || 'Project Board'}
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                {totalTasks} tasks • {completedTasks} completed • {completionRate}% done
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
              <input
                type="text"
                placeholder="Search tasks..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-64"
              />
            </div>

            {/* Priority Filter */}
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
              <select
                value={filterPriority}
                onChange={(e) => setFilterPriority(e.target.value)}
                className="pl-10 pr-8 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none bg-white"
              >
                <option value="all">All Priorities</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center gap-2">
              <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
                <Users size={18} />
              </button>
              <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
                <Settings size={18} />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Board */}
      <div className="flex-1 overflow-x-auto overflow-y-hidden">
        <div className="flex gap-6 p-6 h-full min-w-max">
          {columns
            .sort((a, b) => a.orderIndex - b.orderIndex)
            .map((column) => (
              <KanbanColumn
                key={column.id}
                column={column}
                tasks={getFilteredTasksByStatus(column.statusId)}
                stories={stories}
                onAddTask={() => setIsAddModalOpen(true)}
                onTaskMove={moveTask}
                onTaskEdit={handleTaskEdit}
                onTaskDelete={handleTaskDelete}
              />
            ))}
        </div>
      </div>

      {/* Add Task Modal */}
      <AddTaskModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onSubmit={addTask}
        availableStatuses={columns}
      />

      {/* AI Assistant Fab (Future Enhancement) */}
      <button
        className="fixed bottom-6 right-6 w-14 h-14 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center"
        title="AI Assistant"
      >
        <svg
          className="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
          />
        </svg>
      </button>
    </div>
  );
};
