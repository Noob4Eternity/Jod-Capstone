'use client';

import { useState, useCallback, useEffect } from 'react';
import { Task, Priority, CreateTaskData } from '@/types/kanban';
import { supabase } from '@/lib/supabase';

export const useKanban = (projectId?: string) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [stories, setStories] = useState<Record<string, { id: string; title: string; storyId: string }>>({});
  const [isLoading, setIsLoading] = useState(true);

  // Fetch tasks from database
  useEffect(() => {
    const fetchTasks = async () => {
      if (!projectId) {
        setTasks([]);
        setIsLoading(false);
        return;
      }

      try {
        // First get ALL story_ids for this project
        const { data: storiesData, error: storiesError } = await supabase
          .from('user_stories')
          .select('id, title, story_id')
          .eq('project_id', projectId);

        if (storiesError || !storiesData || storiesData.length === 0) {
          console.error('Error finding stories for project:', storiesError);
          console.log('No stories found for project:', projectId);
          setTasks([]);
          setIsLoading(false);
          return;
        }

        console.log(`Found ${storiesData.length} stories for project ${projectId}:`, storiesData.map(s => s.id));

        // Store story information for display
        const storyMap: Record<string, { id: string; title: string; storyId: string }> = {};
        storiesData.forEach(story => {
          storyMap[story.id] = {
            id: story.id,
            title: story.title || `Story ${story.id}`,
            storyId: story.story_id || story.id
          };
        });
        setStories(storyMap);

        // Get all story IDs
        const storyIds = storiesData.map(story => story.id);

        // Fetch tasks for ALL stories in this project
        const { data: tasksData, error: tasksError } = await supabase
          .from('tasks')
          .select(`
            id,
            task_id,
            title,
            description,
            category,
            estimated_hours,
            priority,
            acceptance_criteria,
            technical_notes,
            dependencies,
            created_at,
            status_id,
            story_id,
            assignee_id,
            task_status (
              id,
              status_name
            ),
            employees (
              full_name
            )
          `)
          .in('story_id', storyIds);

        if (!tasksError && tasksData) {
          console.log(`Fetched ${tasksData.length} tasks for project ${projectId}`);
          console.log('Tasks data:', tasksData);

          // Transform tasks to match our interface
          const transformedTasks: Task[] = tasksData.map((task: any) => ({
            id: task.id,
            taskId: task.task_id,
            title: task.title,
            description: task.description || '',
            status: task.task_status?.status_name || 'To Do',
            statusId: task.status_id || 1,
            priority: (task.priority as any) || 'medium',
            category: task.category,
            estimatedHours: task.estimated_hours,
            acceptanceCriteria: task.acceptance_criteria || [],
            technicalNotes: task.technical_notes,
            dependencies: task.dependencies || [],
            createdAt: new Date(task.created_at),
            updatedAt: new Date(task.created_at),
            storyId: task.story_id,
            assigneeId: task.assignee_id,
            assignee: task.employees?.full_name || undefined,
          }));

          console.log(`Transformed ${transformedTasks.length} tasks`);
          setTasks(transformedTasks);
        } else {
          console.error('Error fetching tasks:', tasksError);
          setTasks([]);
        }
      } catch (error) {
        console.error('Error fetching tasks:', error);
        setTasks([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchTasks();
  }, [projectId]);

  const addTask = useCallback(async (taskData: CreateTaskData) => {
    try {
      // First, get the story_id for this project (use the first one, or create one if none exists)
      const { data: storiesData, error: storiesError } = await supabase
        .from('user_stories')
        .select('id')
        .eq('project_id', projectId)
        .limit(1);

      let storyId: string;

      if (storiesError) {
        console.error('Error finding stories for project:', storiesError);
        return;
      }

      if (!storiesData || storiesData.length === 0) {
        // No stories exist for this project, create a default one
        const { data: newStory, error: createError } = await supabase
          .from('user_stories')
          .insert({
            project_id: projectId,
            title: 'Default Story',
            description: 'Default user story for tasks',
            story_id: `STORY-${Date.now()}`,
          })
          .select('id, title, story_id')
          .single();

        if (createError || !newStory) {
          console.error('Error creating default story:', createError);
          return;
        }

        storyId = newStory.id;
        // Add the new story to the stories state
        setStories(prev => ({
          ...prev,
          [newStory.id]: {
            id: newStory.id,
            title: 'Default Story',
            storyId: newStory.story_id || newStory.id
          }
        }));
      } else {
        storyId = storiesData[0].id;
      }

      // Generate a unique task_id
      const taskId = `TASK-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

      const newTask = {
        task_id: taskId,
        title: taskData.title,
        description: taskData.description,
        category: taskData.category,
        estimated_hours: taskData.estimatedHours,
        priority: taskData.priority,
        acceptance_criteria: taskData.acceptanceCriteria,
        technical_notes: taskData.technicalNotes,
        dependencies: taskData.dependencies,
        story_id: storyId,
        status_id: taskData.statusId,
      };

      const { data, error } = await supabase
        .from('tasks')
        .insert(newTask)
        .select(`
          id,
          task_id,
          title,
          description,
          category,
          estimated_hours,
          priority,
          acceptance_criteria,
          technical_notes,
          dependencies,
          created_at,
          status_id,
          assignee_id,
          task_status (
            id,
            status_name
          ),
          employees (
            full_name
          )
        `)
        .single();

      if (!error && data) {
        const transformedTask: Task = {
          id: data.id,
          taskId: data.task_id,
          title: data.title,
          description: data.description || '',
          status: (data.task_status as any)?.status_name || 'To Do',
          statusId: data.status_id || 1,
          priority: (data.priority as any) || 'medium',
          category: data.category,
          estimatedHours: data.estimated_hours,
          acceptanceCriteria: data.acceptance_criteria || [],
          technicalNotes: data.technical_notes,
          dependencies: data.dependencies || [],
          createdAt: new Date(data.created_at),
          updatedAt: new Date(data.created_at),
          assigneeId: data.assignee_id,
          assignee: (data.employees as any)?.full_name || undefined,
        };

        setTasks(prev => [...prev, transformedTask]);
      } else {
        console.error('Error adding task:', error);
      }
    } catch (error) {
      console.error('Error adding task:', error);
    }
  }, [projectId]);

  const updateTask = useCallback(async (taskId: string, updates: Partial<Task>) => {
    try {
      const updateData: any = {};

      if (updates.title !== undefined) updateData.title = updates.title;
      if (updates.description !== undefined) updateData.description = updates.description;
      if (updates.category !== undefined) updateData.category = updates.category;
      if (updates.estimatedHours !== undefined) updateData.estimated_hours = updates.estimatedHours;
      if (updates.priority !== undefined) updateData.priority = updates.priority;
      if (updates.acceptanceCriteria !== undefined) updateData.acceptance_criteria = updates.acceptanceCriteria;
      if (updates.technicalNotes !== undefined) updateData.technical_notes = updates.technicalNotes;
      if (updates.dependencies !== undefined) updateData.dependencies = updates.dependencies;
      if (updates.statusId !== undefined) updateData.status_id = updates.statusId;
      if (updates.assigneeId !== undefined) updateData.assignee_id = updates.assigneeId;

      const { data, error } = await supabase
        .from('tasks')
        .update(updateData)
        .eq('id', taskId)
        .select(`
          id,
          task_id,
          title,
          description,
          category,
          estimated_hours,
          priority,
          acceptance_criteria,
          technical_notes,
          dependencies,
          created_at,
          status_id,
          assignee_id,
          task_status (
            id,
            status_name
          ),
          employees (
            full_name
          )
        `)
        .single();

      if (!error && data) {
        const updatedTask: Task = {
          id: data.id,
          taskId: data.task_id,
          title: data.title,
          description: data.description || '',
          status: (data.task_status as any)?.status_name || 'To Do',
          statusId: data.status_id || 1,
          priority: (data.priority as any) || 'medium',
          category: data.category,
          estimatedHours: data.estimated_hours,
          acceptanceCriteria: data.acceptance_criteria || [],
          technicalNotes: data.technical_notes,
          dependencies: data.dependencies || [],
          createdAt: new Date(data.created_at),
          updatedAt: new Date(data.created_at),
          assigneeId: data.assignee_id,
          assignee: (data.employees as any)?.full_name || undefined,
        };

        setTasks(prev => prev.map(task => task.id === taskId ? updatedTask : task));
      } else {
        console.error('Error updating task:', error);
      }
    } catch (error) {
      console.error('Error updating task:', error);
    }
  }, []);

  const deleteTask = useCallback(async (taskId: string) => {
    try {
      const { error } = await supabase
        .from('tasks')
        .delete()
        .eq('id', taskId);

      if (!error) {
        setTasks(prev => prev.filter(task => task.id !== taskId));
      } else {
        console.error('Error deleting task:', error);
      }
    } catch (error) {
      console.error('Error deleting task:', error);
    }
  }, []);

  const moveTask = useCallback(async (taskId: string, newStatusId: number, currentStatusId?: number) => {
    try {
      // Get the current user's ID
      const { data: { user } } = await supabase.auth.getUser();
      
      if (!user) {
        throw new Error('User not authenticated');
      }
      
      // Get the current task to check its current status
      const currentTask = tasks.find(t => t.id === taskId);
      const currentStatus = currentStatusId || currentTask?.statusId || 1;
      
      // Fetch user's role from employees table
      const { data: employeeData, error: employeeError } = await supabase
        .from('employees')
        .select('role_id, roles(id, role_name)')
        .eq('id', user.id)
        .single();
      
      if (employeeError) {
        console.warn('Could not fetch employee role:', employeeError);
      }
      
      const userRole = (employeeData?.roles as any)?.role_name?.toLowerCase() || 'developer';
      
      // Role-based permission checks
      // Status IDs: 1=To Do, 2=In Progress, 3=In Review, 4=Done/Completed
      
      // Admins can do anything - skip all permission checks
      if (userRole === 'admin') {
        console.log('[PERMISSIONS] Admin user - all actions allowed');
      } else {
        // Only Project Managers and Admins can move tasks FROM "In Review" (status 3)
        if (currentStatus === 3 && userRole !== 'project_manager') {
          throw new Error('Only project managers and admins can move tasks from "In Review" status');
        }
        
        // Only Project Managers and Admins can move tasks TO "Done/Completed" (status 4)
        if (newStatusId === 4 && userRole !== 'project_manager') {
          throw new Error('Only project managers and admins can mark tasks as completed');
        }
        
        // Developers can move To Do (1) → In Progress (2)
        // Developers can move In Progress (2) → In Review (3) [though this usually happens via PR]
        if (userRole === 'developer' && ![1, 2, 3].includes(newStatusId)) {
          throw new Error('Developers can only move tasks through To Do, In Progress, and In Review statuses');
        }
      }
      
      const updateData: any = { status_id: newStatusId };
      
      // If moving to "In Progress" (statusId 2), assign to current user
      if (newStatusId === 2 && user) {
        updateData.assignee_id = user.id;
      }

      const { data, error } = await supabase
        .from('tasks')
        .update(updateData)
        .eq('id', taskId)
        .select(`
          id,
          task_id,
          status_id,
          assignee_id,
          task_status (
            status_name
          ),
          employees (
            full_name
          )
        `)
        .single();

      if (!error && data) {
        setTasks(prev => prev.map(task =>
          task.id === taskId
            ? { 
                ...task, 
                statusId: newStatusId,
                status: (data.task_status as any)?.status_name || task.status,
                assigneeId: data.assignee_id,
                assignee: (data.employees as any)?.full_name || task.assignee
              }
            : task
        ));
      } else {
        console.error('Error moving task:', error);
      }
    } catch (error) {
      console.error('Error moving task:', error);
    }
  }, []);

  const getTasksByStatus = useCallback((statusId: number) => {
    return tasks.filter(task => task.statusId === statusId);
  }, [tasks]);

  return {
    tasks,
    stories,
    isLoading,
    addTask,
    updateTask,
    deleteTask,
    moveTask,
    getTasksByStatus,
  };
};
