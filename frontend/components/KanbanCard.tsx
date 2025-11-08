'use client';

import React from 'react';
import { Task, Priority } from '@/types/kanban';
import { Calendar, User, Tag, MoreHorizontal, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';

interface KanbanCardProps {
  task: Task;
  onEdit?: (task: Task) => void;
  onDetail?: (task: Task) => void;
  onDelete?: (taskId: string) => void;
  isDragging?: boolean;
}

const priorityColors = {
  low: 'bg-green-100 text-green-800 border-green-200',
  medium: 'bg-blue-100 text-blue-800 border-blue-200',
  high: 'bg-orange-100 text-orange-800 border-orange-200',
  urgent: 'bg-red-100 text-red-800 border-red-200',
};

export const KanbanCard: React.FC<KanbanCardProps> = ({
  task,
  onEdit,
  onDetail,
  onDelete,
  isDragging = false,
}) => {
  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
    }).format(date);
  };

  const isOverdue = task.dueDate && new Date(task.dueDate) < new Date();

  return (
    <div
      className={cn(
        'bg-white rounded-lg border border-gray-200 p-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer',
        isDragging && 'opacity-50 rotate-2',
        isOverdue && 'border-red-300 bg-red-50'
      )}
      draggable
      onClick={() => onDetail?.(task)}
      onDragStart={(e) => {
        e.dataTransfer.setData('text/plain', task.id);
        e.dataTransfer.effectAllowed = 'move';
      }}
    >
      <div className="flex items-start justify-between mb-2">
        <h3 className="font-medium text-gray-900 text-sm line-clamp-2">
          {task.title}
        </h3>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onEdit?.(task);
          }}
          className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
        >
          <MoreHorizontal size={14} />
        </button>
      </div>

      {task.description && (
        <p className="text-gray-600 text-xs mb-3 line-clamp-2">
          {task.description}
        </p>
      )}

      <div className="flex items-center gap-2 mb-3">
        <span
          className={cn(
            'px-2 py-1 text-xs font-medium rounded border',
            priorityColors[task.priority]
          )}
        >
          {task.priority}
        </span>
        {isOverdue && (
          <span className="px-2 py-1 text-xs font-medium rounded bg-red-100 text-red-800 border border-red-200">
            Overdue
          </span>
        )}
      </div>

      {task.tags && task.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {task.tags.map((tag, index) => (
            <span
              key={index}
              className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded"
            >
              <Tag size={10} />
              {tag}
            </span>
          ))}
        </div>
      )}

      <div className="flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center gap-3">
          {task.assignee && (
            <div className="flex items-center gap-1">
              <User size={12} />
              <span>{task.assignee}</span>
            </div>
          )}
          {task.dueDate && (
            <div className={cn(
              'flex items-center gap-1',
              isOverdue && 'text-red-600'
            )}>
              <Calendar size={12} />
              <span>{formatDate(new Date(task.dueDate))}</span>
            </div>
          )}
        </div>
        <div className="flex items-center gap-1">
          <Clock size={12} />
          <span>{formatDate(task.updatedAt)}</span>
        </div>
      </div>
    </div>
  );
};
