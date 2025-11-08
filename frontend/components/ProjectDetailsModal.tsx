'use client';

import React, { useState, useEffect } from 'react';
import { X, FileText, Calendar, GitBranch, Users, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import { supabase } from '@/lib/supabase';

interface ProjectDetails {
  id: string;
  name: string;
  created_at: string;
  github_repo_full_name?: string;
  status?: string;
  validation_score?: number;
  iterations?: number;
}

interface ProjectDocument {
  id: string;
  document_type: string;
  content: string;
  created_at: string;
}

interface ProjectStats {
  totalTasks: number;
  completedTasks: number;
  totalStories: number;
  inProgressTasks: number;
}

interface ProjectDetailsModalProps {
  projectId: string;
  isOpen: boolean;
  onClose: () => void;
}

export const ProjectDetailsModal: React.FC<ProjectDetailsModalProps> = ({
  projectId,
  isOpen,
  onClose,
}) => {
  const [project, setProject] = useState<ProjectDetails | null>(null);
  const [documents, setDocuments] = useState<ProjectDocument[]>([]);
  const [stats, setStats] = useState<ProjectStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'requirements' | 'documents'>('overview');

  useEffect(() => {
    if (isOpen && projectId) {
      loadProjectData();
    }
  }, [isOpen, projectId]);

  const loadProjectData = async () => {
    setIsLoading(true);
    try {
      // Load project details
      const { data: projectData, error: projectError } = await supabase
        .from('projects')
        .select('*')
        .eq('id', projectId)
        .single();

      if (projectError) throw projectError;
      setProject(projectData);

      // Load project documents
      const { data: docsData, error: docsError } = await supabase
        .from('project_documents')
        .select('*')
        .eq('project_id', projectId)
        .order('created_at', { ascending: false });

      if (!docsError && docsData) {
        setDocuments(docsData);
      }

      // Load project statistics
      const [tasksResult, storiesResult] = await Promise.all([
        supabase.from('tasks').select('status_id, story_id'),
        supabase.from('user_stories').select('id, project_id').eq('project_id', projectId)
      ]);

      if (tasksResult.data && storiesResult.data) {
        // Filter tasks that belong to this project's stories
        const projectStoryIds = storiesResult.data.map(story => story.id);
        const projectTasks = tasksResult.data.filter(task => projectStoryIds.includes(task.story_id));

        const totalTasks = projectTasks.length;
        const completedTasks = projectTasks.filter(t => t.status_id === 4).length;
        const inProgressTasks = projectTasks.filter(t => t.status_id === 2).length;

        setStats({
          totalTasks,
          completedTasks,
          totalStories: storiesResult.data.length,
          inProgressTasks,
        });
      }

    } catch (error) {
      console.error('Error loading project data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusIcon = (status?: string) => {
    switch (status?.toLowerCase()) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'active':
        return <Clock className="w-4 h-4 text-blue-500" />;
      case 'on-hold':
        return <AlertCircle className="w-4 h-4 text-yellow-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status?: string) => {
    switch (status?.toLowerCase()) {
      case 'completed':
        return 'bg-green-100 text-green-700 border-green-200';
      case 'active':
        return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'on-hold':
        return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <FileText className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                {project?.name || 'Project Details'}
              </h2>
              <p className="text-sm text-gray-500">Project overview and requirements</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200">
          {[
            { id: 'overview', label: 'Overview', icon: Users },
            { id: 'requirements', label: 'Requirements', icon: FileText },
            { id: 'documents', label: 'Documents', icon: FileText },
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id as any)}
              className={`flex items-center gap-2 px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              <span className="ml-3 text-gray-600">Loading project details...</span>
            </div>
          ) : (
            <>
              {/* Overview Tab */}
              {activeTab === 'overview' && (
                <div className="space-y-6">
                  {/* Project Info */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div>
                        <label className="text-sm font-medium text-gray-700">Project Name</label>
                        <p className="text-lg font-semibold text-gray-900">{project?.name}</p>
                      </div>

                      <div>
                        <label className="text-sm font-medium text-gray-700">Status</label>
                        <div className="flex items-center gap-2 mt-1">
                          {getStatusIcon(project?.status)}
                          <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(project?.status)}`}>
                            {project?.status || 'Unknown'}
                          </span>
                        </div>
                      </div>

                      <div>
                        <label className="text-sm font-medium text-gray-700">Created</label>
                        <div className="flex items-center gap-2 mt-1">
                          <Calendar className="w-4 h-4 text-gray-400" />
                          <span className="text-gray-900">{project?.created_at ? formatDate(project.created_at) : 'Unknown'}</span>
                        </div>
                      </div>

                      {project?.github_repo_full_name && (
                        <div>
                          <label className="text-sm font-medium text-gray-700">GitHub Repository</label>
                          <div className="flex items-center gap-2 mt-1">
                            <GitBranch className="w-4 h-4 text-gray-400" />
                            <span className="text-gray-900 font-mono text-sm">{project.github_repo_full_name}</span>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Statistics */}
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold text-gray-900">Project Statistics</h3>

                      <div className="grid grid-cols-2 gap-4">
                        <div className="bg-blue-50 p-4 rounded-lg">
                          <div className="text-2xl font-bold text-blue-600">{stats?.totalStories || 0}</div>
                          <div className="text-sm text-blue-700">User Stories</div>
                        </div>

                        <div className="bg-green-50 p-4 rounded-lg">
                          <div className="text-2xl font-bold text-green-600">{stats?.totalTasks || 0}</div>
                          <div className="text-sm text-green-700">Total Tasks</div>
                        </div>

                        <div className="bg-yellow-50 p-4 rounded-lg">
                          <div className="text-2xl font-bold text-yellow-600">{stats?.inProgressTasks || 0}</div>
                          <div className="text-sm text-yellow-700">In Progress</div>
                        </div>

                        <div className="bg-purple-50 p-4 rounded-lg">
                          <div className="text-2xl font-bold text-purple-600">{stats?.completedTasks || 0}</div>
                          <div className="text-sm text-purple-700">Completed</div>
                        </div>
                      </div>

                      {project?.validation_score && (
                        <div>
                          <label className="text-sm font-medium text-gray-700">Validation Score</label>
                          <div className="mt-1">
                            <div className="flex items-center gap-2">
                              <div className="flex-1 bg-gray-200 rounded-full h-2">
                                <div
                                  className="bg-green-500 h-2 rounded-full"
                                  style={{ width: `${project.validation_score}%` }}
                                ></div>
                              </div>
                              <span className="text-sm font-medium text-gray-900">{project.validation_score}%</span>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Requirements Tab */}
              {activeTab === 'requirements' && (
                <div className="space-y-6">
                  {documents.filter(doc => doc.document_type === 'requirements_text').length > 0 ? (
                    documents
                      .filter(doc => doc.document_type === 'requirements_text')
                      .map((doc) => (
                        <div key={doc.id} className="space-y-4">
                          <div className="flex items-center justify-between">
                            <h3 className="text-lg font-semibold text-gray-900">Requirements Text</h3>
                            <span className="text-sm text-gray-500">
                              {formatDate(doc.created_at)}
                            </span>
                          </div>
                          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                            <pre className="text-sm text-gray-800 whitespace-pre-wrap font-sans">
                              {doc.content}
                            </pre>
                          </div>
                        </div>
                      ))
                  ) : (
                    <div className="text-center py-12">
                      <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">No Requirements Found</h3>
                      <p className="text-gray-500">Requirements text hasn't been uploaded for this project yet.</p>
                    </div>
                  )}
                </div>
              )}

              {/* Documents Tab */}
              {activeTab === 'documents' && (
                <div className="space-y-6">
                  {documents.length > 0 ? (
                    documents.map((doc) => (
                      <div key={doc.id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <FileText className="w-5 h-5 text-blue-500" />
                            <div>
                              <h4 className="font-medium text-gray-900 capitalize">
                                {doc.document_type.replace('_', ' ')}
                              </h4>
                              <p className="text-sm text-gray-500">
                                Created {formatDate(doc.created_at)}
                              </p>
                            </div>
                          </div>
                        </div>

                        <div className="bg-gray-50 border border-gray-200 rounded p-3">
                          <div className="text-sm text-gray-800 max-h-60 overflow-y-auto">
                            {doc.document_type === 'requirements_file' ? (
                              <pre className="whitespace-pre-wrap font-mono text-xs">
                                {doc.content.length > 1000
                                  ? `${doc.content.substring(0, 1000)}...`
                                  : doc.content
                                }
                              </pre>
                            ) : (
                              <div className="whitespace-pre-wrap">
                                {doc.content.length > 1000
                                  ? `${doc.content.substring(0, 1000)}...`
                                  : doc.content
                                }
                              </div>
                            )}
                          </div>
                        </div>

                        {doc.content.length > 1000 && (
                          <p className="text-xs text-gray-500 mt-2">
                            Showing first 1000 characters. Full content available in database.
                          </p>
                        )}
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-12">
                      <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">No Documents Found</h3>
                      <p className="text-gray-500">No project documents have been uploaded yet.</p>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};