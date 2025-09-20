"""
User Story Generation and Validation Agents for AI Project Management System
Using LangGraph State Management and Gemini-2.0-flash - MODULARIZED VERSION
"""

import json
import os
from typing import Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
# Import modular components with fallback for direct execution
try:
    # Try relative imports (when imported as module)
    from .workflow import create_story_workflow
    from .document_utils import create_multimodal_documentation
except ImportError:
    # Fallback to absolute imports (when run directly)
    from workflow import create_story_workflow
    from document_utils import create_multimodal_documentation

# Import Supabase agent
try:
    from agents.supabase_agent import SupabaseWorkflowAgent
except ImportError:
    # Fallback for when agents is not in path
    try:
        from agents.supabase_agent import SupabaseWorkflowAgent
    except ImportError:
        SupabaseWorkflowAgent = None

# ==================== TEST RUNNER ====================

def test_multimodal_workflow(
    primary_requirements: str,
    document_path: Optional[str] = None,
    project_context: Optional[Dict] = None,
    max_iterations: int = 3
) -> Dict:
    """
    Test the multimodal workflow with given requirements and optional document.
    
    Args:
        primary_requirements: Main text requirements (user input)
        document_path: Optional path to supporting document (PDF, DOCX, TXT)
        project_context: Optional project metadata
        max_iterations: Maximum validation iterations
        
    Returns:
        Dict with results including user stories and validation metrics
    """
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    # Get API key
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    # Create multimodal documentation
    documentation = create_multimodal_documentation(
        primary_requirements=primary_requirements,
        document_path=document_path,
        title="Test Multimodal Requirements"
    )
    
    # Setup project context
    default_context = {
        "industry": "Technology",
        "team_size": 8,
        "tech_stack": ["Python", "React", "PostgreSQL"],
        "timeline": "4 months",
        "budget": "medium"
    }
    if project_context:
        default_context.update(project_context)
    
    # Create initial state
    initial_state = {
        "project_id": f"TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "client_requirements": "",  # Empty - using documentation
        "documentation": documentation,
        "project_context": default_context,
        "current_phase": "story_generation",
        "iteration_count": 0,
        "timestamp": datetime.now().isoformat()
    }
    
    # Run workflow
    workflow = create_story_workflow(gemini_api_key, max_iterations)
    app = workflow.compile()
    
    print(f"🚀 Testing multimodal workflow...")
    print(f"📝 Primary requirements: {len(primary_requirements)} chars")
    if document_path:
        print(f"📄 Document: {document_path}")
    
    final_result = None
    iterations = []
    
    for output in app.stream(initial_state):
        for key, value in output.items():
            final_result = value
            
            if key == "generate_stories":
                iteration = value.get("iteration_count", 0)
                story_count = len(value.get('user_stories', []))
                print(f"📝 Iteration {iteration + 1}: Generated {story_count} stories")
            
            elif key == "validate_stories":
                iteration = value.get("iteration_count", 0)
                status = value.get('validation_status', 'unknown')
                score = value.get('validation_score', 0)
                
                iterations.append({
                    "iteration": iteration,
                    "status": status,
                    "score": score,
                    "story_count": len(value.get('user_stories', []))
                })
                
                print(f"✅ Iteration {iteration}: {status} (Score: {score:.1f}/100)")
            
            elif key == "save_to_supabase":
                storage_success = value.get('storage_success', False)
                if storage_success:
                    supabase_id = value.get('supabase_project_id')
                    print(f"💾 Data saved to Supabase (ID: {supabase_id})")
                else:
                    storage_error = value.get('storage_error', 'Unknown error')
                    print(f"⚠️ Supabase storage failed: {storage_error}")
            
            elif key == "project_complete":
                print("🎉 Project workflow completed!")
    
    # Return comprehensive results
    if final_result and final_result.get('user_stories'):
        return {
            "success": True,
            "workflow_results": {
                "iterations": iterations,
                "final_score": final_result.get('validation_score', 0),
                "final_status": final_result.get('validation_status'),
                "total_iterations": len(iterations)
            },
            "user_stories": final_result['user_stories'],
            "tasks": final_result.get('tasks', []),
            "multimodal_metadata": final_result.get('multimodal_metadata', {}),
            "processing_time": final_result.get('processing_time', {}),
            "supabase_storage": {
                "success": final_result.get('storage_success', False),
                "project_id": final_result.get('supabase_project_id'),
                "error": final_result.get('storage_error')
            },
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "story_count": len(final_result['user_stories']),
                "task_count": len(final_result.get('tasks', [])),
                "validation_score": final_result.get('validation_score', 0)
            }
        }
    else:
        return {
            "success": False,
            "error": final_result.get('last_error', 'Unknown error occurred'),
            "final_state": final_result
        }

# ==================== USAGE EXAMPLES ====================

if __name__ == "__main__":
    
    # Example 1: Text + PDF (Multimodal)
    primary_text = """
        We're building an exclusive online marketplace called 'ArtisanCraft' for high-end, custom-made furniture. Our vision is to connect skilled artisans directly with customers who appreciate unique, handcrafted pieces.

        The experience needs to feel premium and seamless. The most important features are:

        1.  **A beautiful gallery:** Customers need to be able to browse through different furniture pieces made by our artisans. It should be very visual.
        2.  **The customization tool:** This is our main selling point. Customers must be able to select a base furniture design and customize it. For a chair, for example, they should be able to choose the type of wood, the fabric for the upholstery, and even the finish. As they make changes, the price should update in real-time.
        3.  **Artisan Portfolios:** Each artisan needs a profile page where they can showcase their work, share their story, and manage their product listings.
        4.  **A simple, secure checkout:** The payment process has to be straightforward and build trust.

        We're targeting a launch in 6 months, so we need to focus on getting these core features right.
    """
    
    # Path to a sample PDF (create a sample or use None for text-only)
    sample_pdf_path = "requirements-doc.pdf"  # Set to actual PDF path if you have one
    # sample_pdf_path = None  # Use this for text-only testing
    
    try:
        # Run the test
        results = test_multimodal_workflow(
            primary_requirements=primary_text,
            document_path=sample_pdf_path if os.path.exists(sample_pdf_path or "") else None,
            project_context={
                "industry": "E-commerce / Retail Technology",
                "team_size": 6,
                "tech_stack": ["MongoDB", "Express.js", "React", "Node.js"],
                "timeline": "6 months",
                "budget": "High"
            },
            max_iterations=3
        )
        
        if results["success"]:
            print("\n" + "="*80)
            print("🎉 WORKFLOW COMPLETED SUCCESSFULLLY")
            print("="*80)
            print(f"Final Score: {results['workflow_results']['final_score']:.1f}/100")
            print(f"Total Iterations: {results['workflow_results']['total_iterations']}")
            print(f"Stories Generated: {results['metadata']['story_count']}")
            
            # Show multimodal metadata
            mm_metadata = results.get("multimodal_metadata", {})
            if mm_metadata:
                print(f"\n📊 Multimodal Analysis:")
                print(f"  - Source Distribution: {mm_metadata.get('source_distribution', {})}")
                print(f"  - Stories with Primary Coverage: {mm_metadata.get('stories_with_primary_coverage', 0)}")
                print(f"  - Stories with Document Coverage: {mm_metadata.get('stories_with_document_coverage', 0)}")
            
            # Show first few stories
            print(f"\n📝 Sample User Stories:")
            for i, story in enumerate(results["user_stories"][:3]):
                print(f"\n{i+1}. {story['id']}: {story['title']}")
                print(f"   Priority: {story['priority']} | Points: {story['estimated_points']}")
                print(f"   Acceptance Criteria: {len(story['acceptance_criteria'])} items")

            # Show Supabase storage results
            supabase_info = results.get("supabase_storage", {})
            if supabase_info.get("success"):
                print(f"\n� Project automatically saved to Supabase with ID: {supabase_info['project_id']}")
            else:
                print(f"\n⚠️ Supabase storage: {supabase_info.get('error', 'Not attempted')}")
    
        else:
            print("❌ WORKFLOW FAILED")
            print(f"Error: {results.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()