# ==================== ENHANCED VALIDATION AGENT (FIXED FOR ACCURATE SCORING) ====================

from typing import TypedDict, List, Dict, Optional, Any
from datetime import datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import os
import json
# Import dependencies with fallback for direct execution
try:
    # Try relative imports (when imported as module)
    from ..state import ProjectManagementState, ValidationStatus
    from ..utils import safe_string_extract
except ImportError:
    # Fallback to absolute imports (when run directly)
    from state import ProjectManagementState, ValidationStatus
    from utils import safe_string_extract

class EnhancedUserStoryValidationAgent:
    """
    Enhanced validation agent that validates against the full requirements context
    while maintaining stability fixes for the Pro model.
    """
    
    def __init__(self, gemini_api_key: str = None, temperature: float = 0.2):
        api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY must be provided either as parameter or environment variable")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            temperature=temperature,
            google_api_key=api_key
        )
        
        # CHANGED: The prompt now accepts the full, original requirements again.
        # This is critical for the agent to accurately score source coverage.
        self.validation_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are an expert QA / Agile validator for MULTIMODAL user story generation.

Your task is to validate the `GENERATED USER STORIES` against the `ORIGINAL REQUIREMENTS SOURCES`. You must ensure every part of the original requirements is covered.

Assess user stories using this weighted rubric (total 100):
1.  **Requirements & NFR Coverage (25 points):** How well do the stories cover ALL primary and document requirements?
2.  **Multimodal Source Integration (15 points):** Do the stories correctly synthesize details from both text and documents?
3.  **Completeness & Acceptance Criteria Quality (20 points):** Are the stories and their ACs clear, testable, and complete?
4.  **Format & Required Fields (15 points):** Do all stories follow the required schema?
5.  **Dependencies & Consistency (10 points):** Are dependencies logical? Are there contradictions?
6.  **Sizing & Priority Logic (10 points):** Are story points and priorities reasonable?
7.  **Technical Notes Quality (5 points):** Are technical notes helpful and relevant?

Return a detailed JSON analysis. The `validation_score` and `multimodal_analysis` scores are crucial."""
            ),
            (
                "human",
                """ORIGINAL REQUIREMENTS SOURCES:

=== PRIMARY REQUIREMENTS ===
{primary_requirements}

=== SUPPORTING DOCUMENTATION ===  
{document_content}

=== MULTIMODAL METADATA (for context) ===
{multimodal_metadata}

=== GENERATED USER STORIES (for validation) ===
{stories}

INSTRUCTIONS:
Validate the generated stories against ALL original sources. Return ONLY a JSON object with the specified keys:
- overall_valid: boolean
- validation_score: float (0-100)
- missing_requirements: string[] (List specific features from any source that were missed)
- story_issues: object mapping story ID to string[] of issues
- recommendations: string[]
- critical_issues: string[]
- warnings: string[]
- multimodal_analysis: object with source_coverage_score, integration_quality, conflict_resolution_score
"""
            ),
        ])
        
        self.parser = JsonOutputParser()

    def _safe_to_float(self, value: Any, default: float = 50.0) -> float:
        """Safely converts a value to a float, returning a default if conversion fails."""
        if value is None: return default
        try: return float(value)
        except (ValueError, TypeError): return default

    # RE-ADDED: This helper function is now needed again to get the full text.
    def _extract_requirements_from_state(self, state: ProjectManagementState) -> Dict[str, str]:
        """Extracts full requirements from state, handling both legacy and multimodal inputs."""
        primary_requirements = ""
        document_content = ""
        
        if state.get("documentation"):
            doc = state["documentation"]
            full_content = doc.get("content", "")
            
            if "=== PROJECT REQUIREMENTS (TEXT) ===" in full_content:
                parts = full_content.split("=== PROJECT REQUIREMENTS (TEXT) ===")
                if len(parts) > 1:
                    primary_section = parts[1].split("=== DOCUMENT:")[0]
                    primary_requirements = primary_section.strip()
                    
                    doc_parts = full_content.split("=== DOCUMENT:")
                    if len(doc_parts) > 1:
                        document_sections = [part.strip() for part in doc_parts[1:]]
                        document_content = "\n\n".join([f"Document: {section}" for section in document_sections])
            else:
                primary_requirements = full_content
        
        if not primary_requirements and not document_content:
            primary_requirements = state.get("client_requirements", "")
        
        return {
            "primary_requirements": primary_requirements,
            "document_content": document_content
        }

    def validate_stories(self, state: ProjectManagementState) -> ProjectManagementState:
        """Enhanced validation method with full context for accurate scoring."""
        start_time = datetime.now()
        try:
            stories = state.get("user_stories", [])
            print(f"[VALIDATION] Validating {len(stories)} stories with full context prompt...")

            if not stories:
                # Same as before
                state["validation_status"] = ValidationStatus.NEEDS_REVISION.value
                state["validation_feedback"] = ["No user stories generated to validate"]
                state["validation_score"] = 0.0
                return state

            # RE-ADDED: Get the full requirements text instead of just summaries.
            requirements_data = self._extract_requirements_from_state(state)
            multimodal_metadata = state.get("multimodal_metadata", {})

            print(f"[VALIDATION] Calling gemini-2.5-pro with {len(requirements_data['primary_requirements'])} chars of primary requirements...")

            try:
                chain = self.validation_prompt | self.llm | self.parser
                
                # CHANGED: Pass the full requirements and stories to the prompt.
                semantic_validation = chain.invoke({
                    "primary_requirements": requirements_data["primary_requirements"] or "No primary requirements provided",
                    "document_content": requirements_data["document_content"] or "No supporting documentation provided",
                    "multimodal_metadata": json.dumps(multimodal_metadata),
                    "stories": json.dumps(stories, indent=2)
                })
                
            except Exception as validation_error:
                # Same fallback logic
                print(f"[VALIDATION_ERROR] LLM validation failed: {validation_error}")
                semantic_validation = { "validation_score": 50.0, "overall_valid": False, "critical_issues": [f"Semantic validation failed: {str(validation_error)}"], "recommendations": ["Manual review required."], "multimodal_analysis": {}}
            
            # This logic remains the same, but now it will have accurate scores to work with.
            base_score = self._safe_to_float(semantic_validation.get("validation_score"), default=70.0)
            multimodal_analysis = semantic_validation.get("multimodal_analysis", {})

            if multimodal_analysis:
                multimodal_bonus = (
                    self._safe_to_float(multimodal_analysis.get("source_coverage_score")) +  
                    self._safe_to_float(multimodal_analysis.get("integration_quality")) +  
                    self._safe_to_float(multimodal_analysis.get("conflict_resolution_score"))
                ) / 3
                if multimodal_bonus > 70: base_score += min(10, (multimodal_bonus - 70) / 3)
            
            validation_score = max(0, min(100, base_score))
            
            # The rest of the state update logic is the same...
            if validation_score >= 80:
                validation_status = ValidationStatus.APPROVED.value
                next_phase = "generate_tasks" 
            elif validation_score >= 60:
                validation_status = ValidationStatus.NEEDS_REVISION.value
                next_phase = "story_generation"
            else:
                validation_status = ValidationStatus.NEEDS_CLARIFICATION.value
                next_phase = "requirement_parsing"

            state["validation_status"] = validation_status
            state["validation_score"] = validation_score
            state["detailed_feedback"] = semantic_validation
            state["story_issues"] = semantic_validation.get("story_issues", {})
            state["current_phase"] = next_phase if validation_status == ValidationStatus.APPROVED.value else "story_generation"

            if validation_status != ValidationStatus.APPROVED.value:
                state["iteration_count"] = state.get("iteration_count", 0) + 1

            print(f"[VALIDATION] Score: {validation_score:.1f}/100, Status: {validation_status}")
            if multimodal_analysis:
                print(f"[VALIDATION] Source Coverage: {self._safe_to_float(multimodal_analysis.get('source_coverage_score')):.1f}/100, Integration Quality: {self._safe_to_float(multimodal_analysis.get('integration_quality')):.1f}/100")

        except Exception as e:
            # Same fatal error handling
            state["last_error"] = f"Enhanced validation failed unexpectedly: {str(e)}"
            state["validation_status"] = ValidationStatus.NEEDS_REVISION.value
            state["current_phase"] = "error"
            print(f"FATAL VALIDATION ERROR: {e}")
            import traceback
            traceback.print_exc()
        
        return state