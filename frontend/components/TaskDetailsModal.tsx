'use client';

import React from 'react';
import { Task } from '@/types/kanban';
import { X, Calendar, User, Tag, Clock, AlertCircle, Trash2, Edit } from 'lucide-react';
import { cn } from '@/lib/utils';

interface TaskDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  task: Task | null;
  onEdit?: (task: Task) => void;
  onDelete?: (taskId: string) => void;
}

const priorityColors = {
  low: 'bg-green-100 text-green-800 border-green-300',
  medium: 'bg-blue-100 text-blue-800 border-blue-300',
  high: 'bg-orange-100 text-orange-800 border-orange-300',
  urgent: 'bg-red-100 text-red-800 border-red-300',
};

const priorityIcons = {
  low: '🟢',
  medium: '🔵',
  high: '🟠',
  urgent: '🔴',
};

export const TaskDetailsModal: React.FC<TaskDetailsModalProps> = ({
  isOpen,
  onClose,
  task,
  onEdit,
  onDelete,
}) => {
  if (!isOpen || !task) return null;

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    }).format(date);
  };

  const formatDateTime = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  const isOverdue = task.dueDate && new Date(task.dueDate) < new Date();

  const handleDelete = () => {
    if (confirm('Are you sure you want to delete this task?')) {
      onDelete?.(task.id);
      onClose();
    }
  };

  const handleEdit = () => {
    onEdit?.(task);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-card rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden border border-border">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border bg-secondary/50">
          <div className="flex items-center gap-3 flex-1">
            <span className="text-2xl">{priorityIcons[task.priority]}</span>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-foreground">
                {task.title}
              </h2>
              <p className="text-sm text-muted-foreground mt-1">
                Task ID: {task.id.slice(0, 8)}...
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleEdit}
              className="p-2 text-muted-foreground hover:text-foreground hover:bg-secondary rounded-lg transition-colors"
              title="Edit task"
            >
              <Edit size={20} />
            </button>
            <button
              onClick={handleDelete}
              className="p-2 text-destructive hover:bg-destructive/10 rounded-lg transition-colors"
              title="Delete task"
            >
              <Trash2 size={20} />
            </button>
            <button
              onClick={onClose}
              className="p-2 text-muted-foreground hover:text-foreground hover:bg-secondary rounded-lg transition-colors"
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-180px)]">
          {/* Priority and Status */}
          <div className="flex flex-wrap items-center gap-2 mb-6">
            <span
              className={cn(
                'px-3 py-1.5 text-sm font-medium rounded-lg border',
                priorityColors[task.priority]
              )}
            >
              {task.priority.toUpperCase()} Priority
            </span>
            {isOverdue && (
              <span className="px-3 py-1.5 text-sm font-medium rounded-lg bg-red-100 text-red-800 border border-red-300 flex items-center gap-1">
                <AlertCircle size={14} />
                Overdue
              </span>
            )}
          </div>

          {/* Description */}
          {task.description && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-foreground mb-2 uppercase tracking-wide">
                Description
              </h3>
              <p className="text-foreground leading-relaxed bg-secondary/30 p-4 rounded-lg">
                {task.description}
              </p>
            </div>
          )}

          {/* Details Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* Assignee */}
            {task.assignee && (
              <div className="flex items-start gap-3">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <User size={18} className="text-primary" />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">
                    Assignee
                  </p>
                  <p className="text-sm font-medium text-foreground">
                    {task.assignee}
                  </p>
                </div>
              </div>
            )}

            {/* Due Date */}
            {task.dueDate && (
              <div className="flex items-start gap-3">
                <div className={cn(
                  "p-2 rounded-lg",
                  isOverdue ? "bg-red-100" : "bg-primary/10"
                )}>
                  <Calendar size={18} className={isOverdue ? "text-red-600" : "text-primary"} />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">
                    Due Date
                  </p>
                  <p className={cn(
                    "text-sm font-medium",
                    isOverdue ? "text-red-600" : "text-foreground"
                  )}>
                    {formatDate(new Date(task.dueDate))}
                    {isOverdue && " (Overdue)"}
                  </p>
                </div>
              </div>
            )}

            {/* Created */}
            <div className="flex items-start gap-3">
              <div className="p-2 bg-secondary rounded-lg">
                <Clock size={18} className="text-muted-foreground" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">
                  Created
                </p>
                <p className="text-sm font-medium text-foreground">
                  {formatDateTime(task.createdAt)}
                </p>
              </div>
            </div>

            {/* Updated */}
            <div className="flex items-start gap-3">
              <div className="p-2 bg-secondary rounded-lg">
                <Clock size={18} className="text-muted-foreground" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">
                  Last Updated
                </p>
                <p className="text-sm font-medium text-foreground">
                  {formatDateTime(task.updatedAt)}
                </p>
              </div>
            </div>
          </div>

          {/* Tags */}
          {task.tags && task.tags.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-foreground mb-3 uppercase tracking-wide flex items-center gap-2">
                <Tag size={16} />
                Tags
              </h3>
              <div className="flex flex-wrap gap-2">
                {task.tags.map((tag, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm bg-secondary text-foreground rounded-lg border border-border"
                  >
                    <Tag size={12} />
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Category */}
          {task.category && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-foreground mb-2 uppercase tracking-wide">
                Category
              </h3>
              <span className="inline-block px-3 py-1.5 text-sm bg-accent text-accent-foreground rounded-lg">
                {task.category}
              </span>
            </div>
          )}

          {/* Estimated Hours */}
          {task.estimatedHours && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-foreground mb-2 uppercase tracking-wide">
                Estimated Hours
              </h3>
              <p className="text-foreground">
                <span className="text-2xl font-bold text-primary">{task.estimatedHours}</span>
                <span className="text-muted-foreground ml-2">hours</span>
              </p>
            </div>
          )}

          {/* Acceptance Criteria */}
          {task.acceptanceCriteria && task.acceptanceCriteria.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-foreground mb-3 uppercase tracking-wide">
                Acceptance Criteria
              </h3>
              <ul className="space-y-2">
                {task.acceptanceCriteria.map((criteria, index) => (
                  <li
                    key={index}
                    className="flex items-start gap-3 text-sm text-foreground bg-secondary/30 p-3 rounded-lg"
                  >
                    <span className="text-primary font-bold">{index + 1}.</span>
                    <span>{criteria}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Technical Notes */}
          {task.technicalNotes && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold text-foreground mb-3 uppercase tracking-wide">
                Technical Notes
              </h3>
              <div className="bg-secondary/50 p-4 rounded-lg border border-border">
                <pre className="text-sm text-foreground whitespace-pre-wrap font-mono">
                  {task.technicalNotes}
                </pre>
              </div>
            </div>
          )}

          {/* Dependencies */}
          {task.dependencies && task.dependencies.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-foreground mb-3 uppercase tracking-wide">
                Dependencies
              </h3>
              <ul className="space-y-2">
                {task.dependencies.map((dep, index) => (
                  <li
                    key={index}
                    className="flex items-center gap-2 text-sm text-muted-foreground bg-secondary/30 p-3 rounded-lg"
                  >
                    <AlertCircle size={14} />
                    <span className="font-mono text-xs">{dep}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 p-6 border-t border-border bg-secondary/50">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-secondary rounded-lg transition-colors"
          >
            Close
          </button>
          <button
            onClick={handleEdit}
            className="px-4 py-2 text-sm font-medium bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition-opacity"
          >
            Edit Task
          </button>
        </div>
      </div>
    </div>
  );
};
