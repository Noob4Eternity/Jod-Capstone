export interface Task {
  id: string;
  title: string;
  description: string;
  status: string; // Now a string that matches status_name from database
  statusId: number; // The status_id from database
  priority: Priority;
  assignee?: string;
  assigneeId?: string; // UUID of the assigned employee
  createdAt: Date;
  updatedAt: Date;
  dueDate?: Date;
  tags?: string[];
  taskId: string; // The task_id from database
  category?: string;
  estimatedHours?: number;
  acceptanceCriteria?: string[];
  technicalNotes?: string;
  dependencies?: string[];
  storyId?: string; // The story_id from database to group tasks by user story
}

export type Priority = 'low' | 'medium' | 'high' | 'urgent';

export interface Column {
  id: string; // Now matches status_name from database
  statusId: number; // The status_id from database
  title: string;
  color: string;
  limit?: number;
  orderIndex: number; // For sorting columns
}

export interface Board {
  id: string;
  title: string;
  description?: string;
  columns: Column[];
  tasks: Task[];
  createdAt: Date;
  updatedAt: Date;
}

export interface CreateTaskData {
  title: string;
  description: string;
  priority: Priority;
  statusId: number;
  assignee?: string;
  dueDate?: Date;
  tags?: string[];
  category?: string;
  estimatedHours?: number;
  acceptanceCriteria?: string[];
  technicalNotes?: string;
  dependencies?: string[];
}
