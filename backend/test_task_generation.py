#!/usr/bin/env python3
"""
Test script for TaskGenerationAgent integration
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from user_story import (
    create_story_workflow,
    create_structured_documentation,
    ProjectManagementState
)

def test_task_generation():
    """Test the complete workflow including task generation"""
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        return False
    
    print("🚀 Testing Task Generation Workflow")
    print("=" * 50)
    
    # Create test documentation
    test_documentation = create_structured_documentation(
        title="Simple Task Management System",
        doc_type="Product Requirements Document",
        content="""
        Build a simple task management system where users can create, view, and manage their tasks.
        The system should have user authentication and a clean interface.
        """,
        sections={
            "core_features": """
            1. User registration and login
            2. Create new tasks with title and description
            3. View list of all tasks
            4. Mark tasks as completed
            5. Delete tasks
            """,
            "technical_requirements": "Web-based application with REST API backend and React frontend"
        },
        stakeholders=["End Users", "Administrators"],
        business_goals=["Improve productivity", "Simple task tracking"],
        technical_constraints=["Must be responsive", "Fast load times"],
        success_criteria=["User can complete task CRUD operations", "System is intuitive to use"]
    )
    
    # Setup initial state
    initial_state = {
        "project_id": "TEST-001",
        "client_requirements": "",  # Will be generated from documentation
        "documentation": test_documentation,
        "project_context": {
            "industry": "Productivity Software",
            "team_size": 3,
            "tech_stack": ["Python", "FastAPI", "React", "PostgreSQL"],
            "timeline": "4 weeks",
            "budget": "small"
        },
        "current_phase": "story_generation",
        "iteration_count": 0,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        # Create and run workflow
        workflow = create_story_workflow(gemini_api_key, max_iterations=2)
        app = workflow.compile()
        
        print("📝 Running workflow...")
        
        final_result = None
        step_count = 0
        
        for output in app.stream(initial_state):
            step_count += 1
            for key, value in output.items():
                final_result = value
                
                if key == "generate_stories":
                    stories = value.get('user_stories', [])
                    print(f"✅ Step {step_count}: Generated {len(stories)} user stories")
                    
                elif key == "validate_stories":
                    status = value.get('validation_status', 'unknown')
                    score = value.get('validation_score', 0)
                    print(f"✅ Step {step_count}: Validation - {status} (Score: {score:.1f}/100)")
                    
                elif key == "generate_tasks":
                    tasks = value.get('tasks', [])
                    print(f"✅ Step {step_count}: Generated {len(tasks)} tasks")
                    
                    # Show sample tasks
                    if tasks:
                        print("\n📋 Sample Generated Tasks:")
                        for i, task in enumerate(tasks[:3]):  # Show first 3 tasks
                            print(f"   {i+1}. {task.get('id', 'N/A')}: {task.get('title', 'No title')}")
                            print(f"      Category: {task.get('category', 'N/A')} | Hours: {task.get('estimated_hours', 'N/A')}")
                            print(f"      Story: {task.get('story_id', 'N/A')}")
                        
                        if len(tasks) > 3:
                            print(f"   ... and {len(tasks) - 3} more tasks")
                    
                elif key == "task_assignment":
                    print(f"✅ Step {step_count}: Reached task assignment phase")
        
        # Verify results
        if final_result:
            user_stories = final_result.get('user_stories', [])
            tasks = final_result.get('tasks', [])
            
            print(f"\n🎯 Final Results:")
            print(f"   User Stories: {len(user_stories)}")
            print(f"   Generated Tasks: {len(tasks)}")
            print(f"   Final Phase: {final_result.get('current_phase', 'unknown')}")
            
            if tasks:
                # Analyze task distribution
                categories = {}
                for task in tasks:
                    cat = task.get('category', 'unknown')
                    categories[cat] = categories.get(cat, 0) + 1
                
                print(f"\n📊 Task Distribution by Category:")
                for category, count in categories.items():
                    print(f"   {category}: {count} tasks")
                
                # Check task-story mapping
                story_task_map = {}
                for task in tasks:
                    story_id = task.get('story_id', 'unknown')
                    if story_id not in story_task_map:
                        story_task_map[story_id] = 0
                    story_task_map[story_id] += 1
                
                print(f"\n🔗 Tasks per User Story:")
                for story_id, task_count in story_task_map.items():
                    print(f"   {story_id}: {task_count} tasks")
                
                return True
            else:
                print("❌ No tasks were generated")
                return False
        else:
            print("❌ Workflow did not complete successfully")
            return False
            
    except Exception as e:
        print(f"❌ Error during workflow execution: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_task_generation()
    if success:
        print("\n✅ Task Generation Test PASSED")
    else:
        print("\n❌ Task Generation Test FAILED")
    
    sys.exit(0 if success else 1)
