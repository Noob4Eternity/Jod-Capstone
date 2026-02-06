"use client";

import React, { useState, useEffect } from "react";
import { KanbanColumn } from "./KanbanColumn";
import { AddTaskModal } from "./AddTaskModal";
import { TaskDetailsModal } from "./TaskDetailsModal";
import { Task, Column, CreateTaskData } from "@/types/kanban";
import { Search, Filter, ArrowLeft, Sun, Moon, ChevronDown, Check } from "lucide-react";
import Link from "next/link";
import { supabase } from "@/lib/supabase";
import { useKanban } from "@/hooks/useKanban";
import { useTheme } from "next-themes";
import { cn } from "@/lib/utils";

const defaultColumns: Column[] = [
  {
    id: "todo",
    statusId: 1,
    title: "To Do",
    color: "kanban-todo",
    limit: 5,
    orderIndex: 10,
  },
  {
    id: "in-progress",
    statusId: 2,
    title: "In Progress",
    color: "kanban-in-progress",
    limit: 3,
    orderIndex: 20,
  },
  {
    id: "review",
    statusId: 3,
    title: "In Review",
    color: "kanban-review",
    orderIndex: 30,
  },
  {
    id: "done",
    statusId: 4,
    title: "Done",
    color: "kanban-done",
    orderIndex: 40,
  },
];

export const KanbanBoard: React.FC<{ projectId?: string }> = ({ projectId }) => {
  const { tasks, stories, isLoading, addTask, updateTask, deleteTask, moveTask, getTasksByStatus } =
    useKanban(projectId);
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  const [columns, setColumns] = useState<Column[]>(defaultColumns);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterPriority, setFilterPriority] = useState<string[]>([]);
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [filterCategory, setFilterCategory] = useState<string[]>([]);
  const [isCategoryFilterOpen, setIsCategoryFilterOpen] = useState(false);
  const [projectName, setProjectName] = useState<string>("");

  useEffect(() => {
    setMounted(true);
  }, []);

  // Close filter dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (!target.closest(".filter-dropdown-container")) {
        setIsFilterOpen(false);
      }
      if (!target.closest(".category-filter-dropdown-container")) {
        setIsCategoryFilterOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Fetch task statuses and project name from database
  useEffect(() => {
    const fetchBoardData = async () => {
      if (!projectId) return;

      try {
        // Fetch task statuses
        const { data: statusData, error: statusError } = await supabase
          .from("task_status")
          .select("id, status_name, order_index")
          .order("order_index");

        if (!statusError && statusData) {
          // Create columns from database statuses
          const dbColumns: Column[] = statusData.map((status, index) => ({
            id: status.status_name.toLowerCase().replace(" ", "-"),
            statusId: status.id,
            title: status.status_name,
            color: getStatusColor(status.status_name),
            orderIndex: status.order_index,
            limit: getStatusLimit(status.status_name),
          }));
          setColumns(dbColumns);
        }

        // Fetch project name
        const { data: projectData, error: projectError } = await supabase
          .from("projects")
          .select("name")
          .eq("id", projectId)
          .single();

        if (!projectError && projectData) {
          setProjectName(projectData.name);
        } else {
          setProjectName(projectId);
        }
      } catch (error) {
        console.error("Error fetching board data:", error);
        setProjectName(projectId || "Project Board");
      }
    };

    fetchBoardData();
  }, [projectId]);

  // Helper functions
  const getPriorityBadgeStyle = (priority: string) => {
    const base =
      "px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-tighter border flex items-center justify-center";
    switch (priority.toLowerCase()) {
      case "urgent":
      case "critical":
        return `${base} border-zinc-500/50 text-zinc-700 bg-zinc-500/10 dark:text-zinc-100 dark:border-zinc-400/50 dark:bg-zinc-400/10`;
      case "high":
        return `${base} border-red-500/50 text-red-700 bg-red-500/10 dark:text-red-400 dark:border-red-400/50 dark:bg-red-400/10`;
      case "medium":
        return `${base} border-blue-500/50 text-blue-700 bg-blue-500/10 dark:text-blue-400 dark:border-blue-400/50 dark:bg-blue-400/10`;
      case "low":
        return `${base} border-emerald-500/50 text-emerald-700 bg-emerald-500/10 dark:text-emerald-400 dark:border-emerald-400/50 dark:bg-emerald-400/10`;
      default:
        return base;
    }
  };

  const getCategoryBadgeStyle = (category: string) => {
    const base =
      "px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-tighter border flex items-center justify-center";
    switch (category.toLowerCase()) {
      case "frontend":
        return `${base} border-orange-500/50 text-orange-700 bg-orange-500/10 dark:text-orange-400 dark:border-orange-400/50 dark:bg-orange-400/10`;
      case "testing":
      case "qa":
        return `${base} border-yellow-500/50 text-yellow-700 bg-yellow-500/10 dark:text-yellow-400 dark:border-yellow-400/50 dark:bg-yellow-400/10`;
      default:
        // Generate consistent color based on string hash
        const hash = category.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0);
        const colors = [
          {
            border: "border-violet-500/50",
            text: "text-violet-700",
            bg: "bg-violet-500/10",
            darkText: "dark:text-violet-400",
            darkBorder: "dark:border-violet-400/50",
            darkBg: "dark:bg-violet-400/10",
          },
          {
            border: "border-pink-500/50",
            text: "text-pink-700",
            bg: "bg-pink-500/10",
            darkText: "dark:text-pink-400",
            darkBorder: "dark:border-pink-400/50",
            darkBg: "dark:bg-pink-400/10",
          },
          {
            border: "border-cyan-500/50",
            text: "text-cyan-700",
            bg: "bg-cyan-500/10",
            darkText: "dark:text-cyan-400",
            darkBorder: "dark:border-cyan-400/50",
            darkBg: "dark:bg-cyan-400/10",
          },
          {
            border: "border-indigo-500/50",
            text: "text-indigo-700",
            bg: "bg-indigo-500/10",
            darkText: "dark:text-indigo-400",
            darkBorder: "dark:border-indigo-400/50",
            darkBg: "dark:bg-indigo-400/10",
          },
          {
            border: "border-fuchsia-500/50",
            text: "text-fuchsia-700",
            bg: "bg-fuchsia-500/10",
            darkText: "dark:text-fuchsia-400",
            darkBorder: "dark:border-fuchsia-400/50",
            darkBg: "dark:bg-fuchsia-400/10",
          },
          {
            border: "border-rose-500/50",
            text: "text-rose-700",
            bg: "bg-rose-500/10",
            darkText: "dark:text-rose-400",
            darkBorder: "dark:border-rose-400/50",
            darkBg: "dark:bg-rose-400/10",
          },
        ];
        const color = colors[hash % colors.length];
        return `${base} ${color.border} ${color.text} ${color.bg} ${color.darkText} ${color.darkBorder} ${color.darkBg}`;
    }
  };

  const getStatusColor = (statusName: string): string => {
    switch (statusName.toLowerCase()) {
      case "to do":
        return "kanban-todo";
      case "in progress":
        return "kanban-in-progress";
      case "in review":
        return "kanban-review";
      case "done":
        return "kanban-done";
      default:
        return "gray-500";
    }
  };

  const getStatusLimit = (statusName: string): number | undefined => {
    switch (statusName.toLowerCase()) {
      case "to do":
        return 5;
      case "in progress":
        return 3;
      default:
        return undefined;
    }
  };

  const handleTaskEdit = (task: Task) => {
    setSelectedTask(task);
    setIsDetailsModalOpen(false);
    // Here you could open an edit modal similar to AddTaskModal
    console.log("Edit task:", task);
  };

  const handleTaskDelete = (taskId: string) => {
    if (confirm("Are you sure you want to delete this task?")) {
      deleteTask(taskId);
    }
  };

  const handleTaskClick = (task: Task) => {
    setSelectedTask(task);
    setIsDetailsModalOpen(true);
  };

  const uniqueCategories = Array.from(
    new Set(tasks.map((t) => t.category).filter(Boolean))
  ) as string[];

  const togglePriority = (priority: string) => {
    setFilterPriority((prev) =>
      prev.includes(priority) ? prev.filter((p) => p !== priority) : [...prev, priority]
    );
  };

  const toggleCategory = (category: string) => {
    setFilterCategory((prev) =>
      prev.includes(category) ? prev.filter((c) => c !== category) : [...prev, category]
    );
  };

  const filteredTasks = tasks.filter((task) => {
    const matchesSearch =
      task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesPriority = filterPriority.length === 0 || filterPriority.includes(task.priority);
    const matchesCategory =
      filterCategory.length === 0 || (task.category && filterCategory.includes(task.category));
    return matchesSearch && matchesPriority && matchesCategory;
  });

  const getFilteredTasksByStatus = (statusId: number) => {
    return filteredTasks.filter((task) => task.statusId === statusId);
  };

  const totalTasks = tasks.length;
  const completedTasks = tasks.filter((task) => task.statusId === 4).length; // Assuming statusId 4 is 'done'
  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center w-screen h-screen bg-background">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-background flex flex-col overflow-hidden">
      {/* Header */}
      <div className="bg-background/80 backdrop-blur-md border-b border-border/50 px-6 py-3 shrink-0 z-10">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex flex-col gap-0.5">
            <Link
              href="/projects"
              className="inline-flex items-center gap-1.5 text-muted-foreground hover:text-primary transition-colors w-fit group mb-1">
              <div className="p-0.5 rounded-md bg-secondary/50 group-hover:bg-primary/10 transition-colors">
                <ArrowLeft size={14} />
              </div>
              <span className="text-xs font-medium">Back to Projects</span>
            </Link>

            <div className="flex items-center gap-3">
              <h1 className="text-xl font-bold text-foreground tracking-tight">
                {projectName || "Project Board"}
              </h1>
              <div className="flex items-center gap-1.5 text-[10px] font-medium text-muted-foreground bg-secondary/50 px-2 py-0.5 rounded-full border border-border/50">
                <span className="text-primary">{totalTasks} tasks</span>
                <span className="w-0.5 h-0.5 rounded-full bg-border"></span>
                <span className="text-green-600 dark:text-green-400">
                  {completedTasks} completed
                </span>
                <span className="w-0.5 h-0.5 rounded-full bg-border"></span>
                <span>{completionRate}% done</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Search */}
            <div className="relative group">
              <Search
                className="absolute left-2.5 top-1/2 transform -translate-y-1/2 text-muted-foreground group-focus-within:text-primary transition-colors"
                size={14}
              />
              <input
                type="text"
                placeholder="Search tasks..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8 pr-3 py-1.5 border border-border/60 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary/50 bg-secondary/30 hover:bg-secondary/50 focus:bg-background text-foreground w-48 text-xs transition-all duration-200"
              />
            </div>

            {/* Priority Filter */}
            <div className="relative filter-dropdown-container">
              <button
                onClick={() => setIsFilterOpen(!isFilterOpen)}
                className={cn(
                  "flex items-center gap-1.5 pl-2.5 pr-2.5 py-1.5 border rounded-lg text-xs transition-all duration-200 min-w-[110px] relative",
                  isFilterOpen
                    ? "border-primary/50 bg-background ring-2 ring-primary/20"
                    : "border-border/60 bg-secondary/30 hover:bg-secondary/50"
                )}>
                <Filter
                  className={cn(
                    "transition-colors",
                    isFilterOpen ? "text-primary" : "text-muted-foreground"
                  )}
                  size={12}
                />

                <span className="flex-1 text-left flex items-center gap-1 truncate">
                  {filterPriority.length === 0 ? (
                    <span className="text-foreground">Priority</span>
                  ) : (
                    <div className="flex gap-1">
                      {filterPriority.slice(0, 2).map((p) => (
                        <span
                          key={p}
                          className={getPriorityBadgeStyle(p)}>
                          {p}
                        </span>
                      ))}
                      {filterPriority.length > 2 && (
                        <span className="text-[10px] text-muted-foreground">
                          +{filterPriority.length - 2}
                        </span>
                      )}
                    </div>
                  )}
                </span>

                <ChevronDown
                  size={10}
                  className={cn(
                    "text-muted-foreground transition-transform duration-200",
                    isFilterOpen ? "rotate-180" : ""
                  )}
                />
              </button>

              {/* Dropdown Menu */}
              {isFilterOpen && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-popover border border-border/60 rounded-lg shadow-lg shadow-black/5 p-1 z-50 animate-in fade-in zoom-in-95 duration-100 min-w-[140px]">
                  <button
                    onClick={() => {
                      setFilterPriority([]);
                    }}
                    className={cn(
                      "w-full flex items-center justify-between px-2.5 py-1.5 rounded-md text-xs transition-colors",
                      filterPriority.length === 0
                        ? "bg-secondary text-foreground font-medium"
                        : "text-muted-foreground hover:bg-secondary/50 hover:text-foreground"
                    )}>
                    <span>All Priorities</span>
                    {filterPriority.length === 0 && (
                      <Check
                        size={10}
                        className="text-primary"
                      />
                    )}
                  </button>

                  <div className="h-px bg-border/50 my-1 mx-1.5" />

                  {["low", "medium", "high", "urgent"].map((priority) => (
                    <button
                      key={priority}
                      onClick={(e) => {
                        e.stopPropagation();
                        togglePriority(priority);
                      }}
                      className={cn(
                        "w-full flex items-center justify-between px-2.5 py-1.5 rounded-md text-xs transition-colors group",
                        filterPriority.includes(priority) ? "bg-secondary" : "hover:bg-secondary/50"
                      )}>
                      <span className={getPriorityBadgeStyle(priority)}>{priority}</span>
                      {filterPriority.includes(priority) && (
                        <Check
                          size={10}
                          className="text-primary"
                        />
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Category Filter */}
            <div className="relative category-filter-dropdown-container">
              <button
                onClick={() => setIsCategoryFilterOpen(!isCategoryFilterOpen)}
                className={cn(
                  "flex items-center gap-1.5 pl-2.5 pr-2.5 py-1.5 border rounded-lg text-xs transition-all duration-200 min-w-[110px] relative",
                  isCategoryFilterOpen
                    ? "border-primary/50 bg-background ring-2 ring-primary/20"
                    : "border-border/60 bg-secondary/30 hover:bg-secondary/50"
                )}>
                <Filter
                  className={cn(
                    "transition-colors",
                    isCategoryFilterOpen ? "text-primary" : "text-muted-foreground"
                  )}
                  size={12}
                />

                <span className="flex-1 text-left flex items-center gap-1 truncate">
                  {filterCategory.length === 0 ? (
                    <span className="text-foreground">Category</span>
                  ) : (
                    <div className="flex gap-1">
                      {filterCategory.slice(0, 2).map((c) => (
                        <span
                          key={c}
                          className={getCategoryBadgeStyle(c)}>
                          {c}
                        </span>
                      ))}
                      {filterCategory.length > 2 && (
                        <span className="text-[10px] text-muted-foreground">
                          +{filterCategory.length - 2}
                        </span>
                      )}
                    </div>
                  )}
                </span>

                <ChevronDown
                  size={10}
                  className={cn(
                    "text-muted-foreground transition-transform duration-200",
                    isCategoryFilterOpen ? "rotate-180" : ""
                  )}
                />
              </button>

              {/* Dropdown Menu */}
              {isCategoryFilterOpen && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-popover border border-border/60 rounded-lg shadow-lg shadow-black/5 p-1 z-50 animate-in fade-in zoom-in-95 duration-100 min-w-[140px]">
                  <button
                    onClick={() => {
                      setFilterCategory([]);
                    }}
                    className={cn(
                      "w-full flex items-center justify-between px-2.5 py-1.5 rounded-md text-xs transition-colors",
                      filterCategory.length === 0
                        ? "bg-secondary text-foreground font-medium"
                        : "text-muted-foreground hover:bg-secondary/50 hover:text-foreground"
                    )}>
                    <span>All Categories</span>
                    {filterCategory.length === 0 && (
                      <Check
                        size={10}
                        className="text-primary"
                      />
                    )}
                  </button>

                  {uniqueCategories.length > 0 && <div className="h-px bg-border/50 my-1 mx-1.5" />}

                  {uniqueCategories.map((category) => (
                    <button
                      key={category}
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleCategory(category);
                      }}
                      className={cn(
                        "w-full flex items-center justify-between px-2.5 py-1.5 rounded-md text-xs transition-colors group",
                        filterCategory.includes(category) ? "bg-secondary" : "hover:bg-secondary/50"
                      )}>
                      <span className={getCategoryBadgeStyle(category)}>{category}</span>
                      {filterCategory.includes(category) && (
                        <Check
                          size={10}
                          className="text-primary"
                        />
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Theme Toggle */}
            {mounted && (
              <button
                onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                className="p-1.5 text-muted-foreground hover:text-primary hover:bg-primary/10 border border-transparent hover:border-primary/20 rounded-lg transition-all duration-200"
                title="Toggle theme">
                {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Board */}
      <div className="flex-1 overflow-y-auto px-4 pt-8 scrollbar-thin scrollbar-thumb-border scrollbar-track-transparent">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-2  max-w-[1920px] mx-auto">
          {columns
            .sort((a, b) => a.orderIndex - b.orderIndex)
            .map((column) => (
              <div
                key={column.id}
                className="h-[calc(100vh-130px)] min-h-[500px]">
                <KanbanColumn
                  column={column}
                  tasks={getFilteredTasksByStatus(column.statusId)}
                  stories={stories}
                  onAddTask={() => setIsAddModalOpen(true)}
                  onTaskMove={moveTask}
                  onTaskEdit={handleTaskEdit}
                  onTaskDelete={handleTaskDelete}
                  onTaskClick={handleTaskClick}
                  isWide={false}
                  totalTasks={filteredTasks.length}
                />
              </div>
            ))}
        </div>
      </div>

      {/* Add Task Modal */}
      <AddTaskModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onSubmit={addTask}
        availableStatuses={columns}
      />

      {/* Task Details Modal */}
      <TaskDetailsModal
        isOpen={isDetailsModalOpen}
        onClose={() => {
          setIsDetailsModalOpen(false);
          setSelectedTask(null);
        }}
        task={selectedTask}
        onEdit={handleTaskEdit}
        onDelete={handleTaskDelete}
      />

      {/* AI Assistant Fab (Future Enhancement) */}
      {/* <button
        className="fixed bottom-6 right-6 w-14 h-14 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center"
        title="AI Assistant"
      >
        <svg
          className="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
          />
        </svg>
      </button> */}
    </div>
  );
};
