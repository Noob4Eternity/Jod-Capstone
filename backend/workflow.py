# ==================== WORKFLOW SETUP ====================

from langgraph.graph import StateGraph, END
# Import agents with fallback for direct execution
try:
    # Try relative imports (when imported as module)
    from .agents.generation_agent import MultimodalUserStoryGenerationAgent
    from .agents.validation_agent import EnhancedUserStoryValidationAgent
    from .agents.task_agent import TaskGenerationAgent
    from .agents.supabase_agent import SupabaseWorkflowAgent
    from .state import ProjectManagementState, ValidationStatus
except ImportError:
    # Fallback to absolute imports (when run directly)
    from agents.generation_agent import MultimodalUserStoryGenerationAgent
    from agents.validation_agent import EnhancedUserStoryValidationAgent
    from agents.task_agent import TaskGenerationAgent
    from agents.supabase_agent import SupabaseWorkflowAgent
    from state import ProjectManagementState, ValidationStatus

def create_story_workflow(gemini_api_key: str = None, max_iterations: int = 3) -> StateGraph:
    """Create the LangGraph workflow for story generation and validation with feedback loop"""
    
    # Initialize agents
    story_agent = MultimodalUserStoryGenerationAgent(gemini_api_key)
    validation_agent = EnhancedUserStoryValidationAgent(gemini_api_key)
    task_agent = TaskGenerationAgent(gemini_api_key)
    supabase_agent = SupabaseWorkflowAgent()
    
    # Create workflow
    workflow = StateGraph(ProjectManagementState)
    
    def initialize_iteration_tracking(state: ProjectManagementState) -> ProjectManagementState:
        """Initialize iteration tracking in state"""
        if "iteration_count" not in state:
            state["iteration_count"] = 0
        if "max_iterations" not in state:
            state["max_iterations"] = max_iterations
        return state
    
    # Add nodes
    workflow.add_node("initialize", initialize_iteration_tracking)
    workflow.add_node("generate_stories", story_agent.generate_stories)
    workflow.add_node("validate_stories", validation_agent.validate_stories)
    workflow.add_node("generate_tasks", task_agent.generate_tasks)
    workflow.add_node("save_to_supabase", supabase_agent.save_project_to_supabase)
    
    # Add placeholder nodes
    workflow.add_node("task_creation", lambda x: x)  # Placeholder
    workflow.add_node("requirement_parsing", lambda x: x)  # Placeholder
    workflow.add_node("human_review", lambda x: x)  # Placeholder
    workflow.add_node("project_complete", lambda x: x)  # Final completion node
    
    # Add edges
    workflow.add_edge("initialize", "generate_stories")
    workflow.add_edge("generate_stories", "validate_stories")
    workflow.add_edge("generate_tasks", "save_to_supabase")
    workflow.add_edge("save_to_supabase", "project_complete")
    
    # Enhanced conditional edges with feedback loop
    def determine_next_step(state: ProjectManagementState) -> str:
        validation_status = state.get("validation_status")
        iteration_count = state.get("iteration_count", 0)
        max_iter = state.get("max_iterations", max_iterations)
        validation_score = state.get("validation_score", 0)
        
        print(f"[WORKFLOW] Iteration {iteration_count}, Status: {validation_status}, Score: {validation_score:.1f}")
        
        # Check if approved - align with validation agent thresholds (80+ is approved)
        if validation_status == ValidationStatus.APPROVED.value or validation_score >= 80:
            return "approved"
        
        # If we've reached max iterations but have decent stories, proceed
        if iteration_count >= max_iter:
            if validation_score >= 70:
                print(f"[WORKFLOW] Max iterations reached, score {validation_score:.1f} is acceptable.")
                return "approved"
            else:
                print(f"[WORKFLOW] Max iterations reached, escalating to human review")
                return "max_iterations"
        
        # Check for degrading quality (score dropped significantly from previous iteration)
        previous_score = state.get("previous_validation_score", validation_score)
        if iteration_count > 0 and validation_score < previous_score - 10:
            print(f"[WORKFLOW] Score degraded from {previous_score:.1f} to {validation_score:.1f}, stopping iterations")
            if validation_score >= 60:
                return "approved"
            else:
                return "max_iterations"
        
        # Continue with revision if score suggests improvement possible
        if validation_score >= 50:
            print(f"[WORKFLOW] Score {validation_score:.1f} suggests improvement possible, iterating...")
            state["previous_validation_score"] = validation_score  # Track for next iteration
            return "needs_revision"
        else:
            print(f"[WORKFLOW] Low score {validation_score:.1f}, escalating to human review")
            return "low_quality"
    
    workflow.add_conditional_edges(
        "validate_stories",
        determine_next_step,
        {
            "approved": "generate_tasks",
            "needs_revision": "generate_stories",
            "max_iterations": "human_review",
            "low_quality": "human_review"
        }
    )
    
    # Set entry point
    workflow.set_entry_point("initialize")
    
    return workflow