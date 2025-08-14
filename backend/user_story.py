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

class ProjectManagementState(TypedDict):
    """Shared state for all agents in the workflow"""
    # Input
    client_requirements: str
    project_id: str
    project_context: Optional[Dict]  # Industry, team size, tech stack, etc.
    
    # Generated artifacts
    parsed_requirements: Optional[Dict]
    user_stories: Optional[List[Dict]]
    
    # Validation
    validation_status: Optional[str]
    validation_feedback: Optional[List[str]]
    validation_score: Optional[float]
    story_issues: Optional[Dict[str, List[str]]]  # Issues per story ID
    
    # Metadata
    current_phase: str
    iteration_count: int
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
            ("system", """You are an expert Product Manager and Business Analyst specializing in creating comprehensive user stories from client requirements.

Your task is to analyze the client requirements and generate detailed user stories following these guidelines:

1. **Story Format**: Use the standard format "As a [type of user], I want [goal/desire] so that [benefit/value]"
2. **Completeness**: Ensure each story is independent and deliverable
3. **INVEST Criteria**: Each story should be Independent, Negotiable, Valuable, Estimable, Small, Testable
4. **Technical Depth**: Include technical notes for developers
5. **Clear Acceptance Criteria**: Each criterion should be testable and specific

Context about the project:
{project_context}

Generate user stories that:
- Cover all aspects of the requirements
- Are properly prioritized based on business value and dependencies
- Include realistic story point estimates
- Have clear dependencies marked
- Include both functional and non-functional requirements (security, performance, etc.)

Output the stories as a JSON array with the exact structure provided."""),
            ("human", """Client Requirements:
{requirements}

Generate comprehensive user stories from these requirements. 

Return a JSON array where each story has:
- id: Unique identifier (US001, US002, etc.)
- title: User story in standard format
- description: Detailed description
- acceptance_criteria: Array of specific, testable criteria
- priority: "high", "medium", or "low"
- estimated_points: Story points (1, 2, 3, 5, 8, or 13)
- dependencies: Array of story IDs this depends on
- technical_notes: Implementation guidance for developers

Focus on creating stories that are:
1. Complete and independent
2. Properly sized (not too large)
3. Testable with clear acceptance criteria
4. Valuable to the end user""")
        ])
        
        self.parser = JsonOutputParser()
        
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
            requirements = state["client_requirements"]
            project_context = state.get("project_context", {})
            
            # Format context for the prompt
            context_str = json.dumps(project_context) if project_context else "No specific context provided"
            
            # Generate stories using Gemini
            chain = self.story_prompt | self.llm | self.parser
            
            raw_stories = chain.invoke({
                "requirements": requirements,
                "project_context": context_str
            })
            
            # Ensure we have a list
            if not isinstance(raw_stories, list):
                raw_stories = [raw_stories]
            
            # Validate and clean each story
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
                
                validated_stories.append(validated_story)
            
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
            ("system", """You are an expert QA specialist and Business Analyst responsible for validating user stories.

Evaluate each user story against these criteria:

1. **FORMAT COMPLIANCE**:
   - Follows "As a [user], I want [feature] so that [benefit]" format
   - Has unique ID
   - All required fields present

2. **INVEST PRINCIPLES**:
   - Independent: Can be developed separately
   - Negotiable: Not overly detailed implementation
   - Valuable: Provides clear value to users
   - Estimable: Clear enough to estimate effort
   - Small: Can be completed in one sprint
   - Testable: Has clear acceptance criteria

3. **COMPLETENESS**:
   - Acceptance criteria are specific and measurable
   - Dependencies are logical
   - Priority aligns with business value
   - Technical notes provide useful guidance

4. **REQUIREMENTS COVERAGE**:
   - All client requirements are addressed
   - No major features are missing
   - Non-functional requirements included

5. **CONSISTENCY**:
   - No contradictions between stories
   - Dependencies make sense
   - Priorities are logical

Provide detailed feedback for each issue found."""),
            ("human", """Original Requirements:
{requirements}

Generated User Stories:
{stories}

Validate these stories and return a JSON object with:
- overall_valid: boolean
- validation_score: float (0-100)
- missing_requirements: array of requirements not covered
- story_issues: object with story_id as key and array of issues as value
- recommendations: array of specific improvements needed
- critical_issues: array of issues that must be fixed
- warnings: array of non-critical suggestions""")
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
            
            # Update state
            state["validation_status"] = validation_status
            state["validation_feedback"] = feedback
            state["validation_score"] = max(0, min(100, validation_score))
            state["story_issues"] = story_issues
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

def create_story_workflow(gemini_api_key: str = None) -> StateGraph:
    """Create the LangGraph workflow for story generation and validation"""
    
    # Initialize agents
    story_agent = UserStoryGenerationAgent(gemini_api_key)
    validation_agent = UserStoryValidationAgent(gemini_api_key)
    
    # Create workflow
    workflow = StateGraph(ProjectManagementState)
    
    # Add nodes
    workflow.add_node("generate_stories", story_agent.generate_stories)
    workflow.add_node("validate_stories", validation_agent.validate_stories)
    
    # Add placeholder nodes for next steps (implement these later)
    workflow.add_node("task_creation", lambda x: x)  # Placeholder
    workflow.add_node("requirement_parsing", lambda x: x)  # Placeholder
    workflow.add_node("human_review", lambda x: x)  # Placeholder
    
    # Add edges
    workflow.add_edge("generate_stories", "validate_stories")
    
    # Add conditional edges based on validation
    def determine_next_step(state: ProjectManagementState) -> str:
        if state.get("validation_status") == ValidationStatus.APPROVED.value:
            return "approved"
        elif state.get("iteration_count", 0) >= 3:
            return "max_iterations"
        elif state.get("validation_status") == ValidationStatus.NEEDS_CLARIFICATION.value:
            return "needs_clarification"
        else:
            return "needs_revision"
    
    workflow.add_conditional_edges(
        "validate_stories",
        determine_next_step,
        {
            "approved": "task_creation",  # Next agent in pipeline
            "needs_revision": "generate_stories",
            "needs_clarification": "requirement_parsing",  # Go back to requirement parsing
            "max_iterations": "human_review"  # Escalate to human
        }
    )
    
    # Set entry point
    workflow.set_entry_point("generate_stories")
    
    return workflow

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
    
    # Example initial state
    initial_state = {
        "project_id": "PROJ-001",
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