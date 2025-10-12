"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Calendar, Users, CheckCircle, Clock, Plus } from "lucide-react";
import { supabase } from "@/lib/supabase";
import { FloatingNav } from "@/components/FloatingNav";
import { FloatingUtilityBar } from "@/components/FloatingUtilityBar";
interface Project {
  id: string;
  title: string;
  createdAt: string;
  status: "active" | "completed" | "on-hold";
  userStoriesCount: number;
  tasksCount: number;
  description?: string;
  validation_score?: number;
  iterations?: number;
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // ✅ Status styling helpers
  const getStatusStyle = (status: Project["status"]) => {
    switch (status) {
      case "active":
        return "bg-chart-2/10 text-chart-2 ring-1 ring-chart-2/20";
      case "completed":
        return "bg-chart-1/10 text-chart-1 ring-1 ring-chart-1/20";
      case "on-hold":
        return "bg-chart-3/10 text-chart-3 ring-1 ring-chart-3/20";
      default:
        return "bg-muted text-muted-foreground ring-1 ring-border";
    }
  };

  const getStatusIcon = (status: Project["status"]) => {
    switch (status) {
      case "active":
        return <Clock className="w-4 h-4" />;
      case "completed":
        return <CheckCircle className="w-4 h-4" />;
      case "on-hold":
        return <Users className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  // ✅ Mock data fallback
  const getMockProjects = (): Project[] => [
    {
      id: "default-project",
      title: "Default Project",
      createdAt: "2024-01-15",
      status: "active",
      userStoriesCount: 8,
      tasksCount: 26,
      description: "Sample project with basic Kanban functionality",
    },
    {
      id: "project-001",
      title: "E-commerce Platform",
      createdAt: "2024-01-20",
      status: "active",
      userStoriesCount: 12,
      tasksCount: 45,
      description: "Online shopping platform with payment integration",
    },
    {
      id: "project-002",
      title: "Task Management App",
      createdAt: "2024-01-25",
      status: "completed",
      userStoriesCount: 15,
      tasksCount: 52,
      description: "Collaborative task management application",
    },
    {
      id: "project-003",
      title: "Blog CMS",
      createdAt: "2024-02-01",
      status: "on-hold",
      userStoriesCount: 8,
      tasksCount: 28,
      description: "Content management system for blogging",
    },
  ];

  // ✅ Data loading
  useEffect(() => {
    const loadProjects = async () => {
      try {
        const { data, error } = await supabase
          .from("projects")
          .select("id, name, status, validation_score, iterations, project_context")
          .order("created_at", { ascending: false });

        if (error || !data) {
          console.warn("Supabase fetch failed, using mock data:", error);
          setProjects(getMockProjects());
        } else {
          // Map Supabase projects to our format
          const mappedProjects: Project[] = data.map((p: any) => ({
            id: p.id,
            title: p.name,
            createdAt: new Date().toISOString().split("T")[0],
            status: (p.status || "active").toLowerCase(),
            userStoriesCount: Math.floor(Math.random() * 15), // placeholder
            tasksCount: Math.floor(Math.random() * 50), // placeholder
            description: p.project_context?.description || "Generated project",
            validation_score: p.validation_score,
            iterations: p.iterations,
          }));
          setProjects(mappedProjects);
        }
      } catch (err) {
        console.error("Error fetching projects:", err);
        setProjects(getMockProjects());
      }
      setIsLoading(false);
    };

    loadProjects();
  }, []);

  // ✅ Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center text-muted-foreground">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mb-4"></div>
          <p>Loading projects...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background px-6 py-10 relative">
      <FloatingNav />
      <FloatingUtilityBar />

      <div className="max-w-7xl mx-auto pt-20">
        {/* Added pt-20 to push content below navbar */}
        {/* Header */}
        <div className="flex items-center justify-between mb-10">
          <div>
            <h1 className="text-4xl font-bold text-foreground">Projects</h1>
            <p className="text-muted-foreground italic">
              Manage your projects and view their Kanban boards
            </p>
          </div>
          <Link
            href="/requirements"
            className="inline-flex items-center px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors">
            <Plus className="w-5 h-5 mr-2" />
            New Project
          </Link>
        </div>
        <div className="mb-8">
          <Link
            href="/requirements"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground font-medium hover:bg-primary/80 transition">
            <Plus className="w-5 h-5" />
            New Project
          </Link>
        </div>

        {/* Projects grid */}
        {projects.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <Link
                key={project.id}
                href={`/board/${project.id}`}
                className="block group">
                <div className="p-6 bg-card border border-border rounded-xl shadow-sm hover:shadow-lg hover:border-primary/40 transition-all">
                  {/* Header */}
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="text-lg font-semibold text-foreground group-hover:text-primary transition">
                        {project.title}
                      </h3>
                      <div className="flex items-center text-xs text-muted-foreground mt-1">
                        <Calendar className="w-4 h-4 mr-1" />
                        {new Date(project.createdAt).toLocaleDateString()}
                      </div>
                    </div>
                    <span
                      className={`flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusStyle(
                        project.status
                      )}`}>
                      {getStatusIcon(project.status)}
                      {project.status}
                    </span>
                  </div>

                  {/* Description */}
                  {project.description && (
                    <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
                      {project.description}
                    </p>
                  )}

                  {/* Stats */}
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex gap-4 text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Users className="w-4 h-4" />
                        {project.userStoriesCount} stories
                      </div>
                      <div className="flex items-center gap-1">
                        <CheckCircle className="w-4 h-4" />
                        {project.tasksCount} tasks
                      </div>
                    </div>
                    <span className="text-primary font-medium group-hover:text-accent-foreground transition">
                      View →
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          // Empty state
          <div className="text-center py-16">
            <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-muted flex items-center justify-center">
              <Plus className="w-8 h-8 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-semibold text-foreground mb-2">No projects yet</h3>
            <p className="text-muted-foreground mb-6">
              Get started by creating your first project with AI agents.
            </p>
            <Link
              href="/requirements"
              className="inline-flex items-center gap-2 px-5 py-3 rounded-lg bg-primary text-primary-foreground hover:bg-primary/80 transition">
              <Plus className="w-5 h-5" />
              Create Your First Project
            </Link>
          </div>
        )}

        {/* Footer */}
        <div className="mt-12 text-center">
          <Link
            href="/menu"
            className="text-muted-foreground hover:text-foreground transition">
            ← Back to Menu
          </Link>
        </div>
      </div>
    </div>
  );
}
