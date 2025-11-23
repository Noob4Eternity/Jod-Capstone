"use client";

import React from "react";
import { Task, Priority } from "@/types/kanban";
import { Calendar, Tag, GripVertical } from "lucide-react";
import { cn } from "@/lib/utils";

interface KanbanCardProps {
  task: Task;
  onEdit?: (task: Task) => void;
  onDelete?: (taskId: string) => void;
  onClick?: (task: Task) => void;
  isDragging?: boolean;
}

const getBadgeConfig = (type: "category" | "priority", value: string) => {
  const base = "border rounded-full flex items-center justify-center";

  if (type === "priority") {
    switch (value.toLowerCase()) {
      case "critical":
      case "urgent":
        return {
          className: `${base} border-zinc-500/50 text-zinc-700 bg-zinc-500/10 dark:text-zinc-100 dark:border-zinc-400/50 dark:bg-zinc-400/10`,
        };
      case "high":
        return {
          className: `${base} border-red-500/50 text-red-700 bg-red-500/10 dark:text-red-400 dark:border-red-400/50 dark:bg-red-400/10`,
        };
      case "medium":
        return {
          className: `${base} border-blue-500/50 text-blue-700 bg-blue-500/10 dark:text-blue-400 dark:border-blue-400/50 dark:bg-blue-400/10`,
        };
      case "low":
      default:
        return {
          className: `${base} border-emerald-500/50 text-emerald-700 bg-emerald-500/10 dark:text-emerald-400 dark:border-emerald-400/50 dark:bg-emerald-400/10`,
        };
    }
  }

  if (type === "category") {
    switch (value.toLowerCase()) {
      case "frontend":
        return {
          className: `${base} border-orange-500/50 text-orange-700 bg-orange-500/10 dark:text-orange-400 dark:border-orange-400/50 dark:bg-orange-400/10`,
        };
      case "testing":
      case "qa":
        return {
          className: `${base} border-yellow-500/50 text-yellow-700 bg-yellow-500/10 dark:text-yellow-400 dark:border-yellow-400/50 dark:bg-yellow-400/10`,
        };
    }
  }

  const hash = value.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0);
  const configs = [
    {
      className: `${base} border-violet-500/50 text-violet-700 bg-violet-500/10 dark:text-violet-400 dark:border-violet-400/50 dark:bg-violet-400/10`,
    },
    {
      className: `${base} border-pink-500/50 text-pink-700 bg-pink-500/10 dark:text-pink-400 dark:border-pink-400/50 dark:bg-pink-400/10`,
    },
    {
      className: `${base} border-cyan-500/50 text-cyan-700 bg-cyan-500/10 dark:text-cyan-400 dark:border-cyan-400/50 dark:bg-cyan-400/10`,
    },
    {
      className: `${base} border-indigo-500/50 text-indigo-700 bg-indigo-500/10 dark:text-indigo-400 dark:border-indigo-400/50 dark:bg-indigo-400/10`,
    },
    {
      className: `${base} border-fuchsia-500/50 text-fuchsia-700 bg-fuchsia-500/10 dark:text-fuchsia-400 dark:border-fuchsia-400/50 dark:bg-fuchsia-400/10`,
    },
    {
      className: `${base} border-rose-500/50 text-rose-700 bg-rose-500/10 dark:text-rose-400 dark:border-rose-400/50 dark:bg-rose-400/10`,
    },
  ];
  return configs[hash % configs.length];
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
        "bg-card rounded-lg border border-border/60 shadow-sm hover:shadow-md cursor-pointer relative group overflow-visible",
        isDragging && "opacity-50 rotate-2 scale-95 ring-2 ring-primary/20",
        isOverdue && "border-red-300 bg-red-50/50 dark:bg-red-950/10"
      )}
      onClick={handleCardClick}>
      {/* Drag Handle */}
      <div
        className="drag-handle absolute top-2 right-2 p-1 text-muted-foreground/40 hover:text-foreground hover:bg-secondary rounded cursor-move opacity-0 group-hover:opacity-100 transition-opacity z-0"
        draggable
        onDragStart={handleDragStart}
        title="Drag to move">
        <GripVertical size={14} />
      </div>

      <div className="p-3.5 lg:p-1.5 xl:p-3.5">
        <div className="flex items-start justify-between mb-3 lg:mb-1 xl:mb-3 pr-6">
          <h3 className="font-bold text-foreground text-sm lg:text-[10px] xl:text-sm leading-snug lg:leading-tight transition-colors">
            {task.title}
          </h3>
        </div>

        <div className="flex items-center gap-2 lg:gap-1 xl:gap-2 mb-3 lg:mb-1 xl:mb-3 flex-wrap">
          {/* Priority Badge */}
          {(() => {
            const config = getBadgeConfig("priority", task.priority);
            return (
              <div
                className={cn(
                  "group/badge relative overflow-hidden",
                  "px-2.5 py-0.5 lg:px-2 lg:py-0.5 rounded-full cursor-default",
                  config.className
                )}>
                <span
                  className={cn(
                    "relative z-10 text-[9px] lg:text-[8px] xl:text-[9px] font-bold uppercase tracking-tighter transition-colors duration-300"
                  )}>
                  {task.priority}
                </span>
              </div>
            );
          })()}

          {/* Category Badge */}
          {task.category &&
            (() => {
              const config = getBadgeConfig("category", task.category);
              return (
                <div
                  className={cn(
                    "group/badge relative overflow-hidden",
                    "px-2.5 py-0.5 lg:px-2 lg:py-0.5 rounded-full cursor-default",
                    config.className
                  )}>
                  <span
                    className={cn(
                      "relative z-10 text-[9px] lg:text-[8px] xl:text-[9px] font-bold uppercase tracking-tighter transition-colors duration-300"
                    )}>
                    {task.category}
                  </span>
                </div>
              );
            })()}

          {isOverdue && (
            <span className="px-2 py-0.5 text-[10px] lg:text-[9px] xl:text-[10px] font-bold uppercase tracking-tighter rounded-full bg-red-100 text-red-700 border border-red-200 dark:bg-red-900/30 dark:text-red-300 dark:border-red-800 shadow-sm animate-pulse flex items-center justify-center">
              Overdue
            </span>
          )}
        </div>

        {task.tags && task.tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 lg:gap-0.5 xl:gap-1.5 mb-3 lg:mb-1 xl:mb-3">
            {task.tags.map((tag, index) => (
              <span
                key={index}
                className="inline-flex items-center justify-center px-2 py-0.5 text-[10px] lg:text-[8px] xl:text-[10px] font-medium bg-secondary/50 text-secondary-foreground/90 rounded-full border border-border/40 italic">
                #{tag}
              </span>
            ))}
          </div>
        )}

        <div className="flex items-center justify-between text-[11px] lg:text-[9px] xl:text-[11px] text-muted-foreground pt-3 lg:pt-1.5 xl:pt-3 border-t border-border/40 mt-1">
          <div className="flex items-center gap-3 lg:gap-1.5 xl:gap-3">
            {task.assignee && (
              <div
                className="flex items-center gap-1.5 lg:gap-1 xl:gap-1.5"
                title={`Assigned to ${task.assignee}`}>
                <div className="w-5 h-5 lg:w-4 lg:h-4 xl:w-5 xl:h-5 rounded-full bg-primary/10 text-primary flex items-center justify-center text-[9px] lg:text-[8px] xl:text-[9px] font-black ring-1 ring-primary/20">
                  {task.assignee.charAt(0).toUpperCase()}
                </div>
                <span className="max-w-[80px] lg:max-w-[60px] xl:max-w-[80px] truncate font-medium">
                  {task.assignee}
                </span>
              </div>
            )}
            {task.dueDate && (
              <div
                className={cn(
                  "flex items-center gap-1",
                  isOverdue ? "text-red-600 dark:text-red-400 font-bold" : "font-medium"
                )}>
                <Calendar
                  size={12}
                  className="lg:w-2.5 lg:h-2.5 xl:w-3 xl:h-3"
                />
                <span
                  className={isOverdue ? "underline decoration-red-400/50 underline-offset-2" : ""}>
                  {formatDate(new Date(task.dueDate))}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
