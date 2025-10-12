"use client";

import React, { useState } from "react";
import { Task, Column } from "@/types/kanban";
import { KanbanCard } from "./KanbanCard";
import { Plus, MoreVertical } from "lucide-react";
import { cn } from "@/lib/utils";

interface KanbanColumnProps {
  column: Column;
  tasks: Task[];
  stories?: Record<string, { id: string; title: string; storyId: string }>;
  onAddTask?: () => void;
  onTaskMove?: (taskId: string, newStatusId: number) => void;
  onTaskEdit?: (task: Task) => void;
  onTaskDelete?: (taskId: string) => void;
  onTaskClick?: (task: Task) => void;
}

export const KanbanColumn: React.FC<KanbanColumnProps> = ({
  column,
  tasks,
  stories = {},
  onAddTask,
  onTaskMove,
  onTaskEdit,
  onTaskDelete,
  onTaskClick,
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [draggedTask, setDraggedTask] = useState<string | null>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);

    const taskId = e.dataTransfer.getData("text/plain");
    if (taskId && onTaskMove) {
      onTaskMove(taskId, column.statusId);
    }
    setDraggedTask(null);
  };

  const isAtLimit = column.limit && tasks.length >= column.limit;

  // Map column color to CSS variable names
  const getColumnStyles = () => {
    const colorKey = column.color;
    return {
      dotColor: `bg-${colorKey}`,
      bgColor: `bg-${colorKey}-bg`,
      borderColor: `border-${colorKey}-border`,
      textColor: `text-${colorKey}`,
      headerBg: `bg-${colorKey}-bg`,
    };
  };

  const styles = getColumnStyles();

  return (
    <div
      className={cn(
        "flex flex-col h-full rounded-lg p-0 min-w-[300px] max-w-[350px] border-2",
        styles.bgColor,
        styles.borderColor
      )}>
      {/* Column Header */}
      <div
        className={cn(
          "flex items-center justify-between mb-4 p-4 rounded-t-lg border-b-2",
          styles.headerBg,
          styles.borderColor
        )}>
        <div className="flex items-center gap-2">
          <div className={cn("w-3 h-3 rounded-full", styles.dotColor)} />
          <h2 className={cn("font-semibold", styles.textColor)}>{column.title}</h2>
          <span
            className={cn(
              "px-2 py-1 text-xs rounded-full border",
              isAtLimit
                ? "bg-red-100 text-red-700 border-red-300"
                : `bg-white ${styles.textColor} ${styles.borderColor}`
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
              "p-1.5 rounded-md transition-colors",
              isAtLimit
                ? "text-gray-300 cursor-not-allowed"
                : `${styles.textColor} hover:bg-white hover:bg-opacity-50`
            )}
            title={isAtLimit ? "Column limit reached" : "Add new task"}>
            <Plus size={16} />
          </button>
          <button
            className={cn(
              "p-1.5 rounded-md transition-colors hover:bg-white hover:bg-opacity-50",
              styles.textColor
            )}>
            <MoreVertical size={16} />
          </button>
        </div>
      </div>

      {/* Tasks Container */}
      <div
        className={cn(
          "flex-1 space-y-3 min-h-[200px] max-h-[600px] overflow-y-auto transition-colors rounded-lg p-4  mb-4",
          "bg-card bg-opacity-60",
          isDragOver && "bg-primary/10 border-2 border-dashed border-primary"
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}>
        {tasks.length === 0 ? (
          <div className="flex items-center justify-center h-32 text-muted-foreground text-sm">
            {isDragOver ? "Drop task here" : "No tasks yet"}
          </div>
        ) : (
          // Group tasks by story_id
          (() => {
            const groupedTasks = tasks.reduce((groups, task) => {
              const storyId = task.storyId || "no-story";
              if (!groups[storyId]) {
                groups[storyId] = [];
              }
              groups[storyId].push(task);
              return groups;
            }, {} as Record<string, typeof tasks>);

            return Object.entries(groupedTasks).map(([storyId, storyTasks]) => (
              <div
                key={storyId}
                className="mb-4 p-3 border-2 border-border rounded-lg bg-card bg-opacity-50">
                {/* Story Header */}
                <div className="mb-2 pb-2 border-b border-border">
                  <h4 className="text-sm font-medium text-foreground">
                    {storyId === "no-story"
                      ? "Unassigned Tasks"
                      : stories[storyId]?.title || `Story: ${stories[storyId]?.storyId || storyId}`}
                  </h4>
                </div>

                {/* Tasks in this story */}
                <div className="space-y-3">
                  {storyTasks.map((task) => (
                    <KanbanCard
                      key={task.id}
                      task={task}
                      onEdit={onTaskEdit}
                      onDelete={onTaskDelete}
                      onClick={onTaskClick}
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
            styles.textColor,
            styles.borderColor
          )}>
          + Add a task
        </button>
      )}
    </div>
  );
};
