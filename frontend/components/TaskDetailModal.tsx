'use client';

import React from 'react';
import { Task, Priority } from '@/types/kanban';
import {
  Calendar,
  User,
  Tag,
  Clock,
  CheckCircle,
  AlertCircle,
  FileText,
  Target,
  Code,
  Link,
  X
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface TaskDetailModalProps {
  task: Task | null;
  isOpen: boolean;
  onClose: () => void;
  onEdit?: (task: Task) => void;
  onDelete?: (taskId: string) => void;
}

const priorityColors = {
  low: 'bg-green-100 text-green-800 border-green-200',
  medium: 'bg-blue-100 text-blue-800 border-blue-200',
  high: 'bg-orange-100 text-orange-800 border-orange-200',
  urgent: 'bg-red-100 text-red-800 border-red-200',
};

const priorityIcons = {
  low: CheckCircle,
  medium: AlertCircle,
  high: AlertCircle,
  urgent: AlertCircle,
};

export const TaskDetailModal: React.FC<TaskDetailModalProps> = ({
  task,
  isOpen,
  onClose,
  onEdit,
  onDelete,
}) => {
  if (!isOpen || !task) return null;

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  const formatShortDate = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    }).format(date);
  };

  const isOverdue = task.dueDate && new Date(task.dueDate) < new Date();
  const PriorityIcon = priorityIcons[task.priority];

  return (
    <div className="fixed inset-0 bg-black/10 backdrop-blur-md flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-start justify-between p-6 border-b border-gray-200">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h2 className="text-2xl font-bold text-gray-900">{task.title}</h2>
              <span
                className={cn(
                  'px-3 py-1 text-sm font-medium rounded-full border flex items-center gap-1',
                  priorityColors[task.priority]
                )}
              >
                <PriorityIcon size={14} />
                {task.priority}
              </span>
              {isOverdue && (
                <span className="px-3 py-1 text-sm font-medium rounded-full bg-red-100 text-red-800 border border-red-200">
                  Overdue
                </span>
              )}
            </div>
            <p className="text-sm text-gray-500">Task ID: {task.taskId}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Description */}
          {task.description && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Description</h3>
              <p className="text-gray-700 whitespace-pre-wrap">{task.description}</p>
            </div>
          )}

          {/* Status and Assignment */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                <span className="text-sm font-medium text-gray-700">Status:</span>
                <span className="text-sm text-gray-900 font-semibold">{task.status}</span>
              </div>

              {task.assignee && (
                <div className="flex items-center gap-2">
                  <User size={16} className="text-gray-500" />
                  <span className="text-sm font-medium text-gray-700">Assignee:</span>
                  <span className="text-sm text-gray-900">{task.assignee}</span>
                </div>
              )}

              {task.category && (
                <div className="flex items-center gap-2">
                  <FileText size={16} className="text-gray-500" />
                  <span className="text-sm font-medium text-gray-700">Category:</span>
                  <span className="text-sm text-gray-900">{task.category}</span>
                </div>
              )}
            </div>

            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Calendar size={16} className="text-gray-500" />
                <span className="text-sm font-medium text-gray-700">Created:</span>
                <span className="text-sm text-gray-900">{formatShortDate(task.createdAt)}</span>
              </div>

              <div className="flex items-center gap-2">
                <Clock size={16} className="text-gray-500" />
                <span className="text-sm font-medium text-gray-700">Updated:</span>
                <span className="text-sm text-gray-900">{formatShortDate(task.updatedAt)}</span>
              </div>

              {task.dueDate && (
                <div className={cn(
                  'flex items-center gap-2',
                  isOverdue && 'text-red-600'
                )}>
                  <Calendar size={16} className={isOverdue ? 'text-red-500' : 'text-gray-500'} />
                  <span className="text-sm font-medium">Due:</span>
                  <span className="text-sm">{formatDate(new Date(task.dueDate))}</span>
                </div>
              )}

              {task.estimatedHours && (
                <div className="flex items-center gap-2">
                  <Clock size={16} className="text-gray-500" />
                  <span className="text-sm font-medium text-gray-700">Estimated:</span>
                  <span className="text-sm text-gray-900">{task.estimatedHours} hours</span>
                </div>
              )}
            </div>
          </div>

          {/* Tags */}
          {task.tags && task.tags.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Tags</h3>
              <div className="flex flex-wrap gap-2">
                {task.tags.map((tag, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center gap-1 px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-full"
                  >
                    <Tag size={12} />
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Acceptance Criteria */}
          {task.acceptanceCriteria && task.acceptanceCriteria.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <Target size={18} className="text-green-600" />
                Acceptance Criteria
              </h3>
              <ul className="space-y-2">
                {task.acceptanceCriteria.map((criteria, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <CheckCircle size={16} className="text-green-600 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-700">{criteria}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Technical Notes */}
          {task.technicalNotes && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <Code size={18} className="text-blue-600" />
                Technical Notes
              </h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-gray-700 whitespace-pre-wrap">{task.technicalNotes}</p>
              </div>
            </div>
          )}

          {/* Dependencies */}
          {task.dependencies && task.dependencies.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <Link size={18} className="text-purple-600" />
                Dependencies
              </h3>
              <div className="space-y-2">
                {task.dependencies.map((dependency, index) => (
                  <li key={index} className="text-gray-700 list-disc list-inside">{dependency}</li>
                ))}
              </div>
            </div>
          )}

          {/* Story Information */}
          {task.storyId && (
            <div className="bg-blue-50 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-blue-900 mb-2">Story Information</h3>
              <p className="text-blue-800">Part of Story ID: {task.storyId}</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50 rounded-b-lg">
          <div className="text-sm text-gray-500">
            Last updated: {formatDate(task.updatedAt)}
          </div>
          <div className="flex items-center gap-3">
            {onEdit && (
              <button
                onClick={() => onEdit(task)}
                className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-colors"
              >
                Edit Task
              </button>
            )}
            {onDelete && (
              <button
                onClick={() => {
                  if (confirm('Are you sure you want to delete this task?')) {
                    onDelete(task.id);
                    onClose();
                  }
                }}
                className="px-4 py-2 text-sm font-medium text-red-600 hover:text-red-800 hover:bg-red-50 rounded-lg transition-colors"
              >
                Delete Task
              </button>
            )}
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};