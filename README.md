<p align="center">
  <h1 align="center">🚀 JOD — AI-Powered Project Management Platform</h1>
  <p align="center">
    Transform raw requirements into structured, validated user stories and development tasks — powered by a multi-agent LangGraph workflow and Google Gemini 2.5 Pro.
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Next.js-15-black?logo=next.js&logoColor=white" alt="Next.js" />
  <img src="https://img.shields.io/badge/LangGraph-Agent_Workflow-orange" alt="LangGraph" />
  <img src="https://img.shields.io/badge/Gemini-2.5_Pro-4285F4?logo=google&logoColor=white" alt="Gemini" />
  <img src="https://img.shields.io/badge/Supabase-Database_&_Auth-3ECF8E?logo=supabase&logoColor=white" alt="Supabase" />
</p>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Backend Deep Dive](#-backend-deep-dive)
  - [Multi-Agent Workflow (LangGraph)](#multi-agent-workflow-langgraph)
  - [Agent Details](#agent-details)
  - [Workflow State Machine](#workflow-state-machine)
  - [API Endpoints](#api-endpoints)
  - [GitHub Webhook & QC Agent](#github-webhook--qc-agent)
- [Frontend Deep Dive](#-frontend-deep-dive)
  - [Pages](#pages)
  - [Core Components](#core-components)
- [Database Schema](#-database-schema)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Environment Variables](#environment-variables)
- [API Reference](#-api-reference)
- [Project Structure](#-project-structure)
- [License](#-license)

---

## 🌟 Overview

**JOD** is a capstone project that reimagines how software projects go from idea to execution. Instead of manually writing user stories and decomposing them into tasks, JOD uses a **multi-agent AI system** to:

1. **Ingest** requirements from raw text, PDF, or DOCX files (or any combination).
2. **Generate** structured, Agile-compliant user stories via Google Gemini 2.5 Pro.
3. **Validate** stories against the original requirements through an iterative feedback loop.
4. **Decompose** approved stories into development tasks with acceptance criteria.
5. **Persist** everything to a Supabase (PostgreSQL) database.
6. **Visualize** tasks on an interactive Kanban board built with Next.js.
7. **Review** code automatically via a GitHub webhook that triggers an AI QC Agent on pull requests.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| **Multimodal Input** | Accepts plain text, PDF, DOCX, or a combination of all three as requirements input. |
| **Multi-Agent Workflow** | LangGraph state machine orchestrating generation, validation, task decomposition, and storage agents. |
| **Iterative Validation** | Stories are scored on a 100-point rubric; the system loops up to N iterations to improve quality. |
| **Task Decomposition** | Each validated user story is broken into backend, frontend, testing, and DevOps tasks with specific acceptance criteria. |
| **GitHub PR QC Agent** | Webhook-driven AI code reviewer that analyzes pull requests against task acceptance criteria and posts structured feedback. |
| **Kanban Board** | Full-featured board with drag-and-drop, priority/category filters, story grouping, WIP limits, and dark mode. |
| **Supabase Integration** | End-to-end persistence — projects, stories, tasks, documents, submissions, and reviews all stored in PostgreSQL via Supabase. |
| **Auth & RBAC** | Supabase Auth with session management, protected routes, and role-based access (Admin, Developer, etc.). |
| **Dark / Light Mode** | Full theme support across the entire frontend via `next-themes`. |

---

## 🏗 Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js 15)                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────────┐  │
│  │ Landing  │ │ Projects │ │ AI Agent │ │ Kanban Board       │  │
│  │ Page     │ │ List     │ │ Form     │ │ (Drag & Drop)      │  │
│  └──────────┘ └──────────┘ └────┬─────┘ └────────┬───────────┘  │
│                                  │                │              │
│                            Supabase Client ◄──────┘              │
└──────────────────────────────────┼───────────────────────────────┘
                                   │ POST /generate
                                   ▼
┌──────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI + LangGraph)                 │
│                                                                  │
│  ┌────────────┐    ┌─────────────────────────────────────────┐   │
│  │ API Layer  │───▶│         LangGraph Workflow               │   │
│  │ (FastAPI)  │    │                                         │   │
│  └────────────┘    │  ┌───────────┐    ┌───────────────┐     │   │
│                    │  │ Generation│───▶│  Validation    │     │   │
│  ┌────────────┐    │  │  Agent    │    │  Agent         │     │   │
│  │  GitHub    │    │  └───────────┘    └──────┬────────┘     │   │
│  │  Webhook   │    │       ▲                  │              │   │
│  │  (/api/    │    │       │    Feedback Loop  │              │   │
│  │  github-   │    │       └──────────────────┘              │   │
│  │  webhook)  │    │                  │ Score ≥ 80           │   │
│  └─────┬──────┘    │                  ▼                      │   │
│        │           │  ┌───────────┐    ┌───────────────┐     │   │
│        ▼           │  │   Task    │───▶│   Supabase    │     │   │
│  ┌────────────┐    │  │  Agent    │    │   Agent       │     │   │
│  │ QC Agent   │    │  └───────────┘    └───────────────┘     │   │
│  └────────────┘    └─────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────┐
│                      SUPABASE (PostgreSQL)                        │
│  projects │ user_stories │ tasks │ task_submissions │ reviews     │
│  employees │ project_documents │ roles │ statuses                 │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔬 Backend Deep Dive

The backend is a **FastAPI** application that exposes REST endpoints and orchestrates an AI-powered multi-agent workflow using **LangGraph**.

### Multi-Agent Workflow (LangGraph)

The core of the system is a **LangGraph `StateGraph`** defined in `backend/workflow.py`. It chains four specialized agents together with a conditional feedback loop:

```
Initialize ──▶ Generate Stories ──▶ Validate Stories ──┬──▶ Generate Tasks ──▶ Save to Supabase ──▶ Done
                       ▲                               │
                       │         (Score < 80)           │
                       └───────── Needs Revision ◄──────┘
                                                        │
                                 (Max iterations hit)   │
                                 ──▶ Human Review ◄─────┘
```

**Routing Logic** (`determine_next_step`):
- **Score ≥ 80** → `approved` → proceed to task generation
- **Score 50–79** → `needs_revision` → loop back to story generation with feedback
- **Score < 50** or **score degradation > 10 points** → `low_quality` → escalate to human review
- **Max iterations reached with score ≥ 70** → proceed anyway
- **Max iterations reached with score < 70** → escalate to human review

### Agent Details

#### 1. `MultimodalUserStoryGenerationAgent` — *Generation Agent*
**File:** `backend/agents/generation_agent.py`

The generation agent is the most complex component. It:

- **Parses multimodal input** — separates primary text requirements from uploaded document content, tracking source metadata (content distribution percentages, document count, etc.).
- **Analyzes content** — uses a dedicated LLM call to extract core features, stakeholders, technical constraints, business goals, conflicts between sources, and information gaps.
- **Resolves conflicts** — generates explicit conflict resolution guidance when primary text and documents contradict, always favoring primary requirements.
- **Generates user stories** — produces stories following the strict JSON schema with fields: `id` (US001 format), `title` (As a/I want/So that), `description`, `acceptance_criteria` (3-7 items), `priority`, `estimated_points` (Fibonacci), `dependencies`, and `technical_notes`.
- **Handles iteration feedback** — on subsequent iterations, incorporates specific feedback from the validation agent (missing requirements, story-specific issues, critical problems) with instructions to fix only what's broken.

**Scoring Alignment (100 points):** Format (15) + Completeness (20) + Requirements Coverage (25) + Source Integration (10) + NFR Coverage (10) + Dependencies (10) + Acceptance Criteria Quality (10)

**LLM:** Google Gemini 2.5 Pro (temperature: 0.8 for creative generation)

---

#### 2. `EnhancedUserStoryValidationAgent` — *Validation Agent*
**File:** `backend/agents/validation_agent.py`

Validates generated stories against the **full original requirements** (not summaries) using a weighted rubric:

| Category | Points |
|---|---|
| Requirements & NFR Coverage | 25 |
| Multimodal Source Integration | 15 |
| Completeness & Acceptance Criteria | 20 |
| Format & Required Fields | 15 |
| Dependencies & Consistency | 10 |
| Sizing & Priority Logic | 10 |
| Technical Notes Quality | 5 |

Returns structured feedback including: `missing_requirements`, `story_issues` (per story), `recommendations`, `critical_issues`, and `multimodal_analysis` (source coverage, integration quality, conflict resolution scores).

**LLM:** Google Gemini 2.5 Pro (temperature: 0.2 for consistent evaluation)

---

#### 3. `TaskGenerationAgent` — *Task Agent*
**File:** `backend/agents/task_agent.py`

Decomposes validated user stories into actionable development tasks:

- Generates **3–5 tasks per story**: backend, frontend, testing, and optional DevOps/documentation tasks.
- Tasks are **project-specific** — references actual endpoints, components, and business logic from the requirements context.
- Uses **intelligent batching** — processes up to 7 stories per LLM call for efficiency, falling back to individual processing on failure.
- Each task includes: `id` (T001 format), `story_id`, `title`, `description`, `category`, `estimated_hours` (4-16h range), `priority`, `dependencies`, `acceptance_criteria` (2-4 items), and `technical_notes`.
- Ensures **every story gets tasks** via a fallback mechanism that generates basic backend/frontend/testing tasks.

**LLM:** Google Gemini 2.5 Pro (temperature: 0.4)

---

#### 4. `SupabaseWorkflowAgent` — *Storage Agent*
**File:** `backend/agents/supabase_agent.py`

Persists the entire workflow output to Supabase:

- Creates a **project record** with name, validation score, iterations, status, and optional GitHub repository link.
- Saves **project documents** in three categories:
  - `requirements_text` — original user text input
  - `requirements_file` — extracted content from uploaded PDF/DOCX
  - `ai_generated` — structured AI analysis (features, stakeholders, constraints, goals)
- Inserts all **user stories** with full schema fields.
- Inserts all **tasks** linked to their parent stories via UUID foreign keys.
- Maps story IDs (US001) to database UUIDs for proper relational linking.

---

#### 5. `QCAgent` — *Quality Control Agent*
**File:** `backend/agents/qc_agent.py`

An AI code reviewer triggered by GitHub webhooks:

- Receives a **code diff** from a pull request.
- Cross-references the diff against the **task's acceptance criteria** and **parent user story**.
- Returns a structured JSON review:
  - Per-criterion analysis (met/not met + reasoning)
  - Code quality review (readability, best practices, bugs)
  - Security review (hardcoded secrets, injection risks, missing error handling)
  - QC Score (0-100) and status (Approved / Changes Requested)

**LLM:** Google Gemini 2.5 Pro (temperature: 0.2)

---

### Workflow State Machine

The shared state (`ProjectManagementState` in `backend/state.py`) is a `TypedDict` carrying all data through the workflow:

```python
ProjectManagementState:
  # Input
  client_requirements: str
  documentation: Dict          # Multimodal content (text + documents)
  project_context: Dict        # Industry, team size, tech stack, etc.

  # Generated Artifacts
  user_stories: List[Dict]
  tasks: List[Dict]

  # Validation & Feedback Loop
  validation_status: str       # "approved" | "needs_revision" | "needs_clarification"
  validation_score: float      # 0-100
  detailed_feedback: Dict      # Rich feedback for iteration
  improvement_instructions: List[str]

  # Supabase Storage
  supabase_project_id: str     # Database UUID after save
  storage_success: bool

  # Metadata
  iteration_count: int
  max_iterations: int
  processing_time: Dict[str, float]
```

---

### API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/generate` | **Unified endpoint** — accepts text requirements + PDF/DOCX files (multipart form). Returns user stories, tasks, validation score, and Supabase project ID. |
| `POST` | `/generate/text` | Legacy text-only generation endpoint. |
| `POST` | `/generate/pdf` | Legacy PDF/DOCX-only generation endpoint. |
| `POST` | `/save-to-supabase` | Manually save project data (stories + tasks) to Supabase. |
| `POST` | `/api/github-webhook` | GitHub webhook receiver — triggers QC analysis on PR events (`opened`, `synchronize`, `reopened`). |
| `GET` | `/health` | Health check — returns API version and feature flags. |
| `GET` | `/` | API info — lists all endpoints and supported features. |

**Generation Response Schema:**
```json
{
  "success": true,
  "project_id": "uuid-from-supabase",
  "user_stories": [...],
  "tasks": [...],
  "validation_score": 85.5,
  "iterations": 2,
  "status": "approved",
  "multimodal_metadata": {...},
  "source_info": {
    "text_provided": true,
    "pdf_provided": true,
    "multimodal": true
  },
  "supabase_storage": {
    "success": true,
    "project_id": "uuid"
  }
}
```

---

### GitHub Webhook & QC Agent

The `/api/github-webhook` endpoint implements a complete CI/CD quality gate:

1. **Signature Verification** — validates `X-Hub-Signature-256` using HMAC-SHA256.
2. **Task ID Extraction** — parses PR title and branch name for patterns like `T001`, `TASK-001`.
3. **Task Status Update** — automatically moves the task from "In Progress" to "In Review" when a PR is opened.
4. **QC Analysis** — fetches the code diff, retrieves task/story context from Supabase, runs the QC Agent.
5. **Results Storage** — creates a `task_submission` record and stores the `submission_review`.
6. **PR Comment** — posts a formatted review comment on the GitHub PR with per-criterion analysis, scores, and recommendations.

Supports both **GitHub Personal Access Token** and **GitHub App** authentication.

---

## 🎨 Frontend Deep Dive

The frontend is a **Next.js 15** application (App Router, Turbopack) with **Supabase Auth**, **Tailwind CSS**, and full dark/light mode support.

### Pages

| Route | Page | Description |
|---|---|---|
| `/` | Home | Redirects to `/landing`. |
| `/landing` | Landing Page | Marketing page with hero section, stats, feature grid (AI Generation, GitHub Integration, Smart Workflows, Analytics), and "How It Works" walkthrough. |
| `/login` | Login | Split-screen auth page with email/password login via Supabase Auth. Theme-aware branded illustration. |
| `/menu` | Main Hub | 2×2 card grid: Projects, AI Agent, Analytics (coming soon), Settings (coming soon). |
| `/projects` | Projects List | Responsive card grid of all projects from Supabase with status badges, validation scores, and iteration counts. |
| `/requirements` | AI Agent | Standalone form for submitting requirements (text + PDF + project context) to the backend `/generate` endpoint. |
| `/dashboard` | Dashboard | SPA-like layout with `FloatingNav` for switching between Menu, Projects, and Requirements views without page reloads. |
| `/board/[projectId]` | Kanban Board | Dynamic project board with drag-and-drop tasks, priority/category filters, story grouping, and full CRUD. |

### Core Components

| Component | Purpose |
|---|---|
| `KanbanBoard` | Main board orchestrator — fetches statuses/project name, manages modals, search, filters. Uses `useKanban` hook. |
| `KanbanColumn` | Renders a status column with drag-and-drop support, progress bar, story grouping with collapsible headers, WIP limits. |
| `KanbanCard` | Draggable task card with priority/category badges, assignee avatar, due date tracking, overdue pulse animation. |
| `AddTaskModal` | Full form modal for manual task creation with validation — title, description, status, priority, category, tags, etc. |
| `TaskDetailsModal` | Theme-aware detail view with Edit and Delete actions. Shows priority, description, assignee, dates, acceptance criteria. |
| `RequirementsContent` | Reusable form for submitting requirements to the AI backend. Handles text + PDF upload + project context fields. |
| `ProjectDetailsModal` | Tabbed modal (Overview / Requirements / Documents) showing project stats, validation scores, and stored documents. |
| `AuthGuard` | Route protection wrapper — redirects unauthenticated users to `/login`, preserves redirect URL. |
| `FloatingNav` | Pill-shaped top-center navigation bar with active state highlighting. |
| `FloatingUtilityBar` | Top-right bar with theme toggle and sign-out button. |
| `MainLayout` | SPA shell for dashboard — renders nav bars and switches between Menu/Projects/Requirements views. |

### Custom Hooks

| Hook | Purpose |
|---|---|
| `useKanban(projectId)` | Encapsulates all Kanban data logic — fetches tasks/stories from Supabase, provides `addTask`, `updateTask`, `moveTask`, `deleteTask`, `updateTaskAssignee`. |

---

## 🗄 Database Schema

The application uses **Supabase (PostgreSQL)** with the following tables:

```
┌─────────────┐     ┌───────────────┐     ┌─────────────┐
│  employees  │     │   projects    │     │   roles     │
│─────────────│     │───────────────│     │─────────────│
│ id (uuid)   │◄────│ created_by_id │     │ id (serial) │
│ role_id     │────▶│ id (uuid)     │     │ role_name   │
│ full_name   │     │ name          │     └─────────────┘
│ email       │     │ project_context│
└─────────────┘     │ validation_score│
                    │ iterations     │
                    │ github_repo_*  │
                    └───────┬───────┘
                            │ 1:N
               ┌────────────┼────────────┐
               ▼                         ▼
    ┌──────────────────┐     ┌───────────────────────┐
    │  user_stories    │     │  project_documents    │
    │──────────────────│     │───────────────────────│
    │ id (uuid)        │     │ id (uuid)             │
    │ project_id       │     │ project_id            │
    │ story_id (US001) │     │ document_type         │
    │ title            │     │ title, content        │
    │ description      │     │ file_name, file_url   │
    │ acceptance_criteria│   │ metadata (jsonb)      │
    │ priority         │     └───────────────────────┘
    │ estimated_points │
    │ dependencies     │
    │ technical_notes  │
    └───────┬──────────┘
            │ 1:N
            ▼
    ┌──────────────────┐
    │     tasks        │
    │──────────────────│         ┌────────────────────┐
    │ id (uuid)        │         │ task_submissions   │
    │ story_id         │    1:N  │────────────────────│
    │ task_id (T001)   │────────▶│ id (uuid)          │
    │ title            │         │ task_id            │
    │ description      │         │ github_pr_url      │
    │ category         │         │ code_snippet       │
    │ estimated_hours  │         └────────┬───────────┘
    │ acceptance_criteria│                │ 1:N
    │ technical_notes  │                 ▼
    │ assignee_id      │       ┌────────────────────┐
    │ status_id        │       │ submission_reviews  │
    └──────────────────┘       │────────────────────│
                               │ id (uuid)          │
                               │ submission_id      │
                               │ review_type (AI)   │
                               │ status             │
                               │ qc_score           │
                               │ detailed_feedback  │
                               └────────────────────┘
```

**Status Tables:** `project_status`, `story_status`, `task_status` — each with `id`, `status_name`, and `order_index` for Kanban column ordering.

**Row Level Security (RLS):** Enabled on `project_documents` — users can only access documents for projects they created or are assigned to.

---

## 🛠 Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **Python 3.10+** | Runtime |
| **FastAPI** | REST API framework |
| **LangGraph** | Multi-agent workflow orchestration (state machine) |
| **LangChain** | LLM abstractions, prompt templates, output parsers |
| **Google Gemini 2.5 Pro** | Large Language Model for all AI agents |
| **Supabase Python Client** | Database operations |
| **PyPDF2 / pdfplumber** | PDF text extraction (dual fallback) |
| **python-docx** | DOCX text extraction |
| **PyGithub** | GitHub API integration for webhooks and PR management |
| **Pydantic** | Request/response validation |
| **uvicorn** | ASGI server |

### Frontend
| Technology | Purpose |
|---|---|
| **Next.js 15** | React framework (App Router, Turbopack) |
| **TypeScript** | Type safety |
| **Tailwind CSS 4** | Utility-first styling |
| **Supabase JS Client** | Auth + database queries |
| **next-themes** | Dark/light mode |
| **Lucide React** | Icon library |
| **GSAP** | Animation library |
| **Motion (Framer Motion)** | React animation primitives |

### Infrastructure
| Technology | Purpose |
|---|---|
| **Supabase** | PostgreSQL database, authentication, Row Level Security |
| **GitHub Webhooks** | Automated PR analysis trigger |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **Node.js 18+** and **npm**
- A **Google Gemini API key** ([Get one here](https://aistudio.google.com/apikey))
- A **Supabase project** ([Create one here](https://supabase.com))
- (Optional) A **GitHub Personal Access Token** or GitHub App for webhook features

### Backend Setup

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create your environment file
cp .env.example .env  # Or create manually (see Environment Variables below)

# Run the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

### Frontend Setup

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Create your environment file
# Add NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_KEY to .env.local

# Run the development server
npm run dev
```

The app will be available at `http://localhost:3000`.

### Environment Variables

#### Backend (`backend/.env`)
```env
# Required
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_service_role_key

# GitHub Integration (optional — for webhook/QC features)
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# GitHub App Auth (alternative to PAT)
GITHUB_APP_ID=your_app_id
GITHUB_PRIVATE_KEY_PATH=/path/to/private-key.pem
GITHUB_INSTALLATION_ID=your_installation_id
```

#### Frontend (`frontend/.env.local`)
```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_KEY=your_supabase_anon_key
```

### Database Setup

Run the SQL schema from `schema.sql` in your Supabase SQL editor to create all tables, then run migrations:

```sql
-- Run in Supabase SQL Editor:
-- 1. Execute schema.sql (main tables)
-- 2. Execute migrations/001_add_project_documents_table.sql
```

Populate the status tables with initial data:

```sql
-- Task statuses
INSERT INTO task_status (status_name, order_index) VALUES
  ('To Do', 1), ('In Progress', 2), ('In Review', 3), ('Completed', 4);

-- Story statuses
INSERT INTO story_status (status_name, order_index) VALUES
  ('Draft', 1), ('In Progress', 2), ('Completed', 3);

-- Project statuses
INSERT INTO project_status (status_name, order_index) VALUES
  ('Active', 1), ('On Hold', 2), ('Completed', 3);

-- Roles
INSERT INTO roles (role_name) VALUES ('Admin'), ('Developer');
```

---

## 📡 API Reference

### `POST /generate` — Generate User Stories & Tasks

**Content-Type:** `multipart/form-data`

| Field | Type | Required | Description |
|---|---|---|---|
| `requirements` | `string` | No* | Raw text requirements |
| `files` | `File[]` | No* | PDF or DOCX files |
| `project_id` | `string` | No | Custom project identifier |
| `max_iterations` | `int` | No | Validation loop limit (default: 3, max: 10) |
| `project_context` | `string` | No | JSON string with project metadata |

*At least one of `requirements` or `files` must be provided.

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/generate \
  -F "requirements=Build an e-commerce platform with user auth, product catalog, and checkout" \
  -F "files=@requirements.pdf" \
  -F "max_iterations=3" \
  -F 'project_context={"industry":"retail","tech_stack":["React","Node.js","PostgreSQL"]}'
```

### `POST /api/github-webhook` — GitHub PR Webhook

Configure your GitHub repository webhook to point to this endpoint with the `pull_request` event. The system will:
1. Verify the webhook signature
2. Extract the task ID from the PR title/branch
3. Move the task to "In Review"
4. Run AI QC analysis on the code diff
5. Post a review comment on the PR

---

## 📁 Project Structure

```
Jod-Capstone/
├── README.md
├── schema.sql                          # Full database schema
│
├── backend/
│   ├── main.py                         # FastAPI app, endpoints, webhook handler
│   ├── workflow.py                     # LangGraph StateGraph definition
│   ├── state.py                        # ProjectManagementState TypedDict
│   ├── constants.py                    # User story JSON schema
│   ├── utils.py                        # Type safety utilities
│   ├── document_utils.py              # PDF/DOCX text extraction
│   ├── user_story.py                  # Workflow test runner
│   ├── requirements.txt               # Python dependencies
│   ├── sample-response.json           # Example API response
│   ├── agents/
│   │   ├── generation_agent.py        # Multimodal story generation (Gemini)
│   │   ├── validation_agent.py        # Story validation & scoring
│   │   ├── task_agent.py              # Task decomposition from stories
│   │   ├── supabase_agent.py          # Database persistence
│   │   └── qc_agent.py               # GitHub PR code review
│   └── migrations/
│       └── 001_add_project_documents_table.sql
│
└── frontend/
    ├── package.json
    ├── next.config.ts
    ├── tsconfig.json
    ├── app/
    │   ├── layout.tsx                  # Root layout (ThemeProvider + AuthGuard)
    │   ├── page.tsx                    # Redirect to /landing
    │   ├── globals.css                 # Global styles
    │   ├── landing/page.tsx            # Marketing landing page
    │   ├── login/page.tsx              # Authentication page
    │   ├── menu/page.tsx               # Main hub / navigation
    │   ├── projects/page.tsx           # Project list
    │   ├── requirements/page.tsx       # AI agent form (standalone)
    │   ├── dashboard/page.tsx          # SPA dashboard layout
    │   └── board/
    │       ├── page.tsx                # Redirect to /projects
    │       └── [projectId]/page.tsx    # Dynamic Kanban board
    ├── components/
    │   ├── KanbanBoard.tsx             # Board orchestrator
    │   ├── KanbanColumn.tsx            # Status column with D&D
    │   ├── KanbanCard.tsx              # Draggable task card
    │   ├── AddTaskModal.tsx            # Task creation form
    │   ├── TaskDetailsModal.tsx        # Task detail view + edit/delete
    │   ├── RequirementsContent.tsx     # AI requirements form
    │   ├── ProjectDetailsModal.tsx     # Project info modal
    │   ├── AuthGuard.tsx               # Route protection
    │   ├── FloatingNav.tsx             # Floating navigation bar
    │   ├── FloatingUtilityBar.tsx      # Theme toggle + sign out
    │   ├── MainLayout.tsx              # Dashboard shell
    │   ├── Navbar.tsx                  # Top navigation
    │   ├── SignOutButton.tsx           # Sign out component
    │   └── theme-provider.tsx          # next-themes wrapper
    ├── hooks/
    │   └── useKanban.ts                # Kanban data hook (Supabase CRUD)
    ├── lib/
    │   ├── supabase.ts                 # Supabase client init
    │   └── utils.ts                    # Tailwind merge utilities
    └── types/
        └── kanban.ts                   # TypeScript interfaces
```

---

## 📜 License

This project was built as a capstone project. All rights reserved.
