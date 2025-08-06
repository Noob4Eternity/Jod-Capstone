export interface Task {
  id: string;
  title: string;
  description: string;
  status: TaskStatus;
  priority: Priority;
  assignee?: string;
  createdAt: Date;
  updatedAt: Date;
  dueDate?: Date;
  tags?: string[];
}

export type TaskStatus = 'backlog' | 'todo' | 'in-progress' | 'review' | 'done';

export type Priority = 'low' | 'medium' | 'high' | 'urgent';

export interface Column {
  id: TaskStatus;
  title: string;
  color: string;
  limit?: number;
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
  assignee?: string;
  dueDate?: Date;
  tags?: string[];
}
