'use client';

import React, { useState } from 'react';
import { Task, Column } from '@/types/kanban';
import { KanbanCard } from './KanbanCard';
import { Plus, MoreVertical } from 'lucide-react';
import { cn } from '@/lib/utils';

interface KanbanColumnProps {
  column: Column;
  tasks: Task[];
  stories?: Record<string, { id: string; title: string; storyId: string }>;
  onAddTask?: () => void;
  onTaskMove?: (taskId: string, newStatusId: number, currentStatusId?: number) => void;
  onTaskEdit?: (task: Task) => void;
  onTaskDetail?: (task: Task) => void;
  onTaskDelete?: (taskId: string) => void;
}

export const KanbanColumn: React.FC<KanbanColumnProps> = ({
  column,
  tasks,
  stories = {},
  onAddTask,
  onTaskMove,
  onTaskEdit,
  onTaskDetail,
  onTaskDelete,
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [draggedTask, setDraggedTask] = useState<string | null>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const taskId = e.dataTransfer.getData('text/plain');
    if (taskId && onTaskMove) {
      // Find the task to get its current status ID
      const task = tasks.find(t => t.id === taskId);
      onTaskMove(taskId, column.statusId, task?.statusId);
    }
    setDraggedTask(null);
  };

  const isAtLimit = column.limit && tasks.length >= column.limit;

  // Extract color class name for styling
  const getColumnColorClasses = () => {
    const colorMap: Record<string, { bg: string; border: string; header: string; text: string }> = {
      'bg-gray-400': { 
        bg: 'bg-gray-50', 
        border: 'border-gray-200', 
        header: 'bg-gray-100 border-gray-300',
        text: 'text-gray-700'
      },
      'bg-blue-500': { 
        bg: 'bg-blue-50', 
        border: 'border-blue-200', 
        header: 'bg-blue-100 border-blue-300',
        text: 'text-blue-700'
      },
      'bg-yellow-500': { 
        bg: 'bg-yellow-50', 
        border: 'border-yellow-200', 
        header: 'bg-yellow-100 border-yellow-300',
        text: 'text-yellow-700'
      },
      'bg-purple-500': { 
        bg: 'bg-purple-50', 
        border: 'border-purple-200', 
        header: 'bg-purple-100 border-purple-300',
        text: 'text-purple-700'
      },
      'bg-green-500': { 
        bg: 'bg-green-50', 
        border: 'border-green-200', 
        header: 'bg-green-100 border-green-300',
        text: 'text-green-700'
      },
    };
    return colorMap[column.color] || colorMap['bg-gray-400'];
  };

  const colorClasses = getColumnColorClasses();

  return (
    <div className={cn(
      "flex flex-col h-full rounded-lg p-0 min-w-[300px] max-w-[350px] border-2",
      colorClasses.bg,
      colorClasses.border
    )}>
      {/* Column Header */}
      <div className={cn(
        "flex items-center justify-between mb-4 p-4 rounded-t-lg border-b-2",
        colorClasses.header,
        colorClasses.border
      )}>
        <div className="flex items-center gap-2">
          <div
            className={cn('w-3 h-3 rounded-full', column.color)}
          />
          <h2 className={cn("font-semibold", colorClasses.text)}>{column.title}</h2>
          <span className={cn(
            'px-2 py-1 text-xs rounded-full border',
            isAtLimit 
              ? 'bg-red-100 text-red-700 border-red-300' 
              : `bg-white ${colorClasses.text} ${colorClasses.border}`
          )}>
            {tasks.length}
            {column.limit && `/${column.limit}`}
          </span>
        </div>
        
        <div className="flex items-center gap-1">
          <button
            onClick={onAddTask}
            disabled={!!isAtLimit}
            className={cn(
              'p-1.5 rounded-md transition-colors',
              isAtLimit
                ? 'text-gray-300 cursor-not-allowed'
                : `${colorClasses.text} hover:bg-white hover:bg-opacity-50`
            )}
            title={isAtLimit ? 'Column limit reached' : 'Add new task'}
          >
            <Plus size={16} />
          </button>
          <button className={cn(
            "p-1.5 rounded-md transition-colors hover:bg-white hover:bg-opacity-50",
            colorClasses.text
          )}>
            <MoreVertical size={16} />
          </button>
        </div>
      </div>

      {/* Tasks Container */}
      <div
        className={cn(
          'flex-1 space-y-3 min-h-[200px] max-h-[600px] overflow-y-auto transition-colors rounded-lg p-4 mx-4 mb-4',
          'bg-white bg-opacity-60',
          isDragOver && 'bg-blue-100 border-2 border-dashed border-blue-400'
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {tasks.length === 0 ? (
          <div className="flex items-center justify-center h-32 text-gray-500 text-sm">
            {isDragOver ? 'Drop task here' : 'No tasks yet'}
          </div>
        ) : (
          // Group tasks by story_id
          (() => {
            const groupedTasks = tasks.reduce((groups, task) => {
              const storyId = task.storyId || 'no-story';
              if (!groups[storyId]) {
                groups[storyId] = [];
              }
              groups[storyId].push(task);
              return groups;
            }, {} as Record<string, typeof tasks>);

            return Object.entries(groupedTasks).map(([storyId, storyTasks]) => (
              <div
                key={storyId}
                className="mb-4 p-3 border-2 border-gray-200 rounded-lg bg-gray-50 bg-opacity-50"
              >
                {/* Story Header */}
                <div className="mb-2 pb-2 border-b border-gray-300">
                  <h4 className="text-sm font-medium text-gray-700">
                    {storyId === 'no-story' 
                      ? 'Unassigned Tasks' 
                      : stories[storyId]?.title || `Story: ${stories[storyId]?.storyId || storyId}`
                    }
                  </h4>
                </div>

                {/* Tasks in this story */}
                <div className="space-y-3">
                  {storyTasks.map((task) => (
                    <KanbanCard
                      key={task.id}
                      task={task}
                      onEdit={onTaskEdit}
                      onDetail={onTaskDetail}
                      onDelete={onTaskDelete}
                      isDragging={draggedTask === task.id}
                    />
                  ))}
                </div>
              </div>
            ));
          })()
        )}
      </div>

      {/* Add Task Button */}
      {!isAtLimit && (
        <button
          onClick={onAddTask}
          className={cn(
            "mx-4 mb-4 py-2 text-sm rounded-md transition-colors border-2 border-dashed hover:bg-white hover:bg-opacity-50",
            `${colorClasses.text} ${colorClasses.border} hover:${colorClasses.border.replace('border-', 'border-')}-400`
          )}
        >
          + Add a task
        </button>
      )}
    </div>
  );
};
