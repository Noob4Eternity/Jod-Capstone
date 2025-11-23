"use client";

import React, { useState } from "react";
import { Task, Column } from "@/types/kanban";
import { KanbanCard } from "./KanbanCard";
import { Plus, MoreVertical, ChevronDown, ChevronRight } from "lucide-react";
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
  isWide?: boolean;
  totalTasks?: number;
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
  isWide = false,
  totalTasks = 0,
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [draggedTask, setDraggedTask] = useState<string | null>(null);
  const [collapsedStories, setCollapsedStories] = useState<Set<string>>(new Set());

  const toggleStoryCollapse = (storyId: string) => {
    setCollapsedStories((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(storyId)) {
        newSet.delete(storyId);
      } else {
        newSet.add(storyId);
      }
      return newSet;
    });
  };

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

  // Calculate progress percentage based on total tasks (Distribution)
  const progressPercentage = totalTasks > 0 ? (tasks.length / totalTasks) * 100 : 0;

  return (
    <div
      className={cn(
        "flex flex-col h-full rounded-xl overflow-hidden border border-border/40 shadow-sm group",
        "bg-secondary/20 hover:shadow-md hover:border-border/60"
      )}>
      {/* Glowing Progress Line */}
      <div className="h-1 w-full bg-secondary/50 relative overflow-hidden">
        <div
          className={cn("h-full transition-all duration-500 ease-out", styles.dotColor)}
          style={{
            width: `${progressPercentage}%`,
            boxShadow: `0 0 10px 2px var(--${column.color})`,
          }}
        />
      </div>

      {/* Column Header */}
      <div
        className={cn(
          "flex items-center justify-between px-4 py-3 lg:px-2 lg:py-2 xl:px-4 xl:py-3 border-b border-border/10",
          "bg-background/10 backdrop-blur-sm"
        )}>
        <div className="flex items-center gap-2.5 lg:gap-1.5 xl:gap-2.5">
          <div
            className={cn(
              "w-2.5 h-2.5 lg:w-2 lg:h-2 xl:w-2.5 xl:h-2.5 rounded-full shadow-sm",
              styles.dotColor
            )}
          />
          <h2 className="font-bold text-sm lg:text-[11px] xl:text-sm text-foreground tracking-tight">
            {column.title}
          </h2>
          <span
            className={cn(
              "px-1.5 py-0.5 text-[10px] font-semibold rounded-full bg-secondary text-muted-foreground border border-border/50",
              isAtLimit &&
                "bg-red-100 text-red-700 border-red-200 dark:bg-red-900/30 dark:text-red-300 dark:border-red-800"
            )}>
            {tasks.length}
            <span className="text-muted-foreground/60 mx-0.5">/</span>
            {totalTasks}
          </span>
        </div>

        <div className="flex items-center">
          <button
            onClick={onAddTask}
            disabled={!!isAtLimit}
            className={cn(
              "p-1 rounded-lg transition-all duration-200 text-muted-foreground hover:text-primary hover:bg-primary/10",
              isAtLimit && "opacity-50 cursor-not-allowed"
            )}
            title={isAtLimit ? "Column limit reached" : "Add new task"}>
            <Plus
              size={14}
              className="lg:w-3 lg:h-3 xl:w-3.5 xl:h-3.5"
            />
          </button>
        </div>
      </div>

      {/* Tasks Container */}
      <div
        className={cn(
          "flex-1 overflow-y-auto p-3 lg:p-2 xl:p-3 space-y-3 lg:space-y-2 xl:space-y-3 scrollbar-thin scrollbar-thumb-border scrollbar-track-transparent",
          isDragOver && "bg-primary/5 ring-2 ring-inset ring-primary/20",
          isWide && "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 space-y-0 content-start"
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}>
        {tasks.length === 0 ? (
          <div
            className={cn(
              "flex flex-col items-center justify-center text-muted-foreground/40 text-sm border-2 border-dashed border-border/40 rounded-xl m-1 transition-colors hover:border-primary/20 hover:bg-primary/5",
              isWide ? "h-32 col-span-full" : "h-32"
            )}>
            <p>{isDragOver ? "Drop task here" : "No tasks yet"}</p>
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

            return Object.entries(groupedTasks).map(([storyId, storyTasks]) => {
              const isCollapsed = collapsedStories.has(storyId);
              const taskCount = storyTasks.length;

              if (storyId === "no-story") {
                return (
                  <React.Fragment key={storyId}>
                    {storyTasks.map((task) => (
                      <div
                        key={task.id}
                        className={isWide ? "h-full" : ""}>
                        <KanbanCard
                          task={task}
                          onEdit={onTaskEdit}
                          onDelete={onTaskDelete}
                          onClick={onTaskClick}
                          isDragging={draggedTask === task.id}
                        />
                      </div>
                    ))}
                  </React.Fragment>
                );
              }

              return (
                <div
                  key={storyId}
                  className={cn(
                    "mb-2 border border-border/40 rounded-xl bg-background/40 overflow-hidden shadow-sm",
                    isWide && "col-span-full"
                  )}>
                  {/* Story Header - Clickable */}
                  <button
                    onClick={() => toggleStoryCollapse(storyId)}
                    className="w-full flex items-start justify-between p-3 lg:p-1.5 xl:p-3 hover:bg-secondary/50 transition-colors text-left group gap-4 lg:gap-2 xl:gap-4">
                    <div className="flex items-start gap-2 flex-1 min-w-0">
                      {isCollapsed ? (
                        <ChevronRight
                          size={14}
                          className="text-muted-foreground shrink-0 group-hover:text-foreground transition-colors mt-1"
                        />
                      ) : (
                        <ChevronDown
                          size={14}
                          className="text-muted-foreground shrink-0 group-hover:text-foreground transition-colors mt-1"
                        />
                      )}
                      <h4 className="text-sm lg:text-xs xl:text-sm font-bold text-muted-foreground group-hover:text-foreground transition-colors break-words leading-snug">
                        {stories[storyId]?.title ||
                          `Story: ${stories[storyId]?.storyId || storyId}`}
                      </h4>
                    </div>
                    <span className="text-[10px] font-bold text-muted-foreground/70 bg-secondary/40 backdrop-blur-sm px-2 py-1 rounded-full shrink-0 border border-border/30 mt-0.5">
                      {taskCount}
                    </span>
                  </button>

                  {/* Tasks in this story - Collapsible with smooth animation */}
                  <div
                    className={cn(
                      "grid transition-all duration-300 ease-in-out",
                      isCollapsed ? "grid-rows-[0fr] opacity-0" : "grid-rows-[1fr] opacity-100"
                    )}>
                    <div className="overflow-hidden">
                      <div
                        className={cn(
                          "p-3 pt-0",
                          isWide
                            ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3"
                            : "space-y-2"
                        )}>
                        <div className={isWide ? "hidden" : "h-1"}></div>
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
                  </div>
                </div>
              );
            });
          })()
        )}
      </div>

      {/* Add Task Button */}
      {!isAtLimit && (
        <div className="p-3 pt-0">
          <button
            onClick={onAddTask}
            className={cn(
              "w-full py-2 text-xs font-semibold rounded-lg transition-all duration-200",
              "text-muted-foreground hover:text-primary hover:bg-primary/5 border border-transparent hover:border-primary/20",
              "flex items-center justify-center gap-2 group"
            )}>
            <div className="p-0.5 rounded-md bg-secondary group-hover:bg-primary/20 transition-colors">
              <Plus size={12} />
            </div>
            Add New Task
          </button>
        </div>
      )}
    </div>
  );
};
