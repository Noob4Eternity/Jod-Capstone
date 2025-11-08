"""FastAPI service exposing user story generation from text or PDF.

Endpoints:
- POST /generate/text : Provide raw requirements text (and optional context) to get stories.
- POST /generate/pdf  : Upload a PDF file (multipart) plus optional context.
- POST /generate     : Unified endpoint supporting text + PDF in single request.

Implementation uses the updated multimodal workflow for consistent processing.
"""
import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Body, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import tempfile
from datetime import datetime
import uvicorn
import json
import hmac
import hashlib
from github import Github, GithubIntegration
from supabase import create_client, Client
from agents.qc_agent import QCAgent

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Get Gemini API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please set it in your .env file.")

# Import the updated multimodal functions
from user_story import test_multimodal_workflow
from document_utils import create_multimodal_documentation, _extract_text_from_file
from workflow import create_story_workflow

app = FastAPI(title="User Story Generation API", version="0.2.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# ------------- MODELS -------------

class TextGenerationRequest(BaseModel):
    project_id: Optional[str] = Field(default_factory=lambda: f"PRJ-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}")
    requirements: str = Field(..., description="Raw requirements text")
    project_context: Optional[Dict[str, Any]] = Field(default=None, description="Optional project context metadata")
    max_iterations: int = Field(3, ge=1, le=10)

class GenerationResponse(BaseModel):
    success: bool
    project_id: str
    user_stories: Optional[list]
    tasks: Optional[list]  # Now included
    validation_score: Optional[float]
    iterations: Optional[int]
    status: Optional[str]
    multimodal_metadata: Optional[dict] = None  # New field
    source_info: Optional[dict] = None  # New field
    supabase_storage: Optional[dict] = None  # New field for Supabase results
    error: Optional[str] = None

# ------------- HELPERS -------------

def _run_multimodal_workflow(
    primary_requirements: str,
    document_path: Optional[str] = None,
    project_context: Optional[Dict[str, Any]] = None,
    project_id: Optional[str] = None,
    max_iterations: int = 3
) -> Dict[str, Any]:
    """Run the multimodal workflow with proper error handling."""
    
    if not project_id:
        project_id = f"API-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    try:
        # Use the test_multimodal_workflow function which handles everything
        results = test_multimodal_workflow(
            primary_requirements=primary_requirements,
            document_path=document_path,
            project_context=project_context,
            max_iterations=max_iterations
        )
        
        if results["success"]:
            return {
                "success": True,
                "project_id": project_id,
                "user_stories": results["user_stories"],
                "tasks": results.get("tasks", []),  # Include tasks
                "validation_score": results["workflow_results"]["final_score"],
                "iterations": results["workflow_results"]["total_iterations"],
                "status": results["workflow_results"]["final_status"],
                "multimodal_metadata": results.get("multimodal_metadata", {}),
                "processing_time": results.get("processing_time", {}),
                "supabase_storage": results.get("supabase_storage", {})  # Include Supabase results
            }
        else:
            return {
                "success": False,
                "project_id": project_id,
                "error": results.get("error", "Unknown error occurred"),
                "user_stories": None,
                "tasks": None,
                "validation_score": None,
                "iterations": None,
                "status": "failed"
            }
            
    except Exception as e:
        return {
            "success": False,
            "project_id": project_id,
            "error": f"Workflow execution failed: {str(e)}",
            "user_stories": None,
            "tasks": None,
            "validation_score": None,
            "iterations": None,
            "status": "error"
        }

# ------------- ENDPOINTS -------------

@app.post("/generate", response_model=GenerationResponse)
async def generate_unified(
    # Optional text requirements
    requirements: Optional[str] = Form(None, description="Text requirements (optional if PDF provided)"),
    
    # Optional PDF files (can upload multiple)
    files: List[UploadFile] = File(default=[], description="PDF/DOCX files containing requirements (optional if text provided)"),
    
    # Optional metadata
    project_id: Optional[str] = Form(default=None, description="Project identifier"),
    max_iterations: int = Form(default=3, ge=1, le=10, description="Maximum validation iterations"),
    project_context: Optional[str] = Form(default=None, description="Project context as JSON string"),
):
    """
    Unified endpoint for generating user stories and tasks from text and/or PDF/DOCX files.
    
    Supports multiple input combinations:
    - Text only
    - PDF/DOCX only (single file)
    - Text + PDF/DOCX (multimodal - recommended)
    
    Returns both user stories AND development tasks.
    """
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
    
    # Validate that at least one input is provided
    has_text = requirements and requirements.strip()
    has_pdfs = files and len(files) > 0
    
    if not has_text and not has_pdfs:
        raise HTTPException(
            status_code=400,
            detail="At least one input is required: either 'requirements' text or PDF 'files'"
        )
    
    # Validate PDF files and get first one (for now, support single PDF)
    document_path = None
    if has_pdfs:
        pdf_file = files[0]  # Use first file
        file_extension = pdf_file.filename.lower().split('.')[-1]
        if file_extension not in ['pdf', 'docx']:
            raise HTTPException(
                status_code=400,
                detail=f"File '{pdf_file.filename}' is not supported. Only PDF and DOCX files are supported."
            )
        
        # Save file to temporary location with correct extension
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as tmp:
                content = await pdf_file.read()
                tmp.write(content)
                document_path = tmp.name
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process {file_extension.upper()} file: {str(e)}")
    
    # Parse project context
    ctx = None
    if project_context:
        try:
            ctx = json.loads(project_context)
        except json.JSONDecodeError:
            # Treat as plain text if not valid JSON
            ctx = {"description": project_context}
    
    # Generate project ID if not provided
    if not project_id:
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        if has_text and has_pdfs:
            project_id = f"API-MULTIMODAL-{timestamp}"
        elif has_pdfs:
            project_id = f"API-PDF-{timestamp}"
        else:
            project_id = f"API-TEXT-{timestamp}"
    
    try:
        # Run multimodal workflow
        result = _run_multimodal_workflow(
            primary_requirements=requirements or "",
            document_path=document_path,
            project_context=ctx,
            project_id=project_id,
            max_iterations=max_iterations
        )
        
        # Clean up temporary PDF file
        if document_path and os.path.exists(document_path):
            try:
                os.unlink(document_path)
            except:
                pass  # Ignore cleanup errors
        
        # Add source info for response
        result["source_info"] = {
            "text_provided": has_text,
            "pdf_provided": has_pdfs,
            "pdf_filename": files[0].filename if has_pdfs else None,
            "multimodal": has_text and has_pdfs,
            "supported_formats": ["pdf", "docx"]
        }
        
        # If Supabase storage was successful, use the Supabase UUID as the project_id
        if result.get("supabase_storage", {}).get("success") and result.get("supabase_storage", {}).get("project_id"):
            result["project_id"] = result["supabase_storage"]["project_id"]
            print(f"Using Supabase UUID as project_id: {result['project_id']}")
        
        return GenerationResponse(**result)
        
    except Exception as e:
        # Cleanup on error
        if document_path and os.path.exists(document_path):
            try:
                os.unlink(document_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/text", response_model=GenerationResponse)
async def generate_from_text(payload: TextGenerationRequest):
    """Legacy endpoint for text-only generation (backward compatibility)."""
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
    
    try:
        result = _run_multimodal_workflow(
            primary_requirements=payload.requirements,
            document_path=None,
            project_context=payload.project_context,
            project_id=payload.project_id,
            max_iterations=payload.max_iterations
        )
        
        result["source_info"] = {
            "text_provided": True,
            "pdf_provided": False,
            "multimodal": False
        }
        
        # If Supabase storage was successful, use the Supabase UUID as the project_id
        if result.get("supabase_storage", {}).get("success") and result.get("supabase_storage", {}).get("project_id"):
            result["project_id"] = result["supabase_storage"]["project_id"]
        
        return GenerationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/pdf", response_model=GenerationResponse)
async def generate_from_pdf(
    file: UploadFile = File(...),
    project_id: Optional[str] = Form(None),
    max_iterations: int = Form(3),
    project_context: Optional[str] = Form(None)
):
    """Legacy endpoint for PDF/DOCX-only generation (backward compatibility)."""
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")

    file_extension = file.filename.lower().split('.')[-1]
    if file_extension not in ['pdf', 'docx']:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX file uploads are supported")

    document_path = None
    try:
        # Save file to temporary location with correct extension
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as tmp:
            content = await file.read()
            tmp.write(content)
            document_path = tmp.name

        # Parse project context
        ctx = None
        if project_context:
            try:
                ctx = json.loads(project_context)
            except Exception:
                ctx = {"raw_context": project_context}

        # Run workflow with empty primary requirements (PDF-only)
        result = _run_multimodal_workflow(
            primary_requirements="",  # Empty - PDF only
            document_path=document_path,
            project_context=ctx,
            project_id=project_id,
            max_iterations=max_iterations
        )
        
        result["source_info"] = {
            "text_provided": False,
            "pdf_provided": True,
            "pdf_filename": file.filename,
            "multimodal": False
        }
        
        # If Supabase storage was successful, use the Supabase UUID as the project_id
        if result.get("supabase_storage", {}).get("success") and result.get("supabase_storage", {}).get("project_id"):
            result["project_id"] = result["supabase_storage"]["project_id"]

        return GenerationResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temporary file
        if document_path and os.path.exists(document_path):
            try:
                os.unlink(document_path)
            except:
                pass

# ------------- UTILITY ENDPOINTS -------------

@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.2.0", "features": ["multimodal", "tasks"]}

@app.get("/")
async def root():
    return {
        "message": "User Story Generation API with Multimodal Support",
        "version": "0.2.0",
        "endpoints": {
            "unified": "/generate (supports text + PDF/DOCX in single request)",
            "text_only": "/generate/text (legacy)",
            "pdf_docx_only": "/generate/pdf (legacy - supports PDF and DOCX)",
            "save_to_supabase": "/save-to-supabase (manual Supabase storage)",
            "health": "/health"
        },
        "features": [
            "Multimodal input processing (text + PDF/DOCX)",
            "User story generation with validation",
            "Development task generation",
            "Automatic Supabase storage integration",
            "Source traceability",
            "Iterative improvement"
        ],
        "docs": "/docs"
    }

# ------------- GITHUB WEBHOOK ENDPOINT -------------

def verify_github_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify GitHub webhook signature for security."""
    if not signature:
        return False

    # GitHub sends signature as "sha256=<hash>"
    if not signature.startswith("sha256="):
        return False

    expected_signature = signature.split("=", 1)[1]
    computed_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_signature, computed_signature)

def get_github_client():
    """Initialize GitHub client supporting both PAT and GitHub App authentication."""
    # Try GitHub App first (preferred for production)
    app_id = os.getenv("GITHUB_APP_ID")
    private_key_path = os.getenv("GITHUB_PRIVATE_KEY_PATH")
    installation_id = os.getenv("GITHUB_INSTALLATION_ID")

    if app_id and private_key_path and installation_id and os.path.exists(private_key_path):
        try:
            with open(private_key_path, 'r') as key_file:
                private_key = key_file.read()

            integration = GithubIntegration(app_id, private_key)
            # Get access token for the specific installation
            access_token = integration.get_access_token(installation_id).token
            print("[GITHUB] Using GitHub App authentication")
            return Github(access_token)
        except Exception as e:
            print(f"[GITHUB] GitHub App setup failed: {e}")
            print("[GITHUB] Falling back to Personal Access Token")

    # Fall back to Personal Access Token
    token = os.getenv("GITHUB_TOKEN")
    if token and token != "your_github_personal_access_token":  # Check it's not placeholder
        print("[GITHUB] Using Personal Access Token authentication")
        return Github(token)
    else:
        raise ValueError("No valid GitHub authentication configured. Set GITHUB_TOKEN or GITHUB_APP_ID+GITHUB_PRIVATE_KEY_PATH+GITHUB_INSTALLATION_ID")

def extract_task_id_from_pr(pr_title: str, branch_name: str) -> Optional[str]:
    """Extract task ID (e.g., 'T001') from PR title or branch name."""
    import re

    # Look for patterns like T001, TASK-001, etc.
    patterns = [
        r'\bT\d{3}\b',  # T001
        r'\bTASK-\d{3}\b',  # TASK-001
        r'\btask-\d{3}\b',  # task-001
        r'\b\d{3}\b'  # Just 001 (fallback)
    ]

    # Check PR title first
    for pattern in patterns:
        match = re.search(pattern, pr_title, re.IGNORECASE)
        if match:
            return match.group().upper().replace('TASK-', 'T')

    # Check branch name
    for pattern in patterns:
        match = re.search(pattern, branch_name, re.IGNORECASE)
        if match:
            return match.group().upper().replace('TASK-', 'T')

    return None

async def move_task_to_review(
    task_id: str,
    pr_number: int,
    pr_url: str,
    supabase_client: Client,
    project_id: Optional[str] = None
) -> bool:
    """
    Move a task from 'In Progress' (status_id=2) to 'In Review' (status_id=3).
    Only moves tasks that are currently in 'In Progress' status.
    
    Args:
        task_id: The task_id field value (e.g., 'T001')
        pr_number: GitHub PR number
        pr_url: GitHub PR URL
        supabase_client: Supabase client instance
        project_id: Optional project UUID to filter tasks by project
    
    Returns:
        True if task was successfully moved, False otherwise
    """
    try:
        # Find task by task_id, optionally filtered by project
        if project_id:
            # Query with project filter - join through user_stories
            task_query = supabase_client.table("tasks").select(
                "*, user_stories!inner(project_id)"
            ).eq("task_id", task_id).eq("user_stories.project_id", project_id).execute()
        else:
            # Query without project filter (legacy behavior)
            task_query = supabase_client.table("tasks").select("*").eq("task_id", task_id).execute()
        
        if not task_query.data:
            if project_id:
                print(f"[TASK-MOVE] Task {task_id} not found in project {project_id}")
            else:
                print(f"[TASK-MOVE] Task {task_id} not found")
            return False
        
        if len(task_query.data) > 1:
            print(f"[TASK-MOVE] ⚠️  Found {len(task_query.data)} tasks with task_id={task_id}")
            if not project_id:
                print(f"[TASK-MOVE] ⚠️  Multiple tasks found! Consider linking repository to project for accurate task selection.")
        
        task = task_query.data[0]
        task_uuid = task["id"]
        current_status = task["status_id"]
        
        # Map status IDs to names for better logging
        status_names = {
            1: "To Do",
            2: "In Progress",
            3: "In Review",
            4: "Completed"
        }
        current_status_name = status_names.get(current_status, f"Unknown ({current_status})")
        
        # Only move if currently in "In Progress" (status_id = 2)
        if current_status == 3:
            print(f"[TASK-MOVE] ℹ️  Task {task_id} is already in 'In Review' status (PR #{pr_number})")
            return True  # Already in the correct status - consider it a success
        elif current_status != 2:
            print(f"[TASK-MOVE] ⚠️  Task {task_id} cannot be moved to Review - current status: {current_status_name}")
            print(f"[TASK-MOVE] Tasks must be in 'In Progress' status to be automatically moved to Review")
            return False
        
        # Update task status to "In Review" (status_id = 3)
        update_result = supabase_client.table("tasks").update({
            "status_id": 3  # In Review
        }).eq("id", task_uuid).execute()
        
        if update_result.data:
            print(f"[TASK-MOVE] ✓ Task {task_id} moved to 'In Review' (PR #{pr_number})")
            print(f"[TASK-MOVE] PR URL: {pr_url}")
            return True
        else:
            print(f"[TASK-MOVE] Failed to update task {task_id}")
            return False
            
    except Exception as e:
        print(f"[TASK-MOVE] Error moving task to review: {str(e)}")
        return False

async def process_github_webhook_background(
    payload: Dict[str, Any],
    supabase_url: str,
    supabase_key: str,
    gemini_api_key: str
):
    """Background task to process GitHub webhook and run QC analysis."""
    try:
        print("[WEBHOOK] Starting background processing...")

        # Extract PR information
        pr_data = payload.get("pull_request", {})
        pr_action = payload.get("action", "")
        
        if not pr_data:
            print("[WEBHOOK] No pull_request data in payload")
            return

        pr_number = pr_data.get("number")
        pr_title = pr_data.get("title", "")
        branch_name = pr_data.get("head", {}).get("ref", "")
        repo_full_name = payload.get("repository", {}).get("full_name")

        if not all([pr_number, repo_full_name]):
            print("[WEBHOOK] Missing PR number or repo name")
            return

        print(f"[WEBHOOK] Processing PR #{pr_number} in {repo_full_name}")
        print(f"[WEBHOOK] PR Action: {pr_action}")
        
        # Initialize Supabase client early
        supabase_client: Client = create_client(supabase_url, supabase_key)
        
        # Optional: Validate repository is associated with a project
        # This provides an additional security layer
        project_id = None
        project_with_repo = supabase_client.table("projects").select("id", "name").eq("github_repo_full_name", repo_full_name).execute()
        if project_with_repo.data:
            project_info = project_with_repo.data[0]
            project_id = project_info['id']
            print(f"[WEBHOOK] ✓ Repository linked to project: {project_info['name']} ({project_id})")
        else:
            print(f"[WEBHOOK] ⚠️  Repository {repo_full_name} not explicitly linked to any project")
            print(f"[WEBHOOK] ⚠️  Will search for task across ALL projects (may find wrong task if duplicates exist!)")
            # Still process the webhook, but log the warning
        print(f"[WEBHOOK] Title: {pr_title}")
        print(f"[WEBHOOK] Branch: {branch_name}")

        # Extract task ID
        task_id = extract_task_id_from_pr(pr_title, branch_name)
        if not task_id:
            print(f"[WEBHOOK] Could not extract task ID from title '{pr_title}' or branch '{branch_name}'")
            return

        print(f"[WEBHOOK] Extracted task ID: {task_id}")
        
        # Check current task status before attempting to move
        task_check = supabase_client.table("tasks").select("task_id, status_id, title").eq("task_id", task_id).execute()
        if task_check.data:
            current_task = task_check.data[0]
            status_names = {1: "To Do", 2: "In Progress", 3: "In Review", 4: "Completed"}
            current_status_name = status_names.get(current_task["status_id"], "Unknown")
            print(f"[WEBHOOK] Current task status: {current_status_name} (status_id: {current_task['status_id']})")
            print(f"[WEBHOOK] Task title: {current_task['title']}")
        
        # Only move task to "In Review" when PR is first opened (not on updates/syncs)
        if pr_action == "opened":
            print(f"[WEBHOOK] PR is being opened - attempting to move task to 'In Review'")
            pr_url = pr_data.get("html_url")
            move_success = await move_task_to_review(task_id, pr_number, pr_url, supabase_client, project_id)
            
            if not move_success:
                print(f"[WEBHOOK] ⚠️  Task status was not updated (see details above)")
        else:
            print(f"[WEBHOOK] PR action is '{pr_action}' - skipping task status update (only 'opened' triggers status change)")
        
        print(f"[WEBHOOK] Continuing with QC analysis...")

        # Initialize GitHub client
        github_client = get_github_client()

        # Get repository and PR
        repo = github_client.get_repo(repo_full_name)
        pr = repo.get_pull(pr_number)

        # Get code diff
        diff = pr.get_files()
        code_diff = ""
        for file in diff:
            if file.patch:
                code_diff += f"File: {file.filename}\n"
                code_diff += f"Status: {file.status}\n"
                code_diff += f"Changes: +{file.additions} -{file.deletions}\n"
                code_diff += f"Patch:\n{file.patch}\n\n"

        if not code_diff.strip():
            print("[WEBHOOK] No code changes found in PR")
            return

        print(f"[WEBHOOK] Retrieved code diff ({len(code_diff)} chars)")

        # Query database for task and story details
        task_query = supabase_client.table("tasks").select("*").eq("task_id", task_id).execute()
        if not task_query.data:
            print(f"[WEBHOOK] Task {task_id} not found in database")
            return

        task_details = task_query.data[0]
        story_id = task_details.get("story_id")

        if not story_id:
            print(f"[WEBHOOK] No story_id found for task {task_id}")
            return

        story_query = supabase_client.table("user_stories").select("*").eq("id", story_id).execute()
        if not story_query.data:
            print(f"[WEBHOOK] Story {story_id} not found in database")
            return

        story_details = story_query.data[0]

        print(f"[WEBHOOK] Found task: {task_details.get('title')}")
        print(f"[WEBHOOK] Found story: {story_details.get('title')}")

        # Run QC analysis
        qc_agent = QCAgent(gemini_api_key)
        review_result = qc_agent.analyze_submission(task_details, story_details, code_diff)

        print(f"[WEBHOOK] QC Analysis complete - Score: {review_result.get('qc_score')}, Status: {review_result.get('status')}")

        # Create task submission record
        submission_data = {
            "task_id": task_details["id"],
            "github_pr_url": pr_data.get("html_url"),
            "code_snippet": code_diff[:5000],  # Truncate if too long
            "notes": f"Auto-submitted from GitHub PR #{pr_number}"
        }

        submission_result = supabase_client.table("task_submissions").insert(submission_data).execute()
        submission_id = submission_result.data[0]["id"]

        # Save review to database
        review_data = {
            "submission_id": submission_id,
            "review_type": "AI",
            "status": review_result.get("status"),
            "qc_score": review_result.get("qc_score"),
            "detailed_feedback": review_result.get("detailed_feedback")
        }

        supabase_client.table("submission_reviews").insert(review_data).execute()

        # Create PR comment with results
        comment_body = f"""## 🔍 AI Quality Control Review

**Task:** {task_details.get('title')} ({task_id})
**Status:** {review_result.get('status')}
**QC Score:** {review_result.get('qc_score'):.1f}/100

### 📋 Acceptance Criteria Analysis
"""

        criteria_analysis = review_result.get("detailed_feedback", {}).get("criteria_analysis", [])
        for i, criterion in enumerate(criteria_analysis, 1):
            status_icon = "✅" if criterion.get("met") else "❌"
            comment_body += f"{i}. {status_icon} **{criterion.get('criterion')}**\n"
            comment_body += f"   {criterion.get('reasoning')}\n\n"

        comment_body += f"""### 💻 Code Quality Review
{review_result.get('detailed_feedback', {}).get('quality_review', 'No review provided')}

### 🔒 Security Review
{review_result.get('detailed_feedback', {}).get('security_review', 'No review provided')}

---
*This review was automatically generated by the AI QC Agent*
"""

        pr.create_issue_comment(comment_body)

        print("[WEBHOOK] Successfully posted review comment to PR")

    except Exception as e:
        print(f"[WEBHOOK] Error in background processing: {str(e)}")
        import traceback
        traceback.print_exc()

@app.post("/api/github-webhook")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    GitHub webhook endpoint for automated QC analysis of pull requests.

    Expects GitHub webhook payload with pull_request event.
    Verifies webhook signature and processes in background.
    """
    try:
        # Get raw request body for signature verification
        body = await request.body()

        # Verify webhook signature
        signature = request.headers.get("X-Hub-Signature-256")
        webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET")

        if not webhook_secret:
            raise HTTPException(status_code=500, detail="GITHUB_WEBHOOK_SECRET not configured")

        if not verify_github_signature(body, signature, webhook_secret):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")

        # Parse JSON payload
        payload = json.loads(body.decode())

        # Check if this is a pull request event
        if payload.get("action") not in ["opened", "synchronize", "reopened"]:
            return {"status": "ignored", "reason": f"Action '{payload.get('action')}' not processed"}

        # Get required environment variables
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not all([supabase_url, supabase_key]):
            raise HTTPException(status_code=500, detail="Missing required environment variables: SUPABASE_URL, SUPABASE_KEY")

        # Add background task
        background_tasks.add_task(
            process_github_webhook_background,
            payload,
            supabase_url,
            supabase_key,
            GEMINI_API_KEY
        )

        return {"status": "accepted", "message": "Webhook processed successfully"}

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        print(f"[WEBHOOK] Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")

@app.post("/save-to-supabase")
async def save_to_supabase_endpoint(
    project_data: Dict[str, Any] = Body(..., description="Complete project data to save to Supabase")
):
    """
    Save project data to Supabase database.
    
    This endpoint can be used to manually save project data to Supabase,
    or to save data that was generated through other means.
    """
    try:
        # Import the integrated Supabase agent
        from agents.supabase_agent import SupabaseWorkflowAgent
        
        # Initialize Supabase agent
        storage_agent = SupabaseWorkflowAgent()
        
        # Save the project data
        project_db_id = storage_agent.save_project_data(project_data)
        
        if project_db_id:
            return {
                "success": True,
                "message": "Project data saved to Supabase successfully",
                "supabase_project_id": project_db_id,
                "user_stories_saved": len(project_data.get("user_stories", [])),
                "tasks_saved": len(project_data.get("tasks", []))
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to save project data to Supabase"
            )
            
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="Supabase dependencies not available"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error saving to Supabase: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )