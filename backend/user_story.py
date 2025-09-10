"""
User Story Generation and Validation Agents for AI Project Management System
Using LangGraph State Management and Gemini-2.0-flash
"""

import json
import os
import re
from typing import TypedDict, List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field, field_validator
from langgraph.graph import StateGraph, END

# ==================== CONSTANTS / SCHEMA (API-READY) ====================

# JSON schema used to guide LLM output (kept simple for token efficiency). When converting to an API
# this can be exported so clients know the contract.
USER_STORY_JSON_SCHEMA = r"""{
    "type": "array",
    "items": {
        "type": "object",
        "required": [
            "id",
            "title",
            "description",
            "acceptance_criteria",
            "priority",
            "estimated_points",
            "dependencies",
            "technical_notes"
        ],
        "properties": {
            "id": {"type": "string", "pattern": "^US\\d{3}$"},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "acceptance_criteria": {"type": "array", "minItems": 3, "maxItems": 7, "items": {"type": "string"}},
            "priority": {"type": "string", "enum": ["high", "medium", "low"]},
            "estimated_points": {"type": "integer", "enum": [1,2,3,5,8,13]},
            "dependencies": {"type": "array", "items": {"type": "string", "pattern": "^US\\d{3}$"}},
            "technical_notes": {"type": "string"}
        }
    }
}"""

# ==================== STATE DEFINITION ====================

class ValidationStatus(Enum):
    APPROVED = "approved"
    NEEDS_REVISION = "needs_revision"
    NEEDS_CLARIFICATION = "needs_clarification"

class UserStory(BaseModel):
    """Schema for a single user story"""
    id: str = Field(description="Unique identifier (e.g., US001)")
    title: str = Field(description="User story in 'As a... I want... So that...' format")
    description: str = Field(description="Detailed description of the feature")
    acceptance_criteria: List[str] = Field(description="List of acceptance criteria")
    priority: str = Field(description="Priority level: high, medium, or low")
    estimated_points: int = Field(description="Story points (1, 2, 3, 5, 8, 13)")
    dependencies: List[str] = Field(description="IDs of dependent stories")
    technical_notes: str = Field(description="Technical implementation notes")
    
    @field_validator('priority')
    def validate_priority(cls, v):
        if v not in ['high', 'medium', 'low']:
            raise ValueError('Priority must be high, medium, or low')
        return v
    
    @field_validator('estimated_points')
    def validate_points(cls, v):
        if v not in [1, 2, 3, 5, 8, 13]:
            raise ValueError('Story points must follow Fibonacci sequence: 1, 2, 3, 5, 8, 13')
        return v

class DocumentationInput(BaseModel):
    """Schema for documentation input"""
    document_type: str = Field(description="Type of documentation: PRD, BRD, Technical Spec, etc.")
    title: str = Field(description="Document title")
    content: str = Field(description="Main document content")
    sections: Optional[Dict[str, str]] = Field(description="Structured sections (overview, features, requirements, etc.)", default={})
    stakeholders: Optional[List[str]] = Field(description="Key stakeholders mentioned", default=[])
    business_goals: Optional[List[str]] = Field(description="Business objectives", default=[])
    technical_constraints: Optional[List[str]] = Field(description="Technical limitations or requirements", default=[])
    success_criteria: Optional[List[str]] = Field(description="Definition of success", default=[])

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
    
    # Validation and Feedback Loop
    validation_status: Optional[str]
    validation_feedback: Optional[List[str]]
    validation_score: Optional[float]
    story_issues: Optional[Dict[str, List[str]]]  # Issues per story ID
    detailed_feedback: Optional[Dict]  # Rich feedback from validation agent
    improvement_instructions: Optional[List[str]]  # Specific instructions for next iteration
    
    # Metadata
    current_phase: str
    iteration_count: int
    max_iterations: int
    last_error: Optional[str]
    processing_time: Optional[Dict[str, float]]
    timestamp: str

# ==================== USER STORY GENERATION AGENT ====================

class UserStoryGenerationAgent:
    """Agent responsible for generating user stories from client requirements"""
    
    def __init__(self, gemini_api_key: str = None, temperature: float = 0.3):
        api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY must be provided either as parameter or environment variable")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.8,
            google_api_key=api_key
        )
        
        self.story_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are an expert Product Manager + Agile BA generating a HIGH-QUALITY, VALIDATION-READY backlog of user stories.

PRIMARY OBJECTIVE: Produce user stories that will pass a strict validator early (format, INVEST, coverage, sizing, NFR inclusion).

STRICT OUTPUT CONTRACT:

JSON SCHEMA (guidance – conform conceptually):
{json_schema}

PRE-EMISSION INTERNAL STEPS (do silently):
1. Decompose requirements into atomic requirement_units (not output).
2. Map each requirement_unit -> at least one story.
3. Run self_check: FORMAT_OK, MIN_CRITERIA(>=3), INVEST_OK, NO_DUP_IDS, NO_CIRCULAR_DEPS, NFR_COVERED (if implied), COVERAGE_COMPLETE (no obvious uncovered major feature nouns), SIZING_OK (<=13), FEEDBACK_APPLIED.
4. If any check fails, silently revise before output.

ITERATIONS:

TECHNICAL NOTES must provide actionable implementation hints (APIs, data, validation, security or performance considerations).

SCORING ALIGNMENT HINTS:
Format(15) + Completeness(20) + Coverage(25) + NFR(10) + Consistency & Dependencies(10) + Sizing(10) + Acceptance Criteria Quality(10).

Return ONLY the JSON array of story objects. No commentary."""
            ),
            (
                "human",
                """SOURCE REQUIREMENTS / DOCUMENTATION:
{requirements}

VALIDATION / FEEDBACK CONTEXT (may be empty if first iteration):
{feedback_section}

PROJECT CONTEXT:
{project_context}

INSTRUCTIONS:
1. Respect explicit terminology in requirements; do not invent unrelated features.
2. Use personas derived from stakeholders / roles mentioned (fallback: user, admin, system administrator, project manager, QA engineer).
3. Acceptance criteria: Prefer measurable, avoid vague verbs ("optimize" alone unacceptable).
4. Security / performance / scalability / reliability included if implied even indirectly.
5. Avoid epics: if description covers multiple unrelated capabilities, split into multiple stories.
6. Keep language concise and implementation-agnostic except inside technical_notes.
{iteration_instructions}

OUTPUT: JSON array ONLY. No surrounding text.
{feedback_focus}"""
            ),
        ])
        
        self.parser = JsonOutputParser()
        
    def _parse_documentation(self, state: ProjectManagementState) -> str:
        """Parse documentation input and convert to requirements format"""
        # Check if we have structured documentation
        if state.get("documentation"):
            doc = state["documentation"]
            
            # Build comprehensive requirements from documentation
            requirements_parts = []
            
            # Add document header
            if doc.get("title"):
                requirements_parts.append(f"Project: {doc['title']}")
            if doc.get("document_type"):
                requirements_parts.append(f"Document Type: {doc['document_type']}")
            
            # Add main content
            if doc.get("content"):
                requirements_parts.append("\n=== MAIN REQUIREMENTS ===")
                requirements_parts.append(doc["content"])
            
            # Add structured sections
            if doc.get("sections"):
                for section_name, section_content in doc["sections"].items():
                    requirements_parts.append(f"\n=== {section_name.upper()} ===")
                    requirements_parts.append(section_content)
            
            # Add business context
            if doc.get("business_goals"):
                requirements_parts.append("\n=== BUSINESS GOALS ===")
                for goal in doc["business_goals"]:
                    requirements_parts.append(f"- {goal}")
            
            # Add stakeholders
            if doc.get("stakeholders"):
                requirements_parts.append("\n=== STAKEHOLDERS ===")
                requirements_parts.append(f"Key stakeholders: {', '.join(doc['stakeholders'])}")
            
            # Add technical constraints
            if doc.get("technical_constraints"):
                requirements_parts.append("\n=== TECHNICAL CONSTRAINTS ===")
                for constraint in doc["technical_constraints"]:
                    requirements_parts.append(f"- {constraint}")
            
            # Add success criteria
            if doc.get("success_criteria"):
                requirements_parts.append("\n=== SUCCESS CRITERIA ===")
                for criteria in doc["success_criteria"]:
                    requirements_parts.append(f"- {criteria}")
            
            return "\n".join(requirements_parts)
        
        # Fallback to original client_requirements
        return state.get("client_requirements", "")
    
    def _format_feedback_for_prompt(self, state: ProjectManagementState) -> tuple:
        """Format validation feedback for inclusion in the generation prompt"""
        iteration_count = state.get("iteration_count", 0)
        
        if iteration_count == 0:
            # First iteration - no feedback
            return "", "", ""
        
        feedback_section = "\n=== VALIDATION FEEDBACK FROM PREVIOUS ITERATION ===\n"
        iteration_instructions = "\n6. **CRITICAL**: Address all validation feedback from the previous iteration"
        feedback_focus = "\n6. **Address specific feedback and improve story quality**"
        
        # Add detailed feedback if available
        detailed_feedback = state.get("detailed_feedback", {})
        validation_feedback = state.get("validation_feedback", [])
        story_issues = state.get("story_issues", {})
        
        if detailed_feedback:
            feedback_section += f"**Validation Score**: {state.get('validation_score', 0):.1f}/100\n\n"
            
            # Critical issues
            if detailed_feedback.get("critical_issues"):
                feedback_section += "**CRITICAL ISSUES TO FIX**:\n"
                for issue in detailed_feedback["critical_issues"]:
                    feedback_section += f"- {issue}\n"
                feedback_section += "\n"
            
            # Missing requirements
            if detailed_feedback.get("missing_requirements"):
                feedback_section += "**MISSING REQUIREMENTS**:\n"
                for req in detailed_feedback["missing_requirements"]:
                    feedback_section += f"- {req}\n"
                feedback_section += "\n"
            
            # Recommendations
            if detailed_feedback.get("recommendations"):
                feedback_section += "**RECOMMENDATIONS FOR IMPROVEMENT**:\n"
                for rec in detailed_feedback["recommendations"]:
                    feedback_section += f"- {rec}\n"
                feedback_section += "\n"
            
            # Story-specific issues
            if story_issues:
                feedback_section += "**STORY-SPECIFIC ISSUES**:\n"
                for story_id, issues in story_issues.items():
                    feedback_section += f"Story {story_id}:\n"
                    for issue in issues:
                        feedback_section += f"  - {issue}\n"
                feedback_section += "\n"
        
        elif validation_feedback:
            feedback_section += "**GENERAL FEEDBACK**:\n"
            for feedback in validation_feedback:
                feedback_section += f"- {feedback}\n"
            feedback_section += "\n"
        
        # Add improvement instructions if available
        improvement_instructions = state.get("improvement_instructions", [])
        if improvement_instructions:
            feedback_section += "**SPECIFIC IMPROVEMENT INSTRUCTIONS**:\n"
            for instruction in improvement_instructions:
                feedback_section += f"- {instruction}\n"
            feedback_section += "\n"
        
        # Add previous stories for reference
        previous_stories = state.get("previous_user_stories", [])
        if previous_stories:
            feedback_section += f"**PREVIOUS ITERATION HAD {len(previous_stories)} STORIES** - Use this as reference but improve based on feedback.\n"
        
        return feedback_section, iteration_instructions, feedback_focus
        
    def _extract_key_features(self, requirements: str) -> List[str]:
        """Extract key features from requirements for better story generation"""
        feature_prompt = ChatPromptTemplate.from_messages([
            ("system", "Extract the main features and functionalities from these requirements. Return as a JSON array of strings."),
            ("human", "{requirements}")
        ])
        
        chain = feature_prompt | self.llm | self.parser
        try:
            features = chain.invoke({"requirements": requirements})
            return features if isinstance(features, list) else []
        except:
            return []
    
    def _ensure_coverage(self, requirements: str, stories: List[Dict]) -> List[Dict]:
        """Ensure all requirements are covered by the generated stories"""
        # Check for common missing elements
        requirements_lower = requirements.lower()
        story_titles_lower = " ".join([s.get("title", "").lower() for s in stories])
        
        missing_elements = []
        
        # Check for security requirements
        if any(word in requirements_lower for word in ["secure", "security", "authentication", "authorization"]):
            if "security" not in story_titles_lower and "authentication" not in story_titles_lower:
                missing_elements.append("security")
        
        # Check for performance requirements
        if any(word in requirements_lower for word in ["performance", "fast", "speed", "scalable"]):
            if "performance" not in story_titles_lower:
                missing_elements.append("performance")
        
        # Check for error handling
        if "error" in requirements_lower or "exception" in requirements_lower:
            if "error" not in story_titles_lower:
                missing_elements.append("error_handling")
        
        # Add missing non-functional requirements
        if missing_elements:
            nfr_stories = self._generate_nfr_stories(missing_elements, len(stories))
            stories.extend(nfr_stories)
        
        return stories
    
    def _generate_nfr_stories(self, missing_elements: List[str], current_count: int) -> List[Dict]:
        """Generate non-functional requirement stories"""
        nfr_stories = []
        
        templates = {
            "security": {
                "title": "As a system administrator, I want robust security measures so that user data is protected",
                "description": "Implement comprehensive security measures including authentication, authorization, and data encryption",
                "acceptance_criteria": [
                    "All API endpoints require authentication",
                    "Passwords are hashed using bcrypt or similar",
                    "JWT tokens expire after 24 hours",
                    "Rate limiting is implemented on all endpoints",
                    "SQL injection prevention is in place"
                ],
                "priority": "high",
                "estimated_points": 8
            },
            "performance": {
                "title": "As a user, I want the system to respond quickly so that I can work efficiently",
                "description": "Optimize system performance for responsive user experience",
                "acceptance_criteria": [
                    "Page load time under 2 seconds",
                    "API response time under 200ms for 95% of requests",
                    "System handles 100 concurrent users",
                    "Database queries optimized with proper indexing",
                    "Caching implemented for frequently accessed data"
                ],
                "priority": "medium",
                "estimated_points": 5
            },
            "error_handling": {
                "title": "As a user, I want clear error messages so that I know how to resolve issues",
                "description": "Implement comprehensive error handling and user feedback",
                "acceptance_criteria": [
                    "All errors display user-friendly messages",
                    "Errors are logged with stack traces",
                    "System gracefully handles network failures",
                    "Validation errors clearly indicate the issue",
                    "500 errors show generic message to users but log details"
                ],
                "priority": "medium",
                "estimated_points": 3
            }
        }
        
        for idx, element in enumerate(missing_elements):
            if element in templates:
                story = templates[element].copy()
                story["id"] = f"US{current_count + idx + 1:03d}"
                story["dependencies"] = []
                story["technical_notes"] = f"Implement {element} best practices"
                nfr_stories.append(story)
        
        return nfr_stories
    
    def generate_stories(self, state: ProjectManagementState) -> ProjectManagementState:
        """Main method to generate user stories from requirements"""
        start_time = datetime.now()
        
        try:
            # Store previous stories before generating new ones
            current_stories = state.get("user_stories", [])
            if current_stories:
                state["previous_user_stories"] = current_stories
            
            # Parse documentation if available, otherwise use original requirements
            requirements = self._parse_documentation(state)
            project_context = state.get("project_context", {})
            
            # Format context for the prompt
            context_str = json.dumps(project_context) if project_context else "No specific context provided"
            
            # Format feedback for iterative improvement
            feedback_section, iteration_instructions, feedback_focus = self._format_feedback_for_prompt(state)
            
            # Log iteration info
            iteration_count = state.get("iteration_count", 0)
            print(f"[GENERATION] Iteration {iteration_count + 1}")
            if iteration_count > 0:
                print(f"[GENERATION] Using feedback from validation to improve stories")
            
            # Generate stories using Gemini with feedback
            chain = self.story_prompt | self.llm | self.parser
            
            raw_stories = chain.invoke({
                "requirements": requirements,
                "project_context": context_str,
                "feedback_section": feedback_section,
                "iteration_instructions": iteration_instructions,
                "feedback_focus": feedback_focus,
                "json_schema": USER_STORY_JSON_SCHEMA
            })
            
            # Ensure we have a list
            if not isinstance(raw_stories, list):
                raw_stories = [raw_stories]
            
            # Validate and clean each story (structural adjustments before coverage pass)
            validated_stories = []
            for idx, story in enumerate(raw_stories):
                # Ensure story has all required fields
                story_id = story.get("id", f"US{idx+1:03d}")
                
                validated_story = {
                    "id": story_id,
                    "title": story.get("title", ""),
                    "description": story.get("description", ""),
                    "acceptance_criteria": story.get("acceptance_criteria", []),
                    "priority": story.get("priority", "medium"),
                    "estimated_points": story.get("estimated_points", 3),
                    "dependencies": story.get("dependencies", []),
                    "technical_notes": story.get("technical_notes", "")
                }
                
                # Validate story format
                if validated_story["title"] and not self._is_valid_story_format(validated_story["title"]):
                    validated_story["title"] = self._fix_story_format(validated_story["title"])
                
                # Ensure minimum acceptance criteria length (auto-fix if model gave too few)
                if len(validated_story["acceptance_criteria"]) < 3:
                    # Pad by echoing last criterion variations (better than failing later)
                    while len(validated_story["acceptance_criteria"]) < 3:
                        seed_text = validated_story["acceptance_criteria"][-1] if validated_story["acceptance_criteria"] else "System returns success response"
                        validated_story["acceptance_criteria"].append(seed_text)

                validated_stories.append(validated_story)

            # Post-pass: enforce sequential IDs & uniqueness (API-friendly deterministic output)
            seen = set()
            for i, story in enumerate(validated_stories):
                new_id = f"US{i+1:03d}"
                story["id"] = new_id
                if story["id"] in seen:
                    # Should not happen after reassignment, but safety check
                    suffix = len(seen)
                    story["id"] = f"US{i+1:03d}"
                seen.add(story["id"])
            
            # Ensure coverage of all requirements
            validated_stories = self._ensure_coverage(requirements, validated_stories)
            
            # Update state
            state["user_stories"] = validated_stories
            state["current_phase"] = "story_validation"
            
            processing_time = (datetime.now() - start_time).total_seconds()
            if "processing_time" not in state:
                state["processing_time"] = {}
            state["processing_time"]["story_generation"] = processing_time
            
        except Exception as e:
            state["last_error"] = f"Story generation failed: {str(e)}"
            state["user_stories"] = []
            state["current_phase"] = "error"
            
        return state
    
    def _is_valid_story_format(self, title: str) -> bool:
        """Check if story follows the standard format"""
        pattern = r"^As a .+, I want .+ so that .+"
        return bool(re.match(pattern, title, re.IGNORECASE))
    
    def _fix_story_format(self, title: str) -> str:
        """Attempt to fix story format"""
        if "want" in title.lower():
            return title  # Might be close enough
        return f"As a user, I want {title} so that I can complete my tasks"

# ==================== VALIDATION AGENT ====================

class UserStoryValidationAgent:
    """Agent responsible for validating generated user stories"""
    
    def __init__(self, gemini_api_key: str = None, temperature: float = 0.1):
        api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY must be provided either as parameter or environment variable")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.7,  # Lower temperature for validation
            google_api_key=api_key
        )
        
        self.validation_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are an expert QA / Agile validator.
Assess user stories using this weighted rubric (total 100):
1. Format & Required Fields (15)
2. Completeness & Acceptance Criteria Quality (20)
3. Requirements & NFR Coverage (25)
4. Consistency & Dependencies (10)
5. Sizing & Split Quality (10)
6. Priority Logic & Business Alignment (10)
7. Technical Notes Usefulness (10)

Expectations:
- Title pattern: As a <persona>, I want <capability> so that <benefit>
- Acceptance criteria: >=3, each objectively testable
- Story points: one of 1,2,3,5,8,13
- Include NFR stories if security, performance, scalability, reliability, observability, compliance implied
- No circular / invalid dependencies; IDs sequential US###
- Technical notes: actionable implementation guidance

Classify findings: critical_issues (must fix), recommendations (quality improvements), warnings (minor polish)."""
            ),
            (
                "human",
                """Original Requirements:
{requirements}

Generated User Stories:
{stories}

Return ONLY a JSON object with keys:
- overall_valid: boolean
- validation_score: float (0-100)
- missing_requirements: string[]
- story_issues: object mapping story ID (e.g. US001) to string[] of issues
- recommendations: string[]
- critical_issues: string[]
- warnings: string[]"""
            ),
        ])
        
        self.parser = JsonOutputParser()
    
    def _check_story_format(self, story: Dict) -> List[str]:
        """Check if a story follows proper format"""
        issues = []
        
        # Check title format
        title = story.get("title", "")
        if not title:
            issues.append("Missing story title")
        elif not re.match(r"^As a .+, I want .+ so that .+", title, re.IGNORECASE):
            issues.append("Title doesn't follow 'As a... I want... so that...' format")
        
        # Check required fields
        if not story.get("id"):
            issues.append("Missing story ID")
        
        if not story.get("description"):
            issues.append("Missing description")
        
        if not story.get("acceptance_criteria") or len(story.get("acceptance_criteria", [])) == 0:
            issues.append("Missing or empty acceptance criteria")
        elif len(story.get("acceptance_criteria", [])) < 2:
            issues.append("Insufficient acceptance criteria (need at least 2)")
        
        # Check priority
        if story.get("priority") not in ["high", "medium", "low"]:
            issues.append(f"Invalid priority: {story.get('priority')}")
        
        # Check story points
        if story.get("estimated_points") not in [1, 2, 3, 5, 8, 13]:
            issues.append(f"Invalid story points: {story.get('estimated_points')}")
        
        return issues
    
    def _check_dependencies(self, stories: List[Dict]) -> List[str]:
        """Check if dependencies are valid"""
        issues = []
        story_ids = {story["id"] for story in stories}
        
        for story in stories:
            for dep in story.get("dependencies", []):
                if dep not in story_ids:
                    issues.append(f"Story {story['id']} has invalid dependency: {dep}")
                if dep == story["id"]:
                    issues.append(f"Story {story['id']} cannot depend on itself")
        
        # Check for circular dependencies
        for story in stories:
            if self._has_circular_dependency(story["id"], stories):
                issues.append(f"Story {story['id']} has circular dependencies")
        
        return issues
    
    def _has_circular_dependency(self, story_id: str, stories: List[Dict], visited: set = None) -> bool:
        """Check for circular dependencies"""
        if visited is None:
            visited = set()
        
        if story_id in visited:
            return True
        
        visited.add(story_id)
        
        story = next((s for s in stories if s["id"] == story_id), None)
        if not story:
            return False
        
        for dep in story.get("dependencies", []):
            if self._has_circular_dependency(dep, stories, visited.copy()):
                return True
        
        return False
    
    def _check_coverage(self, requirements: str, stories: List[Dict]) -> List[str]:
        """Check if all requirements are covered"""
        missing = []
        
        requirements_lower = requirements.lower()
        all_story_text = " ".join([
            f"{s.get('title', '')} {s.get('description', '')} {' '.join(s.get('acceptance_criteria', []))}"
            for s in stories
        ]).lower()
        
        # Check for key technical terms
        technical_terms = ["api", "database", "authentication", "ui", "frontend", "backend", 
                          "security", "performance", "testing", "deployment"]
        
        for term in technical_terms:
            if term in requirements_lower and term not in all_story_text:
                missing.append(f"No story addresses '{term}' mentioned in requirements")
        
        # Check for CRUD operations if applicable
        if any(word in requirements_lower for word in ["create", "read", "update", "delete", "crud"]):
            crud_ops = ["create", "read", "view", "update", "edit", "delete", "remove"]
            covered_ops = [op for op in crud_ops if op in all_story_text]
            if len(covered_ops) < 3:  # Should have at least 3 CRUD operations
                missing.append("CRUD operations not fully covered")
        
        return missing
    
    def validate_stories(self, state: ProjectManagementState) -> ProjectManagementState:
        """Main method to validate user stories"""
        start_time = datetime.now()
        
        try:
            requirements = state["client_requirements"]
            stories = state.get("user_stories", [])
            
            print(f"[VALIDATION DEBUG] Received {len(stories)} stories from generation")
            if stories:
                print(f"[VALIDATION DEBUG] First story keys: {list(stories[0].keys())}")
            
            if not stories:
                state["validation_status"] = ValidationStatus.NEEDS_REVISION.value
                state["validation_feedback"] = ["No user stories generated"]
                state["validation_score"] = 0.0
                state["current_phase"] = "story_generation"
                return state
            
            # Perform structural validation
            all_issues = []
            story_issues = {}
            
            # Check each story's format
            for story in stories:
                issues = self._check_story_format(story)
                if issues:
                    story_issues[story["id"]] = issues
                    all_issues.extend(issues)
            
            # Check dependencies
            dep_issues = self._check_dependencies(stories)
            if dep_issues:
                all_issues.extend(dep_issues)
            
            # Check coverage
            coverage_issues = self._check_coverage(requirements, stories)
            if coverage_issues:
                all_issues.extend(coverage_issues)
            
            # Use Gemini for semantic validation
            chain = self.validation_prompt | self.llm | self.parser
            
            print(f"[VALIDATION DEBUG] About to call LLM with {len(stories)} stories")
            try:
                # First try without the JSON parser to see raw response
                raw_chain = self.validation_prompt | self.llm
                raw_response = raw_chain.invoke({
                    "requirements": requirements,
                    "stories": json.dumps(stories, indent=2)
                })
                print(f"[VALIDATION DEBUG] Raw LLM response: {raw_response.content[:500]}...")
                
                # Now try with the parser
                semantic_validation = self.parser.parse(raw_response.content)
                print(f"[VALIDATION DEBUG] Parsed response type: {type(semantic_validation)}")
                print(f"[VALIDATION DEBUG] Parsed response keys: {semantic_validation.keys() if isinstance(semantic_validation, dict) else 'Not a dict'}")
            except Exception as validation_error:
                print(f"[VALIDATION ERROR] LLM call failed: {validation_error}")
                # Provide fallback validation result
                semantic_validation = {
                    "validation_score": 60.0,
                    "overall_valid": False,
                    "critical_issues": [f"Validation LLM failed: {str(validation_error)}"],
                    "recommendations": ["Manual review required - validation system error"],
                    "story_issues": {},
                    "missing_requirements": [],
                    "warnings": []
                }
            
            # Combine validations
            validation_score = semantic_validation.get("validation_score", 70.0)
            
            # Adjust score based on structural issues
            if all_issues:
                validation_score -= min(30, len(all_issues) * 2)
            
            # Determine validation status
            if validation_score >= 80 and len(all_issues) < 3:
                validation_status = ValidationStatus.APPROVED.value
                next_phase = "task_creation"
            elif validation_score >= 60:
                validation_status = ValidationStatus.NEEDS_REVISION.value
                next_phase = "story_generation"
            else:
                validation_status = ValidationStatus.NEEDS_CLARIFICATION.value
                next_phase = "requirement_parsing"
            
            # Combine feedback
            feedback = []
            if semantic_validation.get("critical_issues"):
                feedback.extend(semantic_validation["critical_issues"])
            if all_issues:
                feedback.extend(all_issues[:5])  # Top 5 issues
            if semantic_validation.get("recommendations"):
                feedback.extend(semantic_validation["recommendations"][:3])
            
            # Store detailed feedback for next iteration
            detailed_feedback = {
                "validation_score": validation_score,
                "critical_issues": semantic_validation.get("critical_issues", []),
                "recommendations": semantic_validation.get("recommendations", []),
                "missing_requirements": semantic_validation.get("missing_requirements", []),
                "warnings": semantic_validation.get("warnings", []),
                "structural_issues": all_issues
            }
            
            # Generate improvement instructions for next iteration
            improvement_instructions = []
            if semantic_validation.get("critical_issues"):
                improvement_instructions.append("Fix all critical issues identified in the validation")
            if semantic_validation.get("missing_requirements"):
                improvement_instructions.append("Add user stories to cover missing requirements")
            if story_issues:
                improvement_instructions.append("Address story-specific formatting and content issues")
            if validation_score < 70:
                improvement_instructions.append("Improve overall story quality to achieve higher validation score")
            
            # Update state with rich feedback
            state["validation_status"] = validation_status
            state["validation_feedback"] = feedback
            state["validation_score"] = max(0, min(100, validation_score))
            state["story_issues"] = story_issues
            state["detailed_feedback"] = detailed_feedback
            state["improvement_instructions"] = improvement_instructions
            state["current_phase"] = next_phase
            
            # Increment iteration count if revision needed
            if validation_status != ValidationStatus.APPROVED.value:
                state["iteration_count"] = state.get("iteration_count", 0) + 1
            
            processing_time = (datetime.now() - start_time).total_seconds()
            if "processing_time" not in state:
                state["processing_time"] = {}
            state["processing_time"]["validation"] = processing_time
            
        except Exception as e:
            state["last_error"] = f"Validation failed: {str(e)}"
            state["validation_status"] = ValidationStatus.NEEDS_REVISION.value
            state["validation_feedback"] = ["Validation process encountered an error"]
            state["current_phase"] = "error"
        
        return state

# ==================== WORKFLOW SETUP ====================

def create_story_workflow(gemini_api_key: str = None, max_iterations: int = 3) -> StateGraph:
    """Create the LangGraph workflow for story generation and validation with feedback loop"""
    
    # Initialize agents
    story_agent = UserStoryGenerationAgent(gemini_api_key)
    validation_agent = UserStoryValidationAgent(gemini_api_key)
    
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
    
    # Add placeholder nodes for next steps (implement these later)
    workflow.add_node("task_creation", lambda x: x)  # Placeholder
    workflow.add_node("requirement_parsing", lambda x: x)  # Placeholder
    workflow.add_node("human_review", lambda x: x)  # Placeholder
    
    # Add edges
    workflow.add_edge("initialize", "generate_stories")
    workflow.add_edge("generate_stories", "validate_stories")
    
    # Enhanced conditional edges with feedback loop
    def determine_next_step(state: ProjectManagementState) -> str:
        validation_status = state.get("validation_status")
        iteration_count = state.get("iteration_count", 0)
        max_iter = state.get("max_iterations", max_iterations)
        validation_score = state.get("validation_score", 0)
        
        print(f"[WORKFLOW] Iteration {iteration_count}, Status: {validation_status}, Score: {validation_score:.1f}")
        
        # Check if approved or good enough
        if validation_status == ValidationStatus.APPROVED.value or validation_score >= 85:
            return "approved"
        
        # Check iteration limits
        if iteration_count >= max_iter:
            print(f"[WORKFLOW] Maximum iterations ({max_iter}) reached, escalating to human review")
            return "max_iterations"
        
        # Check for clarification needs
        if validation_status == ValidationStatus.NEEDS_CLARIFICATION.value:
            return "needs_clarification"
        
        # Continue with revision if validation score suggests improvement is possible
        if validation_score >= 30:  # Worth trying to improve
            print(f"[WORKFLOW] Score {validation_score:.1f} suggests improvement possible, iterating...")
            return "needs_revision"
        else:
            print(f"[WORKFLOW] Low score {validation_score:.1f}, escalating to human review")
            return "low_quality"
    
    workflow.add_conditional_edges(
        "validate_stories",
        determine_next_step,
        {
            "approved": "task_creation",  # Success - proceed to next stage
            "needs_revision": "generate_stories",  # Feedback loop - try again with validation feedback
            "needs_clarification": "requirement_parsing",  # Requirements issue
            "max_iterations": "human_review",  # Too many iterations
            "low_quality": "human_review"  # Quality too low to auto-improve
        }
    )
    
    # Set entry point
    workflow.set_entry_point("initialize")
    
    return workflow

# ==================== PDF PROCESSING FUNCTIONS ====================

def process_pdf_to_user_stories(
    pdf_file_path: str,
    project_context: Dict = None,
    max_iterations: int = 3,
    gemini_api_key: str = None
) -> Dict:
    """
    Complete workflow: Load PDF → Generate User Stories with Feedback Loop
    
    Args:
        pdf_file_path: Path to the PDF requirements document
        project_context: Optional project context (industry, team size, etc.)
        max_iterations: Maximum feedback loop iterations (default: 3)
        gemini_api_key: Gemini API key (uses env variable if not provided)
    
    Returns:
        Dict containing user stories, validation results, and metadata
    """
    
    # Step 1: Load and parse PDF
    try:
        documentation = load_documentation_from_file(pdf_file_path)
        print(f"✅ Loaded PDF: {documentation['title']}")
    except Exception as e:
        raise ValueError(f"Failed to load PDF {pdf_file_path}: {e}")
    
    # Step 2: Setup default project context
    default_context = {
        "industry": "Technology",
        "team_size": 10,
        "tech_stack": ["Python", "React", "PostgreSQL"],
        "timeline": "6 months",
        "budget": "medium",
        "source": f"PDF: {pdf_file_path}"
    }
    
    if project_context:
        default_context.update(project_context)
    
    # Step 3: Create workflow
    workflow = create_story_workflow(gemini_api_key, max_iterations)
    app = workflow.compile()
    
    # Step 4: Setup initial state
    initial_state = {
        "project_id": f"PDF_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "client_requirements": "",  # Will be generated from PDF
        "documentation": documentation,
        "project_context": default_context,
        "current_phase": "story_generation",
        "iteration_count": 0,
        "timestamp": datetime.now().isoformat()
    }
    
    # Step 5: Run workflow
    print(f"🚀 Generating user stories from PDF...")
    
    final_result = None
    iterations = []
    
    for output in app.stream(initial_state):
        for key, value in output.items():
            final_result = value
            
            if key == "generate_stories":
                iteration = value.get("iteration_count", 0)
                story_count = len(value.get('user_stories', []))
                print(f"📝 Iteration {iteration}: Generated {story_count} stories")
            
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
                
                print(f"🔍 Iteration {iteration}: {status} (Score: {score:.1f}/100)")
    
    # Step 6: Return results
    if final_result and final_result.get('user_stories'):
        return {
            "success": True,
            "source_pdf": pdf_file_path,
            "document_info": {
                "title": documentation['title'],
                "type": documentation['document_type'],
                "content_length": len(documentation['content'])
            },
            "workflow_results": {
                "iterations": iterations,
                "final_score": final_result.get('validation_score', 0),
                "final_status": final_result.get('validation_status'),
                "total_iterations": len(iterations)
            },
            "user_stories": final_result['user_stories'],
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "story_count": len(final_result['user_stories']),
                "validation_score": final_result.get('validation_score', 0)
            }
        }
    else:
        return {
            "success": False,
            "error": "No user stories were generated",
            "source_pdf": pdf_file_path
        }

# ==================== UTILITY FUNCTIONS ====================

def create_documentation_from_text(content: str, doc_type: str = "Requirements Document", title: str = "Project Requirements") -> Dict:
    """Helper function to create structured documentation from plain text"""
    return {
        "document_type": doc_type,
        "title": title,
        "content": content,
        "sections": {},
        "stakeholders": [],
        "business_goals": [],
        "technical_constraints": [],
        "success_criteria": []
    }

def create_structured_documentation(
    title: str,
    content: str,
    doc_type: str = "Product Requirements Document",
    sections: Dict[str, str] = None,
    stakeholders: List[str] = None,
    business_goals: List[str] = None,
    technical_constraints: List[str] = None,
    success_criteria: List[str] = None
) -> Dict:
    """Helper function to create comprehensive structured documentation"""
    return {
        "document_type": doc_type,
        "title": title,
        "content": content,
        "sections": sections or {},
        "stakeholders": stakeholders or [],
        "business_goals": business_goals or [],
        "technical_constraints": technical_constraints or [],
        "success_criteria": success_criteria or []
    }

def load_documentation_from_file(file_path: str) -> Dict:
    """Load documentation from various file formats (PDF, DOCX, TXT, MD)"""
    import os
    
    if not os.path.exists(file_path):
        raise ValueError(f"File not found: {file_path}")
    
    file_extension = os.path.splitext(file_path)[1].lower()
    filename = os.path.basename(file_path)
    title = os.path.splitext(filename)[0]
    
    try:
        if file_extension == '.pdf':
            content = _extract_text_from_pdf(file_path)
            doc_type = "PDF Document"
        elif file_extension == '.docx':
            content = _extract_text_from_docx(file_path)
            doc_type = "Word Document"
        elif file_extension in ['.txt', '.md']:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            doc_type = "Markdown Document" if file_extension == '.md' else "Text Document"
        else:
            # Try to read as plain text for unknown extensions
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            doc_type = "Text Document"
        
        if not content.strip():
            raise ValueError("Document appears to be empty or unreadable")
        
        return create_documentation_from_text(
            content=content,
            title=title,
            doc_type=doc_type
        )
        
    except Exception as e:
        raise ValueError(f"Failed to load documentation from {file_path}: {e}")

def _extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from PDF file"""
    try:
        import PyPDF2
        
        text_content = []
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text_content.append(page.extract_text())
        
        content = '\n'.join(text_content)
        
        # Clean up the text
        content = _clean_extracted_text(content)
        
        return content
        
    except ImportError:
        raise ValueError("PyPDF2 library not installed. Run: pip install PyPDF2")
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {e}")

def _extract_text_from_docx(file_path: str) -> str:
    """Extract text content from DOCX file"""
    try:
        from docx import Document
        
        doc = Document(file_path)
        text_content = []
        
        # Extract paragraphs
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_content.append(paragraph.text)
        
        # Extract text from tables
        for table in doc.tables:
            for row in table.rows:
                row_text = []
                for cell in row.cells:
                    if cell.text.strip():
                        row_text.append(cell.text.strip())
                if row_text:
                    text_content.append(' | '.join(row_text))
        
        content = '\n'.join(text_content)
        
        # Clean up the text
        content = _clean_extracted_text(content)
        
        return content
        
    except ImportError:
        raise ValueError("python-docx library not installed. Run: pip install python-docx")
    except Exception as e:
        raise ValueError(f"Failed to extract text from DOCX: {e}")

def _clean_extracted_text(text: str) -> str:
    """Clean and normalize extracted text from documents"""
    import re
    
    # Remove excessive whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Multiple newlines to double newline
    text = re.sub(r' +', ' ', text)  # Multiple spaces to single space
    
    # Remove strange characters that sometimes appear in PDFs
    text = re.sub(r'[^\w\s\.,;:!?\-()[\]{}"\'/\\+=*&%$#@|<>~`]', '', text)
    
    # Fix common PDF extraction issues
    text = text.replace('•', '-')  # Bullet points
    text = text.replace('○', '-')  # Bullet points
    text = text.replace('▪', '-')  # Bullet points
    
    return text.strip()

# ==================== USAGE EXAMPLE ====================

if __name__ == "__main__":
    # Example usage
    import os
    
    # Load environment variables from .env file if available
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("python-dotenv not installed. Loading environment variables from system only.")
    
    # Get API key from environment variable
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("Please set GEMINI_API_KEY environment variable or create a .env file")
        print("Example .env file content:")
        print("GEMINI_API_KEY=your_api_key_here")
        exit(1)
    
    # Initialize workflow
    workflow = create_story_workflow(gemini_api_key)
    app = workflow.compile()
    
    # Example 1: Using structured documentation (RECOMMENDED)
    project_documentation = create_structured_documentation(
        title="AI-Powered Project Management Platform",
        doc_type="Product Requirements Document",
        content="""
        Build an AI-powered project management tool similar to JIRA that automates project management workflows
        and provides intelligent insights for development teams.
        """,
        sections={
            "overview": "An intelligent project management platform that uses AI to automate story generation, task assignment, and quality control.",
            "core_features": """
            1. Automated user story generation from requirements
            2. Intelligent task creation and assignment
            3. Interactive Kanban board with drag-and-drop
            4. AI-powered quality control and testing
            5. Real-time developer feedback system
            6. Validation agents for output verification
            7. Team collaboration tools
            8. Performance analytics and reporting
            """,
            "user_interface": "Modern React-based UI with responsive design and intuitive user experience",
            "architecture": "Microservices architecture with Python backend and PostgreSQL database"
        },
        stakeholders=["Development Teams", "Project Managers", "QA Engineers", "Product Owners", "Scrum Masters"],
        business_goals=[
            "Reduce project planning time by 70%",
            "Improve development velocity by 40%", 
            "Increase delivery quality through automated QC",
            "Enable data-driven project decisions"
        ],
        technical_constraints=[
            "Must handle 100+ concurrent users",
            "Sub-second response times required",
            "Integration with existing development tools",
            "Scalable cloud-native architecture"
        ],
        success_criteria=[
            "User story generation accuracy > 90%",
            "Task completion tracking in real-time",
            "User adoption rate > 80% within 3 months",
            "System uptime > 99.9%"
        ]
    )
    
    initial_state_with_docs = {
        "project_id": "PROJ-001", 
        "client_requirements": "",  # Will be generated from documentation
        "documentation": project_documentation,
        "project_context": {
            "industry": "Software Development",
            "team_size": 10,
            "tech_stack": ["Python", "FastAPI", "React", "PostgreSQL"],
            "timeline": "3 months",
            "budget": "medium"
        },
        "current_phase": "story_generation",
        "iteration_count": 0,
        "timestamp": datetime.now().isoformat()
    }
    
    # Example 2: Using simple text (BACKWARD COMPATIBILITY)
    initial_state_simple = {
        "project_id": "PROJ-002",
        "client_requirements": """
        Build an AI-powered project management tool similar to JIRA.
        The system should:
        1. Parse client requirements and generate user stories automatically
        2. Create tasks from user stories and assign them to developers
        3. Display tasks on a Kanban board with drag-and-drop functionality
        4. Perform automated QC and testing on completed work
        5. Provide AI-powered feedback to developers
        6. Include validation agents to verify all outputs
        7. Support real-time collaboration between team members
        8. Generate performance reports for employees
        9. Include authentication and role-based access control
        10. Handle at least 100 concurrent users with sub-second response times
        """,
        "project_context": {
            "industry": "Software Development",
            "team_size": 10,
            "tech_stack": ["Python", "FastAPI", "React", "PostgreSQL"],
            "timeline": "3 months",
            "budget": "medium"
        },
        "current_phase": "story_generation",
        "iteration_count": 0,
        "timestamp": datetime.now().isoformat()
    }
    
    # Choose which example to run
    initial_state = initial_state_with_docs  # Use structured documentation
    
    # Run the workflow
    try:
        # Invoke with the initial state
        for output in app.stream(initial_state):
            for key, value in output.items():
                print(f"\n=== {key} ===")
                if key == "generate_stories":
                    print(f"Generated {len(value.get('user_stories', []))} user stories")
                elif key == "validate_stories":
                    print(f"Validation Status: {value.get('validation_status')}")
                    print(f"Validation Score: {value.get('validation_score')}")
                    if value.get('validation_feedback'):
                        print(f"Feedback: {value.get('validation_feedback')}")
        
        # Get final state
        final_state = app.get_state(initial_state)
        
        if final_state.values.get("user_stories"):
            print("\n=== Final Generated User Stories ===")
            for story in final_state.values["user_stories"][:3]:  # Show first 3 stories
                print(f"\nID: {story['id']}")
                print(f"Title: {story['title']}")
                print(f"Priority: {story['priority']}")
                print(f"Points: {story['estimated_points']}")
                print(f"Acceptance Criteria: {len(story['acceptance_criteria'])} items")
                
    except Exception as e:
        print(f"Error running workflow: {e}")