-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.employees (
  id uuid NOT NULL,
  role_id integer NOT NULL DEFAULT 2,
  full_name text,
  email text NOT NULL UNIQUE,
  CONSTRAINT employees_pkey PRIMARY KEY (id),
  CONSTRAINT employees_id_fkey FOREIGN KEY (id) REFERENCES auth.users(id),
  CONSTRAINT employees_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id)
);
CREATE TABLE public.project_status (
  id integer NOT NULL DEFAULT nextval('project_status_id_seq'::regclass),
  status_name text NOT NULL UNIQUE,
  order_index smallint NOT NULL,
  CONSTRAINT project_status_pkey PRIMARY KEY (id)
);
CREATE TABLE public.projects (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  created_by_id uuid,
  status_id integer NOT NULL DEFAULT 1,
  name text NOT NULL,
  project_context jsonb,
  validation_score numeric,
  iterations integer,
  status text,
  source_info jsonb,
  github_repo_full_name text,  -- NEW: GitHub repository (e.g., "owner/repo")
  github_repo_url text,       -- NEW: Full GitHub URL
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT projects_pkey PRIMARY KEY (id),
  CONSTRAINT projects_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.employees(id),
  CONSTRAINT projects_status_id_fkey FOREIGN KEY (status_id) REFERENCES public.project_status(id)
);
CREATE TABLE public.roles (
  id integer NOT NULL DEFAULT nextval('roles_id_seq'::regclass),
  role_name text NOT NULL UNIQUE,
  CONSTRAINT roles_pkey PRIMARY KEY (id)
);
CREATE TABLE public.story_status (
  id integer NOT NULL DEFAULT nextval('story_status_id_seq'::regclass),
  status_name text NOT NULL UNIQUE,
  order_index smallint NOT NULL,
  CONSTRAINT story_status_pkey PRIMARY KEY (id)
);
CREATE TABLE public.submission_reviews (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  submission_id uuid NOT NULL,
  reviewed_by_id uuid,
  reviewed_at timestamp with time zone DEFAULT now(),
  review_type text NOT NULL DEFAULT 'AI'::text,
  status text NOT NULL,
  qc_score numeric,
  detailed_feedback jsonb,
  CONSTRAINT submission_reviews_pkey PRIMARY KEY (id),
  CONSTRAINT submission_reviews_submission_id_fkey FOREIGN KEY (submission_id) REFERENCES public.task_submissions(id),
  CONSTRAINT submission_reviews_reviewed_by_id_fkey FOREIGN KEY (reviewed_by_id) REFERENCES public.employees(id)
);
CREATE TABLE public.task_status (
  id integer NOT NULL DEFAULT nextval('task_status_id_seq'::regclass),
  status_name text NOT NULL UNIQUE,
  order_index smallint NOT NULL,
  CONSTRAINT task_status_pkey PRIMARY KEY (id)
);
CREATE TABLE public.task_submissions (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  task_id uuid NOT NULL,
  submitted_by_id uuid,
  submitted_at timestamp with time zone DEFAULT now(),
  github_pr_url text,
  code_snippet text,
  notes text,
  CONSTRAINT task_submissions_pkey PRIMARY KEY (id),
  CONSTRAINT task_submissions_task_id_fkey FOREIGN KEY (task_id) REFERENCES public.tasks(id),
  CONSTRAINT task_submissions_submitted_by_id_fkey FOREIGN KEY (submitted_by_id) REFERENCES public.employees(id)
);
CREATE TABLE public.tasks (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  story_id uuid,
  assignee_id uuid,
  status_id integer NOT NULL DEFAULT 1,
  task_id text NOT NULL,
  title text NOT NULL,
  description text,
  category text,
  estimated_hours integer,
  dependencies ARRAY,
  priority text,
  acceptance_criteria ARRAY,
  technical_notes text,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT tasks_pkey PRIMARY KEY (id),
  CONSTRAINT tasks_story_id_fkey FOREIGN KEY (story_id) REFERENCES public.user_stories(id),
  CONSTRAINT tasks_assignee_id_fkey FOREIGN KEY (assignee_id) REFERENCES public.employees(id),
  CONSTRAINT tasks_status_id_fkey FOREIGN KEY (status_id) REFERENCES public.task_status(id)
);
CREATE TABLE public.user_stories (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  project_id uuid,
  status_id integer NOT NULL DEFAULT 1,
  story_id text NOT NULL,
  title text NOT NULL,
  description text,
  acceptance_criteria ARRAY,
  priority text,
  estimated_points integer,
  dependencies ARRAY,
  technical_notes text,
  source_traceability jsonb,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT user_stories_pkey PRIMARY KEY (id),
  CONSTRAINT user_stories_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id),
  CONSTRAINT user_stories_status_id_fkey FOREIGN KEY (status_id) REFERENCES public.story_status(id)
);