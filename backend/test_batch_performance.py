#!/usr/bin/env python3
"""
Performance test for optimized batch TaskGenerationAgent
"""

import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from user_story import (
    create_story_workflow,
    create_structured_documentation,
    ProjectManagementState
)

def create_test_documentation(num_features: int):
    """Create test documentation with specified number of features"""
    
    features = []
    for i in range(1, num_features + 1):
        features.append(f"{i}. Feature {i}: User can perform action {i} with data validation")
    
    return create_structured_documentation(
        title=f"Test System with {num_features} Features",
        doc_type="Product Requirements Document",
        content=f"""
        Build a comprehensive system with {num_features} different features.
        Each feature should have proper CRUD operations, validation, and testing.
        """,
        sections={
            "core_features": "\n".join(features),
            "technical_requirements": "Web-based application with REST API backend and React frontend",
            "performance_requirements": "System must handle concurrent users efficiently"
        },
        stakeholders=["End Users", "Administrators", "Developers"],
        business_goals=["Feature completeness", "Performance", "User satisfaction"],
        technical_constraints=["Scalable architecture", "Fast response times"],
        success_criteria=["All features work correctly", "Performance targets met"]
    )

def run_performance_test(test_name: str, num_features: int, gemini_api_key: str):
    """Run a performance test with specified number of features"""
    
    print(f"\n{'='*60}")
    print(f"🚀 {test_name}")
    print(f"📊 Expected stories: ~{num_features + 3} (features + NFRs)")
    print(f"{'='*60}")
    
    # Create test documentation
    test_documentation = create_test_documentation(num_features)
    
    # Setup initial state
    initial_state = {
        "project_id": f"PERF-{num_features:02d}",
        "client_requirements": "",
        "documentation": test_documentation,
        "project_context": {
            "industry": "Software Testing",
            "team_size": 5,
            "tech_stack": ["Python", "FastAPI", "React", "PostgreSQL"],
            "timeline": "6 weeks",
            "budget": "medium"
        },
        "current_phase": "story_generation",
        "iteration_count": 0,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        # Create and run workflow
        workflow = create_story_workflow(gemini_api_key, max_iterations=2)
        app = workflow.compile()
        
        overall_start = time.time()
        
        final_result = None
        task_gen_time = 0
        
        for output in app.stream(initial_state):
            for key, value in output.items():
                final_result = value
                
                if key == "generate_stories":
                    stories = value.get('user_stories', [])
                    print(f"📝 Generated {len(stories)} user stories")
                    
                elif key == "validate_stories":
                    status = value.get('validation_status', 'unknown')
                    score = value.get('validation_score', 0)
                    print(f"✅ Validation: {status} (Score: {score:.1f}/100)")
                    
                elif key == "generate_tasks":
                    tasks = value.get('tasks', [])
                    task_gen_time = value.get('processing_time', {}).get('task_generation', 0)
                    print(f"⚡ Generated {len(tasks)} tasks in {task_gen_time:.1f}s")
        
        overall_time = time.time() - overall_start
        
        if final_result and final_result.get('tasks'):
            user_stories = final_result.get('user_stories', [])
            tasks = final_result.get('tasks', [])
            
            # Calculate performance metrics
            stories_per_sec = len(user_stories) / task_gen_time if task_gen_time > 0 else 0
            tasks_per_sec = len(tasks) / task_gen_time if task_gen_time > 0 else 0
            
            print(f"\n📈 Performance Results:")
            print(f"   Stories: {len(user_stories)}")
            print(f"   Tasks: {len(tasks)}")
            print(f"   Task Generation Time: {task_gen_time:.1f}s")
            print(f"   Overall Time: {overall_time:.1f}s")
            print(f"   Performance: {stories_per_sec:.1f} stories/sec, {tasks_per_sec:.1f} tasks/sec")
            
            # Analyze task distribution
            categories = {}
            story_task_count = {}
            
            for task in tasks:
                cat = task.get('category', 'unknown')
                categories[cat] = categories.get(cat, 0) + 1
                
                story_id = task.get('story_id', 'unknown')
                story_task_count[story_id] = story_task_count.get(story_id, 0) + 1
            
            print(f"\n📊 Task Categories: {', '.join([f'{k}: {v}' for k, v in categories.items()])}")
            
            # Check if all stories have tasks
            stories_without_tasks = len(user_stories) - len(story_task_count)
            if stories_without_tasks > 0:
                print(f"⚠️  {stories_without_tasks} stories missing tasks")
            else:
                print(f"✅ All {len(user_stories)} stories have tasks")
            
            return {
                'success': True,
                'stories': len(user_stories),
                'tasks': len(tasks),
                'task_gen_time': task_gen_time,
                'overall_time': overall_time,
                'stories_per_sec': stories_per_sec,
                'tasks_per_sec': tasks_per_sec
            }
        else:
            print(f"❌ No tasks generated")
            return {'success': False}
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return {'success': False, 'error': str(e)}

def main():
    """Run comprehensive performance tests"""
    
    # Load environment variables
    load_dotenv()
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        return False
    
    print("🧪 TaskGenerationAgent Batch Processing Performance Tests")
    print("=" * 80)
    
    # Test scenarios
    test_scenarios = [
        ("Small Set (3 features)", 3),
        ("Medium Set (8 features)", 8),
        ("Large Set (15 features)", 15),
    ]
    
    results = []
    
    for test_name, num_features in test_scenarios:
        result = run_performance_test(test_name, num_features, gemini_api_key)
        results.append((test_name, result))
        
        # Brief pause between tests
        time.sleep(2)
    
    # Summary
    print(f"\n{'='*80}")
    print("📊 PERFORMANCE SUMMARY")
    print(f"{'='*80}")
    
    for test_name, result in results:
        if result.get('success'):
            print(f"{test_name}:")
            print(f"  Stories: {result['stories']}, Tasks: {result['tasks']}")
            print(f"  Task Gen Time: {result['task_gen_time']:.1f}s")
            print(f"  Performance: {result['stories_per_sec']:.1f} stories/sec")
        else:
            print(f"{test_name}: FAILED - {result.get('error', 'Unknown error')}")
    
    # Check if performance targets are met
    successful_tests = [r for _, r in results if r.get('success')]
    if successful_tests:
        avg_time_per_story = sum(r['task_gen_time'] / r['stories'] for r in successful_tests) / len(successful_tests)
        print(f"\n🎯 Average time per story: {avg_time_per_story:.2f}s")
        
        if avg_time_per_story < 2.0:
            print("✅ Performance target met: <2s per story")
        else:
            print("⚠️  Performance target missed: >2s per story")
    
    return len(successful_tests) == len(test_scenarios)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
