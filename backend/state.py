# ==================== STATE DEFINITION ====================

from typing import TypedDict, List, Dict, Optional, Any
from enum import Enum

class ValidationStatus(Enum):
    APPROVED = "approved"
    NEEDS_REVISION = "needs_revision"
    NEEDS_CLARIFICATION = "needs_clarification"

class ProjectManagementState(TypedDict):
    """Shared state for all agents in the workflow"""
    # Input - Enhanced to support documentation
    client_requirements: str  # Backward compatibility
    documentation: Optional[Dict]  # New structured documentation input
    project_id: str
    project_context: Optional[Dict]  # Industry, team size, tech stack, etc.
    
    # Generated artifacts
    parsed_requirements: Optional[Dict]
    user_stories: Optional[List[Dict]]
    previous_user_stories: Optional[List[Dict]]  # For tracking iterations
    tasks: Optional[List[Dict]]  # Generated tasks from user stories
    
    # Validation and Feedback Loop
    validation_status: Optional[str]
    validation_feedback: Optional[List[str]]
    validation_score: Optional[float]
    story_issues: Optional[Dict[str, List[str]]]  # Issues per story ID
    detailed_feedback: Optional[Dict]  # Rich feedback from validation agent
    improvement_instructions: Optional[List[str]]  # Specific instructions for next iteration
    
    # Supabase Storage
    supabase_project_id: Optional[str]  # Database ID of saved project
    storage_success: Optional[bool]  # Whether data was successfully saved
    storage_error: Optional[str]  # Any storage-related errors
    
    # Metadata
    current_phase: str
    iteration_count: int
    max_iterations: int
    last_error: Optional[str]
    processing_time: Optional[Dict[str, float]]
    timestamp: str