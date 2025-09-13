"""FastAPI service exposing user story generation from text or PDF.

Endpoints:
- POST /generate/text : Provide raw requirements text (and optional context) to get stories.
- POST /generate/pdf  : Upload a PDF file (multipart) plus optional context.
- POST /generate     : Unified endpoint supporting text + PDF in single request.

Implementation uses the updated multimodal workflow for consistent processing.
"""
import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import tempfile
from datetime import datetime
import uvicorn
import json

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Get Gemini API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please set it in your .env file.")

# Import the updated multimodal functions
from user_story import (
    test_multimodal_workflow,
    create_multimodal_documentation,
    create_story_workflow,
    _extract_text_from_file
)

app = FastAPI(title="User Story Generation API", version="0.2.0")

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
                "processing_time": results.get("processing_time", {})
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
    files: List[UploadFile] = File(default=[], description="PDF files containing requirements (optional if text provided)"),
    
    # Optional metadata
    project_id: Optional[str] = Form(default=None, description="Project identifier"),
    max_iterations: int = Form(default=3, ge=1, le=10, description="Maximum validation iterations"),
    project_context: Optional[str] = Form(default=None, description="Project context as JSON string"),
):
    """
    Unified endpoint for generating user stories and tasks from text and/or PDF files.
    
    Supports multiple input combinations:
    - Text only
    - PDF only (single file)
    - Text + PDF (multimodal - recommended)
    
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
        pdf_file = files[0]  # Use first PDF
        if not pdf_file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail=f"File '{pdf_file.filename}' is not a PDF. Only PDF files are supported."
            )
        
        # Save PDF to temporary file
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                content = await pdf_file.read()
                tmp.write(content)
                document_path = tmp.name
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")
    
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
            "multimodal": has_text and has_pdfs
        }
        
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
    """Legacy endpoint for PDF-only generation (backward compatibility)."""
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")

    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported")

    document_path = None
    try:
        # Save PDF to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
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
            "unified": "/generate (supports text + PDF in single request)",
            "text_only": "/generate/text (legacy)",
            "pdf_only": "/generate/pdf (legacy)",
            "health": "/health"
        },
        "features": [
            "Multimodal input processing (text + PDF)",
            "User story generation with validation",
            "Development task generation",
            "Source traceability",
            "Iterative improvement"
        ],
        "docs": "/docs"
    }

# ------------- TESTING ENDPOINT (OPTIONAL) -------------

@app.post("/test/multimodal")
async def test_multimodal_endpoint(
    requirements: str = Form(..., description="Test requirements text"),
    max_iterations: int = Form(default=2, description="Max iterations for testing")
):
    """Test endpoint to verify multimodal functionality works."""
    try:
        result = _run_multimodal_workflow(
            primary_requirements=requirements,
            document_path=None,
            project_context={"industry": "Technology", "team_size": 5},
            project_id="TEST-001",
            max_iterations=max_iterations
        )
        
        return {
            "test_result": "success" if result["success"] else "failed",
            "user_stories_count": len(result.get("user_stories", [])),
            "tasks_count": len(result.get("tasks", [])),
            "validation_score": result.get("validation_score"),
            "details": result
        }
    except Exception as e:
        return {
            "test_result": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )