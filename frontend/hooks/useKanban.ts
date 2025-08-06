'use client';

import { useState, useCallback } from 'react';
import { Task, TaskStatus, Priority, CreateTaskData } from '@/types/kanban';

export const useKanban = () => {
  const [tasks, setTasks] = useState<Task[]>([
    {
      id: '1',
      title: 'Setup project structure',
      description: 'Create the basic folder structure and configuration files',
      status: 'done',
      priority: 'high',
      assignee: 'John Doe',
      createdAt: new Date('2024-01-01'),
      updatedAt: new Date('2024-01-02'),
      tags: ['setup', 'infrastructure']
    },
    {
      id: '2',
      title: 'Design Kanban UI',
      description: 'Create wireframes and mockups for the Kanban board interface',
      status: 'in-progress',
      priority: 'medium',
      assignee: 'Jane Smith',
      createdAt: new Date('2024-01-02'),
      updatedAt: new Date('2024-01-03'),
      tags: ['design', 'ui']
    },
    {
      id: '3',
      title: 'Implement drag and drop',
      description: 'Add drag and drop functionality to move tasks between columns',
      status: 'todo',
      priority: 'high',
      createdAt: new Date('2024-01-03'),
      updatedAt: new Date('2024-01-03'),
      tags: ['feature', 'interaction']
    },
    {
      id: '4',
      title: 'Add AI agent integration',
      description: 'Connect with AI agents for automated task management',
      status: 'backlog',
      priority: 'urgent',
      createdAt: new Date('2024-01-04'),
      updatedAt: new Date('2024-01-04'),
      tags: ['ai', 'integration']
    }
  ]);

  const addTask = useCallback((taskData: CreateTaskData) => {
    const newTask: Task = {
      id: Date.now().toString(),
      ...taskData,
      status: 'todo',
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    setTasks(prev => [...prev, newTask]);
  }, []);

  const updateTask = useCallback((taskId: string, updates: Partial<Task>) => {
    setTasks(prev =>
      prev.map(task =>
        task.id === taskId
          ? { ...task, ...updates, updatedAt: new Date() }
          : task
      )
    );
  }, []);

  const deleteTask = useCallback((taskId: string) => {
    setTasks(prev => prev.filter(task => task.id !== taskId));
  }, []);

  const moveTask = useCallback((taskId: string, newStatus: TaskStatus) => {
    updateTask(taskId, { status: newStatus });
  }, [updateTask]);

  const getTasksByStatus = useCallback((status: TaskStatus) => {
    return tasks.filter(task => task.status === status);
  }, [tasks]);

  return {
    tasks,
    addTask,
    updateTask,
    deleteTask,
    moveTask,
    getTasksByStatus,
  };
};
