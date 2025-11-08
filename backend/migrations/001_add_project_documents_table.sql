-- Migration: Add project_documents table for storing requirements and documentation
-- Created: 2025-11-08
-- Purpose: Store original client requirements, uploaded files, and AI-generated documentation

-- Create project_documents table
CREATE TABLE IF NOT EXISTS public.project_documents (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL,
  document_type text NOT NULL CHECK (document_type IN ('requirements_text', 'requirements_file', 'ai_generated', 'technical_specs', 'other')),
  title text NOT NULL,
  content text,  -- Extracted text content for search/reference
  file_name text,  -- Original filename if uploaded
  file_url text,  -- Supabase Storage URL for original file
  file_size_bytes integer,
  mime_type text,
  metadata jsonb,  -- Additional structured data (e.g., extraction method, word count, etc.)
  created_at timestamp with time zone DEFAULT now(),
  created_by_id uuid,
  
  CONSTRAINT project_documents_pkey PRIMARY KEY (id),
  CONSTRAINT project_documents_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE,
  CONSTRAINT project_documents_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.employees(id)
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_project_documents_project_id ON public.project_documents(project_id);
CREATE INDEX IF NOT EXISTS idx_project_documents_type ON public.project_documents(document_type);
CREATE INDEX IF NOT EXISTS idx_project_documents_created_at ON public.project_documents(created_at DESC);

-- Add Row Level Security (RLS) policies
ALTER TABLE public.project_documents ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view documents for projects they have access to
CREATE POLICY "Users can view project documents they have access to"
  ON public.project_documents FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.projects p
      WHERE p.id = project_documents.project_id
      AND (p.created_by_id = auth.uid() OR EXISTS (
        SELECT 1 FROM public.tasks t
        WHERE t.story_id IN (SELECT id FROM public.user_stories WHERE project_id = p.id)
        AND t.assignee_id = auth.uid()
      ))
    )
  );

-- Policy: Project creators can insert documents
CREATE POLICY "Project creators can insert documents"
  ON public.project_documents FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM public.projects p
      WHERE p.id = project_documents.project_id
      AND p.created_by_id = auth.uid()
    )
  );

-- Policy: Project creators can update their documents
CREATE POLICY "Project creators can update documents"
  ON public.project_documents FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM public.projects p
      WHERE p.id = project_documents.project_id
      AND p.created_by_id = auth.uid()
    )
  );

-- Policy: Project creators can delete their documents
CREATE POLICY "Project creators can delete documents"
  ON public.project_documents FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM public.projects p
      WHERE p.id = project_documents.project_id
      AND p.created_by_id = auth.uid()
    )
  );

-- Add comment for documentation
COMMENT ON TABLE public.project_documents IS 'Stores project documentation including original requirements, uploaded files, and AI-generated docs';
COMMENT ON COLUMN public.project_documents.document_type IS 'Type of document: requirements_text (user input), requirements_file (uploaded PDF/DOCX), ai_generated (Gemini output), technical_specs, other';
COMMENT ON COLUMN public.project_documents.content IS 'Extracted text content for search and reference - searchable by developers';
COMMENT ON COLUMN public.project_documents.file_url IS 'URL to original file in Supabase Storage bucket (if applicable)';
COMMENT ON COLUMN public.project_documents.metadata IS 'Additional data: word count, extraction method, file hash, etc.';
