# ==================== TASK GENERATION AGENT ====================

from typing import TypedDict, List, Dict, Optional, Any
from datetime import datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import os
# Import dependencies with fallback for direct execution
try:
    # Try relative imports (when imported as module)
    from ..state import ProjectManagementState
except ImportError:
    # Fallback to absolute imports (when run directly)
    from state import ProjectManagementState

class TaskGenerationAgent:
    """Agent responsible for generating tasks from validated user stories"""
    
    def __init__(self, gemini_api_key: str = None, temperature: float = 0.3):
        api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY must be provided either as parameter or environment variable")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            temperature=0.4,
            google_api_key=api_key
        )
        
        # Optimized batch processing prompt for multiple stories
        self.batch_task_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are a Technical Lead decomposing user stories into development tasks.

For each story, generate 3-5 tasks:
- Backend task (API/database)
- Frontend task (UI/components) 
- Testing task (unit/integration tests)
- Optional: DevOps or documentation task

Each task must include:
- story_id, title, description, category, estimated_hours, dependencies
- 2-4 specific acceptance criteria defining when the task is complete

Return JSON array: [{{
  "story_id": "US001",
  "title": "Task name",
  "description": "Create REST API endpoints for user registration, login, and logout.",
  "category": "backend|frontend|testing|devops",
  "estimated_hours": 8,
  "dependencies": [],
  "acceptance_criteria": [
    "API endpoint returns correct JSON response",
    "Endpoint handles error cases appropriately",
    "Unit tests pass with 90% coverage"
  ]
}}]"""
            ),
            (
                "human",
                """Stories:
{stories_formatted}

Tech: {tech_stack}

Generate 3-5 tasks per story. Include a unique title, concise description, and 2-4 specific acceptance criteria for each task. Return JSON array only."""
            ),
        ])
        
        self.parser = JsonOutputParser()
    
    def _generate_batch_tasks(self, story_batch: List[Dict], project_context: Dict, starting_task_id: int) -> List[Dict]:
        """Process multiple stories in a single LLM call for improved performance"""
        
        batch_start_time = datetime.now()
        tech_stack = project_context.get("tech_stack", ["Python", "React", "PostgreSQL"])
        tech_stack_str = ", ".join(tech_stack)
        
        # Format stories concisely for the prompt
        stories_formatted = []
        for story in story_batch:
            story_text = f"{story['id']}: {story['title']} | {story.get('priority', 'medium')} priority"
            stories_formatted.append(story_text)
        
        stories_formatted_str = "\n".join(stories_formatted)
        
        try:
            chain = self.batch_task_prompt | self.llm | self.parser
            
            print(f"[TASK_GEN] Batch processing {len(story_batch)} stories...")
            
            tasks = chain.invoke({
                "stories_formatted": stories_formatted_str,
                "tech_stack": tech_stack_str
            })
            
            # Ensure we have a list
            if not isinstance(tasks, list):
                tasks = [tasks] if tasks else []
            
            validated_tasks = []
            task_id_counter = starting_task_id
            
            for task in tasks:
                if isinstance(task, dict):
                    # Ensure required fields and validate story_id
                    story_id = task.get("story_id", "")
                    if not story_id or not any(s["id"] == story_id for s in story_batch):
                        # Try to infer story_id from task content or assign to first story
                        story_id = story_batch[0]["id"]
                    
                    validated_task = {
                        "id": f"T{task_id_counter:03d}",
                        "story_id": story_id,
                        "title": task.get("title", f"Task for {story_id}"),
                        "description": task.get("description", task.get("title", "")),
                        "category": task.get("category", "backend"),
                        "estimated_hours": min(16, max(4, task.get("estimated_hours", 8))),
                        "priority": task.get("priority", "medium"),
                        "dependencies": task.get("dependencies", []),
                        "acceptance_criteria": task.get("acceptance_criteria", ["Task completed successfully"]),
                        "technical_notes": task.get("technical_notes", "")
                    }
                    validated_tasks.append(validated_task)
                    task_id_counter += 1
            
            elapsed = (datetime.now() - batch_start_time).total_seconds()
            print(f"[TASK_GEN] Batch completed: {len(story_batch)} stories -> {len(validated_tasks)} tasks in {elapsed:.1f}s")
            
            return validated_tasks
            
        except Exception as e:
            print(f"[TASK_GEN_ERROR] Batch processing failed: {e}")
            # Fallback to individual story processing
            return self._create_fallback_tasks_for_batch(story_batch, project_context, starting_task_id)
    
    def _create_fallback_tasks_for_batch(self, story_batch: List[Dict], project_context: Dict, starting_task_id: int) -> List[Dict]:
        """Create fallback tasks for a batch of stories when LLM fails"""
        print(f"[TASK_GEN] Creating fallback tasks for {len(story_batch)} stories")
        
        all_tasks = []
        task_counter = starting_task_id - 1
        
        for story in story_batch:
            fallback_tasks = self._create_fallback_tasks(story, task_counter)
            task_counter += len(fallback_tasks)
            all_tasks.extend(fallback_tasks)
        
        return all_tasks
    
    def _create_fallback_tasks(self, story: Dict, task_counter: int) -> List[Dict]:
        """Create basic fallback tasks when LLM decomposition fails"""
        story_id = story["id"]
        base_title = story["title"].replace("As a ", "").replace(", I want ", " - ").replace(" so that ", " - ")
        
        fallback_tasks = [
            {
                "id": f"T{task_counter + 1:03d}",
                "story_id": story_id,
                "title": f"Backend implementation for {base_title}",
                "description": f"Implement backend logic and API endpoints for {story['description']}",
                "category": "backend",
                "estimated_hours": 12,
                "priority": story.get("priority", "medium"),
                "dependencies": [],
                "acceptance_criteria": [
                    "Backend logic implements the required functionality",
                    "API endpoints return correct responses",
                    "Error handling is implemented",
                    "Code follows project standards"
                ],
                "technical_notes": story.get("technical_notes", "")
            },
            {
                "id": f"T{task_counter + 2:03d}",
                "story_id": story_id,
                "title": f"Frontend implementation for {base_title}",
                "description": f"Create UI components and user interface for {story['description']}",
                "category": "frontend",
                "estimated_hours": 10,
                "priority": story.get("priority", "medium"),
                "dependencies": [f"T{task_counter + 1:03d}"],
                "acceptance_criteria": [
                    "UI components render correctly",
                    "User interactions work as expected",
                    "Design matches requirements",
                    "Responsive design implemented"
                ],
                "technical_notes": "Ensure responsive design and accessibility"
            },
            {
                "id": f"T{task_counter + 3:03d}",
                "story_id": story_id,
                "title": f"Testing for {base_title}",
                "description": f"Write and execute tests for {story['description']}",
                "category": "testing",
                "estimated_hours": 6,
                "priority": "medium",
                "dependencies": [f"T{task_counter + 1:03d}", f"T{task_counter + 2:03d}"],
                "acceptance_criteria": [
                    "Unit tests pass with >80% coverage",
                    "Integration tests pass",
                    "Edge cases are covered",
                    "Tests are automated and runnable"
                ],
                "technical_notes": "Include both unit and integration tests"
            }
        ]
        
        return fallback_tasks
    
    def generate_tasks(self, state: ProjectManagementState) -> ProjectManagementState:
        """Main method to generate tasks from validated user stories using intelligent batching"""
        start_time = datetime.now()
        
        try:
            user_stories = state.get("user_stories", [])
            project_context = state.get("project_context", {})
            
            if not user_stories:
                state["last_error"] = "No user stories available for task generation"
                state["current_phase"] = "error"
                return state
            
            num_stories = len(user_stories)
            print(f"[TASK_GEN] Generating tasks for {num_stories} user stories using batch processing")
            
            # Intelligent batching logic
            if num_stories <= 7:
                # Single batch for small sets
                batch_size = num_stories
                num_batches = 1
                print(f"[TASK_GEN] Using single batch processing for {num_stories} stories")
            else:
                # Multiple batches of 7 stories each for better efficiency
                batch_size = 7
                num_batches = (num_stories + batch_size - 1) // batch_size
                print(f"[TASK_GEN] Processing {num_stories} stories in {num_batches} batches of {batch_size}")
            
            all_tasks = []
            task_id_counter = 1
            
            # Process stories in batches
            for i in range(num_batches):
                batch_start_idx = i * batch_size
                batch_end_idx = min((i + 1) * batch_size, num_stories)
                story_batch = user_stories[batch_start_idx:batch_end_idx]
                
                print(f"[TASK_GEN] Processing batch {i+1}/{num_batches}: stories {batch_start_idx+1}-{batch_end_idx}")
                
                # Generate tasks for this batch
                batch_tasks = self._generate_batch_tasks(story_batch, project_context, task_id_counter)
                
                # Update task counter for next batch
                task_id_counter += len(batch_tasks)
                all_tasks.extend(batch_tasks)
            
            # Ensure all stories have tasks (fallback for missing ones)
            stories_with_tasks = {task["story_id"] for task in all_tasks}
            stories_without_tasks = [story for story in user_stories if story["id"] not in stories_with_tasks]
            
            if stories_without_tasks:
                print(f"[TASK_GEN] Generating fallback tasks for {len(stories_without_tasks)} stories without tasks")
                for story in stories_without_tasks:
                    fallback_tasks = self._create_fallback_tasks(story, task_id_counter - 1)
                    task_id_counter += len(fallback_tasks)
                    all_tasks.extend(fallback_tasks)
            
            # Ensure sequential task IDs
            for i, task in enumerate(all_tasks):
                task["id"] = f"T{i + 1:03d}"
            
            # Update state
            state["tasks"] = all_tasks
            state["current_phase"] = "task_assignment"
            
            processing_time = (datetime.now() - start_time).total_seconds()
            if "processing_time" not in state:
                state["processing_time"] = {}
            state["processing_time"]["task_generation"] = processing_time
            
            # Performance summary
            avg_time_per_story = processing_time / num_stories if num_stories > 0 else 0
            print(f"[TASK_GEN] Generated {len(all_tasks)} tasks for {num_stories} stories in {processing_time:.1f}s")
            print(f"[TASK_GEN] Performance: {avg_time_per_story:.1f}s per story, {num_batches} batches")
            
        except Exception as e:
            state["last_error"] = f"Task generation failed: {str(e)}"
            state["tasks"] = []
            state["current_phase"] = "error"
            print(f"[TASK_GEN_ERROR] {str(e)}")
            import traceback
            traceback.print_exc()
            
        return state