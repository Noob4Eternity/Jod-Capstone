"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Calendar, Users, CheckCircle, Clock, Plus } from "lucide-react";
import { supabase } from "@/lib/supabase";

interface Project {
  id: string;
  title: string;
  createdAt: string;
  status: 'active' | 'completed' | 'on-hold';
  userStoriesCount: number;
  tasksCount: number;
  description?: string;
  validation_score?: number;
  iterations?: number;
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Helper functions for Supabase data transformation
  const mapSupabaseStatus = (status: string | null): Project['status'] => {
    if (!status) return 'active';
    switch (status.toLowerCase()) {
      case 'completed':
      case 'success':
        return 'completed';
      case 'failed':
      case 'error':
        return 'on-hold';
      default:
        return 'active';
    }
  };

  const extractDescription = (projectContext: any): string => {
    if (!projectContext) return '';
    try {
      const context = typeof projectContext === 'string' ? JSON.parse(projectContext) : projectContext;
      return context.title || context.description || `Project: ${context.industry || 'General'}`;
    } catch {
      return 'Generated project';
    }
  };

  useEffect(() => {
    const loadProjects = async () => {
      try {
        // Always try to fetch fresh data from Supabase first
        const { data: supabaseProjects, error } = await supabase
          .from('projects')
          .select('id, name, status, validation_score, iterations, project_context')
          .order('created_at', { ascending: false });

        if (!error) {
          // Supabase query succeeded (even if empty), use the result
          const projectsWithCounts = await Promise.all(
            supabaseProjects.map(async (project: any) => {
              // Get user stories for this project
              const { data: stories } = await supabase
                .from('user_stories')
                .select('id')
                .eq('project_id', project.id);

              const storyIds = stories?.map(s => s.id) || [];

              // Get task count for these stories
              const { count: tasksCount } = await supabase
                .from('tasks')
                .select('id', { count: 'exact' })
                .in('story_id', storyIds);

              return {
                id: project.id,
                title: project.name,
                createdAt: new Date().toISOString().split('T')[0], // Use current date as fallback
                status: mapSupabaseStatus(project.status),
                userStoriesCount: storyIds.length,
                tasksCount: tasksCount || 0,
                description: extractDescription(project.project_context),
                validation_score: project.validation_score,
                iterations: project.iterations
              };
            })
          );

          setProjects(projectsWithCounts);
          // Update localStorage cache with fresh data (including empty array)
          localStorage.setItem('projects-list', JSON.stringify(projectsWithCounts));
        } else {
          // Supabase query failed, fall back to localStorage
          console.warn('Supabase fetch failed, using localStorage cache:', error);
          loadFromLocalStorage();
        }
      } catch (error) {
        console.error('Error fetching from Supabase:', error);
        // Fall back to localStorage
        loadFromLocalStorage();
      }

      setIsLoading(false);
    };

    const loadFromLocalStorage = () => {
      const storedProjects = localStorage.getItem('projects-list');
      if (storedProjects) {
        try {
          setProjects(JSON.parse(storedProjects));
        } catch (error) {
          console.error('Error parsing stored projects:', error);
          setProjects(getMockProjects());
        }
      } else {
        // Create mock projects for demonstration
        const mockProjects = getMockProjects();
        setProjects(mockProjects);
        localStorage.setItem('projects-list', JSON.stringify(mockProjects));
      }
    };

    loadProjects();
  }, []);

  const getMockProjects = (): Project[] => [
    {
      id: 'default-project',
      title: 'Default Project',
      createdAt: '2024-01-15',
      status: 'active',
      userStoriesCount: 8,
      tasksCount: 26,
      description: 'Sample project with basic Kanban functionality'
    },
    {
      id: 'project-001',
      title: 'E-commerce Platform',
      createdAt: '2024-01-20',
      status: 'active',
      userStoriesCount: 12,
      tasksCount: 45,
      description: 'Online shopping platform with payment integration'
    },
    {
      id: 'project-002',
      title: 'Task Management App',
      createdAt: '2024-01-25',
      status: 'completed',
      userStoriesCount: 15,
      tasksCount: 52,
      description: 'Collaborative task management application'
    },
    {
      id: 'project-003',
      title: 'Blog CMS',
      createdAt: '2024-02-01',
      status: 'on-hold',
      userStoriesCount: 8,
      tasksCount: 28,
      description: 'Content management system for blogging'
    }
  ];

  const getStatusColor = (status: Project['status']) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'completed':
        return 'bg-blue-100 text-blue-800';
      case 'on-hold':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: Project['status']) => {
    switch (status) {
      case 'active':
        return <Clock className="w-4 h-4" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4" />;
      case 'on-hold':
        return <Users className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading projects...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Projects</h1>
              <p className="mt-2 text-gray-600">
                Select a project to view its Kanban board and manage tasks
              </p>
            </div>
            <Link
              href="/requirements"
              className="inline-flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              <Plus className="w-5 h-5 mr-2" />
              New Project
            </Link>
          </div>
        </div>

        {/* Projects Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <Link
              key={project.id}
              href={`/board/${project.id}`}
              className="block"
            >
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md hover:border-blue-300 transition-all duration-200 p-6">
                {/* Project Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      {project.title}
                    </h3>
                    <div className="flex items-center text-sm text-gray-500 mb-2">
                      <Calendar className="w-4 h-4 mr-1" />
                      Created {new Date(project.createdAt).toLocaleDateString()}
                    </div>
                  </div>
                  <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(project.status)}`}>
                    {getStatusIcon(project.status)}
                    <span className="ml-1 capitalize">{project.status.replace('-', ' ')}</span>
                  </div>
                </div>

                {/* Project Description */}
                {project.description && (
                  <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                    {project.description}
                  </p>
                )}

                {/* Project Stats */}
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center text-gray-500">
                      <Users className="w-4 h-4 mr-1" />
                      {project.userStoriesCount} stories
                    </div>
                    <div className="flex items-center text-gray-500">
                      <CheckCircle className="w-4 h-4 mr-1" />
                      {project.tasksCount} tasks
                    </div>
                  </div>
                  <div className="text-blue-600 font-medium">
                    View Board →
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>

        {/* Empty State */}
        {projects.length === 0 && (
          <div className="text-center py-12">
            <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Plus className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No projects yet</h3>
            <p className="text-gray-600 mb-6">
              Get started by creating your first project with AI agents.
            </p>
            <Link
              href="/requirements"
              className="inline-flex items-center px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              <Plus className="w-5 h-5 mr-2" />
              Create Your First Project
            </Link>
          </div>
        )}

        {/* Footer */}
        <div className="mt-12 text-center">
          <Link
            href="/menu"
            className="text-gray-600 hover:text-gray-900 transition-colors"
          >
            ← Back to Menu
          </Link>
        </div>
      </div>
    </div>
  );
}