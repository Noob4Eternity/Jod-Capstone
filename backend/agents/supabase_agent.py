# ==================== SUPABASE STORAGE AGENT ====================

import os
import json
from datetime import datetime
from typing import Optional, Dict, Any
# Import dependencies with fallback for direct execution
try:
    # Try relative imports (when imported as module)
    from ..state import ProjectManagementState
except ImportError:
    # Fallback to absolute imports (when run directly)
    from state import ProjectManagementState

class SupabaseWorkflowAgent:
    """Agent responsible for saving project data to Supabase within the workflow."""

    def __init__(self):
        try:
            from supabase import create_client
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")
            if not url or not key:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables.")

            self.client = create_client(url, key)
            self.available = True
            print("✅ Supabase workflow agent initialized.")
        except ImportError:
            print("⚠️ Supabase library not available. Storage functionality disabled.")
            self.available = False
        except Exception as e:
            print(f"⚠️ Supabase initialization failed: {e}")
            self.available = False

    def save_project_to_supabase(self, state: ProjectManagementState) -> ProjectManagementState:
        """
        Save the complete project data to Supabase after successful task generation.
        """
        if not self.available:
            print("[SUPABASE] Supabase not available, skipping storage.")
            state["storage_success"] = False
            state["storage_error"] = "Supabase not available"
            return state

        try:
            start_time = datetime.now()

            # Prepare project data for Supabase (only include fields that exist)
            # Use project title if available, otherwise generate from project_id
            project_title = None
            if state.get("project_context"):
                project_title = state["project_context"].get("title") or state["project_context"].get("name")
            
            project_name = project_title or f"Project_{state.get('project_id', 'Unnamed')}"
            project_data = {
                "name": project_name,
                "validation_score": state.get("validation_score"),
                "iterations": state.get("iteration_count", 0),
                "status": state.get("validation_status")
            }

            # Add GitHub repository information if provided
            if state.get("project_context"):
                if state["project_context"].get("github_repo_full_name"):
                    project_data["github_repo_full_name"] = state["project_context"]["github_repo_full_name"]
                if state["project_context"].get("github_repo_url"):
                    project_data["github_repo_url"] = state["project_context"]["github_repo_url"]

            # Only add optional fields if they exist in schema
            if state.get("project_context"):
                try:
                    project_data["project_context"] = json.dumps(state["project_context"])
                except:
                    pass

            # Insert project
            project_response = self.client.from_("projects").insert(project_data).execute()
            project_db_id = project_response.data[0]['id']
            print(f"📄 Project saved to Supabase with ID: {project_db_id}")

            # Save project documentation (requirements + AI-generated docs)
            self._save_project_documents(project_db_id, state)

            # Insert user stories
            user_stories = state.get("user_stories", [])
            if user_stories:
                stories_to_insert = []
                for story in user_stories:
                    stories_to_insert.append({
                        "project_id": project_db_id,  # Use the actual UUID from projects table
                        "story_id": story.get("id"),
                        "title": story.get("title"),
                        "description": story.get("description"),
                        "acceptance_criteria": story.get("acceptance_criteria", []),  # Send as array
                        "priority": story.get("priority"),
                        "estimated_points": story.get("estimated_points"),
                        "dependencies": story.get("dependencies", []),  # Send as array
                        "technical_notes": story.get("technical_notes")
                    })

                story_response = self.client.from_("user_stories").insert(stories_to_insert).execute()
                print(f"📝 Saved {len(story_response.data)} user stories to Supabase.")

                # Create story ID mapping for tasks
                story_id_map = {story['story_id']: story['id'] for story in story_response.data}

                # Insert tasks
                tasks = state.get("tasks", [])
                if tasks:
                    tasks_to_insert = []
                    for task in tasks:
                        db_story_id = story_id_map.get(task.get("story_id"))
                        if db_story_id:
                            tasks_to_insert.append({
                                "story_id": db_story_id,
                                "task_id": task.get("id"),
                                "title": task.get("title"),
                                "description": task.get("description"),
                                "category": task.get("category"),
                                "estimated_hours": task.get("estimated_hours"),
                                "priority": task.get("priority", "medium"),
                                "acceptance_criteria": task.get("acceptance_criteria", []),  # Send as array
                                "technical_notes": task.get("technical_notes", ""),
                                "dependencies": task.get("dependencies", [])  # Send as array
                            })

                    if tasks_to_insert:
                        task_response = self.client.from_("tasks").insert(tasks_to_insert).execute()
                        print(f"✅ Saved {len(task_response.data)} tasks to Supabase.")

            # Update state with success
            state["supabase_project_id"] = project_db_id
            state["storage_success"] = True
            state["current_phase"] = "storage_complete"

            processing_time = (datetime.now() - start_time).total_seconds()
            if "processing_time" not in state:
                state["processing_time"] = {}
            state["processing_time"]["supabase_storage"] = processing_time

            print(f"[SUPABASE] Data storage completed in {processing_time:.1f}s")

        except Exception as e:
            error_msg = f"Supabase storage failed: {str(e)}"
            print(f"[SUPABASE_ERROR] {error_msg}")
            state["storage_success"] = False
            state["storage_error"] = error_msg
            state["current_phase"] = "storage_failed"
            import traceback
            traceback.print_exc()

        return state

    def _save_project_documents(self, project_db_id: str, state: ProjectManagementState):
        """
        Save project documentation to project_documents table.
        Stores original requirements, uploaded files content, and AI-generated docs.
        """
        try:
            documents_to_insert = []
            
            # 1. Save original text requirements if provided
            client_requirements = state.get("client_requirements", "")
            documentation = state.get("documentation", {})
            
            # Extract primary requirements from documentation structure
            primary_requirements = ""
            document_content = ""
            
            if documentation and documentation.get("content"):
                full_content = documentation["content"]
                
                # Parse multimodal structure
                if "=== PROJECT REQUIREMENTS (TEXT) ===" in full_content:
                    parts = full_content.split("=== PROJECT REQUIREMENTS (TEXT) ===")
                    if len(parts) > 1:
                        primary_section = parts[1].split("=== DOCUMENT:")[0]
                        primary_requirements = primary_section.strip()
                        
                        # Extract document sections
                        doc_parts = full_content.split("=== DOCUMENT:")
                        if len(doc_parts) > 1:
                            document_content = "\n\n".join(doc_parts[1:])
                else:
                    # Single source - treat as requirements
                    primary_requirements = full_content
            elif client_requirements:
                # Fallback to client_requirements
                primary_requirements = client_requirements
            
            # Save primary text requirements
            if primary_requirements:
                documents_to_insert.append({
                    "project_id": project_db_id,
                    "document_type": "requirements_text",
                    "title": "Original Client Requirements (Text Input)",
                    "content": primary_requirements,
                    "metadata": json.dumps({
                        "source": "user_input",
                        "word_count": len(primary_requirements.split()),
                        "char_count": len(primary_requirements),
                        "timestamp": datetime.now().isoformat()
                    })
                })
            
            # 2. Save uploaded document content if provided
            if document_content:
                documents_to_insert.append({
                    "project_id": project_db_id,
                    "document_type": "requirements_file",
                    "title": "Uploaded Requirements Document",
                    "content": document_content[:50000],  # Limit to 50k chars for storage
                    "file_name": documentation.get("title", "requirements_document.pdf"),
                    "metadata": json.dumps({
                        "source": "uploaded_file",
                        "document_type": documentation.get("document_type", "Unknown"),
                        "word_count": len(document_content.split()),
                        "char_count": len(document_content),
                        "timestamp": datetime.now().isoformat()
                    })
                })
            
            # 3. Save AI-generated documentation (structured analysis)
            multimodal_metadata = state.get("multimodal_metadata", {})
            if multimodal_metadata:
                source_analysis = multimodal_metadata.get("source_analysis", {})
                
                # Create a readable summary document
                ai_doc_content = f"""# AI-Generated Project Analysis

## Core Features
{chr(10).join(f'- {f}' for f in source_analysis.get('core_features', [])[:10])}

## Identified Stakeholders
{chr(10).join(f'- {s}' for s in source_analysis.get('stakeholders', [])[:10])}

## Technical Constraints
{chr(10).join(f'- {c}' for c in source_analysis.get('technical_constraints', [])[:10])}

## Business Goals
{chr(10).join(f'- {g}' for g in source_analysis.get('business_goals', [])[:10])}

## Conflicts Identified
{chr(10).join(f'- {c}' for c in source_analysis.get('conflicts', [])[:5]) if source_analysis.get('conflicts') else 'None'}

## Gaps to Address
{chr(10).join(f'- {g}' for g in source_analysis.get('gaps', [])[:5]) if source_analysis.get('gaps') else 'None'}

## Generation Metadata
- User Stories Generated: {len(state.get('user_stories', []))}
- Tasks Generated: {len(state.get('tasks', []))}
- Validation Score: {state.get('validation_score', 0):.1f}/100
- Iterations: {state.get('iteration_count', 0)}
"""
                
                documents_to_insert.append({
                    "project_id": project_db_id,
                    "document_type": "ai_generated",
                    "title": "AI-Generated Project Analysis",
                    "content": ai_doc_content,
                    "metadata": json.dumps({
                        "source": "gemini_analysis",
                        "model": "gemini-2.5-pro",
                        "validation_score": state.get("validation_score", 0),
                        "iteration_count": state.get("iteration_count", 0),
                        "story_count": len(state.get("user_stories", [])),
                        "task_count": len(state.get("tasks", [])),
                        "timestamp": datetime.now().isoformat()
                    })
                })
            
            # Insert all documents
            if documents_to_insert:
                response = self.client.from_("project_documents").insert(documents_to_insert).execute()
                print(f"📚 Saved {len(response.data)} project documents to Supabase.")
            else:
                print("[SUPABASE] No project documents to save.")
                
        except Exception as e:
            print(f"[SUPABASE_ERROR] Failed to save project documents: {e}")
            import traceback
            traceback.print_exc()
            # Don't fail the entire save operation if documents fail

    def save_project_data(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Save project data to Supabase from a dictionary (API-compatible method).
        
        This method provides the same functionality as the original SupabaseStorageAgent
        but with graceful error handling and availability checking.
        """
        if not self.available:
            print("⚠️ Supabase not available, cannot save project data.")
            return None

        try:
            # 1. Create the Project
            # Use project title if available, otherwise generate from project_id
            project_title = None
            if data.get("project_context"):
                project_title = data["project_context"].get("title") or data["project_context"].get("name")
            
            project_name = project_title or f"Project_{data.get('project_id', 'Unnamed')}"
            project_data = {
                "name": project_name,
                "project_context": data.get("project_context"),
                "validation_score": data.get("validation_score"),
                "iterations": data.get("iterations"),
                "status": data.get("status"),
                "source_info": data.get("source_info")
            }
            
            # Add GitHub repository information if provided
            if data.get("project_context"):
                if data["project_context"].get("github_repo_full_name"):
                    project_data["github_repo_full_name"] = data["project_context"]["github_repo_full_name"]
                if data["project_context"].get("github_repo_url"):
                    project_data["github_repo_url"] = data["project_context"]["github_repo_url"]
            
            # Clean up None values
            project_data = {k: v for k, v in project_data.items() if v is not None}
            
            project_response = self.client.from_("projects").insert(project_data).execute()
            project_id = project_response.data[0]['id']
            print(f"📄 Project created in Supabase with ID: {project_id}")

            # 2. Prepare and Insert User Stories
            user_stories = data.get("user_stories", [])
            stories_to_insert = []
            for story in user_stories:
                stories_to_insert.append({
                    "project_id": project_id,
                    "story_id": story.get("id"),
                    "title": story.get("title"),
                    "description": story.get("description"),
                    "acceptance_criteria": story.get("acceptance_criteria", []),  # Send as array
                    "priority": story.get("priority"),
                    "estimated_points": story.get("estimated_points"),
                    "dependencies": story.get("dependencies", []),  # Send as array
                    "technical_notes": story.get("technical_notes"),
                    "source_traceability": story.get("source_traceability")
                })
            
            if stories_to_insert:
                story_response = self.client.from_("user_stories").insert(stories_to_insert).execute()
                print(f"📝 Inserted {len(story_response.data)} user stories.")
                
                story_id_map = {story['story_id']: story['id'] for story in story_response.data}

                # 3. Prepare and Insert Tasks
                tasks = data.get("tasks", [])
                if tasks:
                    tasks_to_insert = []
                    for task in tasks:
                        db_story_id = story_id_map.get(task.get("story_id"))
                        if db_story_id:
                            tasks_to_insert.append({
                                "story_id": db_story_id,
                                "task_id": task.get("id"),
                                "title": task.get("title"),
                                "description": task.get("description"),
                                "category": task.get("category"),
                                "estimated_hours": task.get("estimated_hours"),
                                "dependencies": task.get("dependencies", []),  # Send as array
                                "priority": task.get("priority"),
                                "acceptance_criteria": task.get("acceptance_criteria", []),  # Send as array
                                "technical_notes": task.get("technical_notes")
                            })
                    
                    if tasks_to_insert:
                        task_response = self.client.from_("tasks").insert(tasks_to_insert).execute()
                        print(f"✅ Inserted {len(task_response.data)} tasks.")

            return project_id

        except Exception as e:
            print(f"❌ Error saving data to Supabase: {e}")
            import traceback
            traceback.print_exc()
            return None
