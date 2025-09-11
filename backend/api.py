"""FastAPI service exposing user story generation from text or PDF.

Endpoints:
- POST /generate/text : Provide raw requirements text (and optional context) to get stories.
- POST /generate/pdf  : Upload a PDF file (multipart) plus optional context.

Implementation uses existing synchronous workflow in user_story.py for consistency.
"""
import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import tempfile
from datetime import datetime
import uvicorn

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Get Gemini API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please set it in your .env file.")

from user_story import (
    process_pdf_to_user_stories,
    create_story_workflow,
    create_structured_documentation
)

app = FastAPI(title="User Story Generation API", version="0.1.0")

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
    tasks: Optional[list]
    validation_score: Optional[float]
    iterations: Optional[int]
    status: Optional[str]
    error: Optional[str] = None

# ------------- HELPERS -------------

def _run_text_flow(req: TextGenerationRequest) -> Dict[str, Any]:
    """Run workflow using plain text requirements (no PDF)."""
    workflow = create_story_workflow(os.getenv("GEMINI_API_KEY"), req.max_iterations)
    app_graph = workflow.compile()

    initial_state = {
        "project_id": req.project_id,
        "client_requirements": req.requirements,
        "documentation": None,
        "project_context": req.project_context or {},
        "current_phase": "story_generation",
        "iteration_count": 0,
        "timestamp": datetime.utcnow().isoformat()
    }

    final_result = None
    iterations_meta = []
    for output in app_graph.stream(initial_state):
        for key, value in output.items():
            final_result = value
            if key == "validate_stories":
                iterations_meta.append({
                    "iteration": value.get("iteration_count", 0),
                    "status": value.get("validation_status"),
                    "score": value.get("validation_score")
                })

    if not final_result or not final_result.get("user_stories"):
        return {
            "success": False,
            "project_id": req.project_id,
            "error": final_result.get("last_error") if final_result else "No stories generated"
        }

    return {
        "success": True,
        "project_id": req.project_id,
        "user_stories": final_result.get("user_stories"),
        "tasks": final_result.get("tasks"),
        "validation_score": final_result.get("validation_score"),
        "iterations": len(iterations_meta),
        "status": final_result.get("validation_status")
    }

# ------------- ENDPOINTS -------------

@app.post("/generate/text", response_model=GenerationResponse)
async def generate_from_text(payload: TextGenerationRequest):
    if not os.getenv("GEMINI_API_KEY"):
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
    try:
        result = _run_text_flow(payload)
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
    if not os.getenv("GEMINI_API_KEY"):
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")

    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        ctx = None
        if project_context:
            try:
                import json
                ctx = json.loads(project_context)
            except Exception:
                ctx = {"raw_context": project_context}

        data = process_pdf_to_user_stories(
            pdf_file_path=tmp_path,
            project_context=ctx,
            max_iterations=max_iterations,
            gemini_api_key=os.getenv("GEMINI_API_KEY")
        )

        os.unlink(tmp_path)

        if not data.get("success"):
            return GenerationResponse(
                success=False,
                project_id=project_id or data.get("workflow_results", {}).get("project_id", "PDF"),
                user_stories=None,
                tasks=None,
                validation_score=None,
                iterations=data.get("workflow_results", {}).get("total_iterations"),
                status=data.get("workflow_results", {}).get("final_status"),
                error=data.get("error", "Generation failed")
            )

        return GenerationResponse(
            success=True,
            project_id=project_id or data.get("workflow_results", {}).get("project_id", "PDF"),
            user_stories=data.get("user_stories"),
            tasks=data.get("tasks"),
            validation_score=data.get("workflow_results", {}).get("final_score"),
            iterations=data.get("workflow_results", {}).get("total_iterations"),
            status=data.get("workflow_results", {}).get("final_status")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
