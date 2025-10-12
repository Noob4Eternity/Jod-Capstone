"use client";

import React from "react";
import { Task, Priority } from "@/types/kanban";
import { Calendar, User, Tag, GripVertical, Clock } from "lucide-react";
import { cn } from "@/lib/utils";

interface KanbanCardProps {
  task: Task;
  onEdit?: (task: Task) => void;
  onDelete?: (taskId: string) => void;
  onClick?: (task: Task) => void;
  isDragging?: boolean;
}

const priorityColors = {
  low: "bg-green-100 text-green-800 border-green-200",
  medium: "bg-blue-100 text-blue-800 border-blue-200",
  high: "bg-orange-100 text-orange-800 border-orange-200",
  urgent: "bg-red-100 text-red-800 border-red-200",
};

export const KanbanCard: React.FC<KanbanCardProps> = ({
  task,
  onEdit,
  onDelete,
  onClick,
  isDragging = false,
}) => {
  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
    }).format(date);
  };

  const isOverdue = task.dueDate && new Date(task.dueDate) < new Date();

  const handleDragStart = (e: React.DragEvent) => {
    e.dataTransfer.setData("text/plain", task.id);
    e.dataTransfer.effectAllowed = "move";
  };

  const handleCardClick = (e: React.MouseEvent) => {
    // Prevent click event when clicking on the drag handle
    if ((e.target as HTMLElement).closest(".drag-handle")) {
      return;
    }
    onClick?.(task);
  };

  return (
    <div
      className={cn(
        "bg-card rounded-lg border border-border shadow-sm hover:shadow-md transition-all cursor-pointer relative group",
        isDragging && "opacity-50 rotate-2",
        isOverdue && "border-red-300 bg-red-50 dark:bg-red-950/20"
      )}
      onClick={handleCardClick}>
      {/* Drag Handle */}
      <div
        className="drag-handle absolute top-2 right-2 p-1 text-muted-foreground hover:text-foreground hover:bg-secondary rounded cursor-move opacity-0 group-hover:opacity-100 transition-opacity"
        draggable
        onDragStart={handleDragStart}
        title="Drag to move">
        <GripVertical size={16} />
      </div>

      <div className="p-4">
        <div className="flex items-start justify-between mb-2 pr-6">
          <h3 className="font-medium text-foreground text-sm line-clamp-2">{task.title}</h3>
        </div>

        {task.description && (
          <p className="text-muted-foreground text-xs mb-3 line-clamp-2">{task.description}</p>
        )}

        <div className="flex items-center gap-2 mb-3">
          <span
            className={cn(
              "px-2 py-1 text-xs font-medium rounded border",
              priorityColors[task.priority]
            )}>
            {task.priority}
          </span>
          {isOverdue && (
            <span className="px-2 py-1 text-xs font-medium rounded bg-red-100 text-red-800 border border-red-200 dark:bg-red-900/30 dark:text-red-300 dark:border-red-800">
              Overdue
            </span>
          )}
        </div>

        {task.tags && task.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {task.tags.map((tag, index) => (
              <span
                key={index}
                className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-secondary text-muted-foreground rounded">
                <Tag size={10} />
                {tag}
              </span>
            ))}
          </div>
        )}

        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <div className="flex items-center gap-3">
            {task.assignee && (
              <div className="flex items-center gap-1">
                <User size={12} />
                <span>{task.assignee}</span>
              </div>
            )}
            {task.dueDate && (
              <div
                className={cn(
                  "flex items-center gap-1",
                  isOverdue && "text-red-600 dark:text-red-400"
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
    </div>
  );
};
