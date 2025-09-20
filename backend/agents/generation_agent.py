# ==================== ENHANCED USER STORY GENERATION AGENT ====================

from typing import TypedDict, List, Dict, Optional, Any, Union
from datetime import datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import os
import re
import json
# Import dependencies with fallback for direct execution
try:
    # Try relative imports (when imported as module)
    from ..state import ProjectManagementState
    from ..utils import safe_string_extract, safe_list_extract, normalize_analysis_data
    from ..constants import USER_STORY_JSON_SCHEMA
except ImportError:
    # Fallback to absolute imports (when run directly)
    from state import ProjectManagementState
    from utils import safe_string_extract, safe_list_extract, normalize_analysis_data
    from constants import USER_STORY_JSON_SCHEMA

class MultimodalUserStoryGenerationAgent:
    """Enhanced agent for generating user stories from multimodal inputs (text + PDF)"""
    
    def __init__(self, gemini_api_key: str = None, temperature: float = 0.3):
        api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY must be provided either as parameter or environment variable")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            temperature=0.8,
            google_api_key=api_key
        )
        
        # Enhanced multimodal story generation prompt
        self.multimodal_story_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are an expert Product Manager + Agile BA generating HIGH-QUALITY user stories from MULTIMODAL requirements.

You receive requirements from multiple sources with different priorities:
1. PRIMARY REQUIREMENTS (user text input) - HIGHEST PRIORITY
2. SUPPORTING DOCUMENTATION (PDF content) - CONTEXT & REFERENCE
3. PROJECT CONTEXT - TECHNICAL & BUSINESS CONSTRAINTS

MULTIMODAL PROCESSING RULES:
- PRIMARY requirements take precedence over document content
- Use documents to add context, clarify ambiguities, and fill gaps
- Identify and resolve conflicts between sources (favor primary requirements)
- Extract stakeholders, constraints, and success criteria from all sources
- Generate stories that satisfy primary requirements while incorporating relevant document insights

OUTPUT CONTRACT: {json_schema}

QUALITY STANDARDS:
- Format: "As a [persona], I want [capability] so that [benefit]"
- Acceptance Criteria: 3-7 measurable, testable criteria per story
- Dependencies: Valid story IDs only, no circular dependencies
- Technical Notes: Actionable implementation guidance
- Coverage: Address ALL primary requirements and relevant document features

SCORING ALIGNMENT (100 points):
Format(15) + Completeness(20) + Requirements Coverage(25) + Source Integration(10) + NFR Coverage(10) + Dependencies(10) + Acceptance Criteria Quality(10)

Return ONLY the JSON array of story objects."""
            ),
            (
                "human",
                """MULTIMODAL REQUIREMENTS INPUT:

=== PRIMARY REQUIREMENTS (User Input - HIGHEST PRIORITY) ===
{primary_requirements}

=== SUPPORTING DOCUMENTATION (PDF Content - Context & Reference) ===
{document_content}

=== SOURCE ANALYSIS ===
{source_analysis}

=== CONFLICT RESOLUTION ===
{conflict_resolution}

=== PROJECT CONTEXT ===
{project_context}

=== VALIDATION FEEDBACK (if applicable) ===
{feedback_section}

INSTRUCTIONS:
1. Prioritize PRIMARY REQUIREMENTS as the main specification
2. Use SUPPORTING DOCUMENTATION to enhance, clarify, and provide context
3. Resolve any conflicts between sources (favor primary requirements)
4. Extract personas from all sources (stakeholders, roles mentioned)
5. Include security/performance/scalability if implied in any source
6. Generate comprehensive technical notes incorporating insights from all sources
7. Ensure all primary requirements are fully covered
{iteration_instructions}

OUTPUT: JSON array ONLY. No surrounding text.
{feedback_focus}"""
            ),
        ])
        
        # Content analysis prompt for multimodal processing
        self.content_analysis_prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """Analyze multimodal requirements input to extract key information for story generation.

IMPORTANT: Return all data as simple strings and arrays of strings only. No nested objects.

Extract and categorize:
1. Core Features: Main functionalities required (return as array of strings)
2. Stakeholders: All user types, roles mentioned across sources (return as array of strings)
3. Technical Constraints: Technology, performance, security requirements (return as array of strings)
4. Business Goals: Objectives, success criteria, KPIs (return as array of strings)
5. Conflicts: Any contradictions between primary and document sources (return as array of strings)
6. Gaps: Missing information that needs clarification (return as array of strings)

Return structured analysis as JSON with arrays of strings only."""
            ),
            (
                "human",
                """PRIMARY REQUIREMENTS:
{primary_text}

DOCUMENT CONTENT:
{document_text}

Analyze and return JSON with: core_features, stakeholders, technical_constraints, business_goals, conflicts, gaps
All fields must be arrays of strings. No nested objects or complex data structures."""
            ),
        ])
        
        self.parser = JsonOutputParser()
    
    def _parse_multimodal_documentation(self, state: ProjectManagementState) -> Dict[str, Any]:
        """
        Parse and organize multimodal content by source type and priority.
        Returns structured analysis for intelligent story generation.
        """
        print(f"[DEBUG] === PARSING MULTIMODAL INPUT ===")
        print(f"[DEBUG] State keys: {list(state.keys())}")
        print(f"[DEBUG] client_requirements length: {len(state.get('client_requirements', ''))}")
        print(f"[DEBUG] documentation exists: {bool(state.get('documentation'))}")
        
        # Extract different content sources
        primary_requirements = ""
        document_content = ""
        source_metadata = {
            "has_primary_text": False,
            "has_documents": False,
            "document_count": 0,
            "content_distribution": {}
        }
        
        # Check for structured documentation (from unified API)
        if state.get("documentation"):
            doc = state["documentation"]
            full_content = doc.get("content", "")
            
            print(f"[DEBUG] documentation content length: {len(full_content)}")
            print(f"[DEBUG] content preview: {full_content[:300]}...")
            
            # Parse structured multimodal content
            if "=== PROJECT REQUIREMENTS (TEXT) ===" in full_content:
                print("[DEBUG] ✓ Found multimodal structure")
                # Split multimodal content
                parts = full_content.split("=== PROJECT REQUIREMENTS (TEXT) ===")
                if len(parts) > 1:
                    # Extract primary requirements
                    primary_section = parts[1].split("=== DOCUMENT:")[0]
                    primary_requirements = primary_section.strip()
                    source_metadata["has_primary_text"] = True
                    
                    # Extract document sections
                    document_sections = []
                    doc_parts = full_content.split("=== DOCUMENT:")
                    for i, part in enumerate(doc_parts[1:], 1):
                        document_sections.append(f"Document {i}: {part.strip()}")
                        source_metadata["document_count"] += 1
                    
                    if document_sections:
                        document_content = "\n\n".join(document_sections)
                        source_metadata["has_documents"] = True
            else:
                print("[DEBUG] ✗ No multimodal structure found - treating as document-only")
                # Single source content (likely PDF only) - treat as primary requirements
                primary_requirements = full_content
                source_metadata["has_primary_text"] = True
                source_metadata["document_count"] = 1
        
        # Fallback to client_requirements (backward compatibility)
        if not primary_requirements and not document_content:
            primary_requirements = state.get("client_requirements", "")
            source_metadata["has_primary_text"] = bool(primary_requirements)
            print(f"[DEBUG] Using client_requirements fallback: {len(primary_requirements)} chars")
        
        # Calculate content distribution
        total_length = len(primary_requirements) + len(document_content)
        if total_length > 0:
            source_metadata["content_distribution"] = {
                "primary_percentage": len(primary_requirements) / total_length * 100,
                "document_percentage": len(document_content) / total_length * 100
            }
        
        print(f"[DEBUG] Final primary_requirements: {len(primary_requirements)} chars")
        print(f"[DEBUG] Final document_content: {len(document_content)} chars")
        print(f"[DEBUG] Source metadata: {source_metadata}")
        
        return {
            "primary_requirements": primary_requirements,
            "document_content": document_content,
            "source_metadata": source_metadata,
            "project_context": state.get("project_context", {})
        }
    
    def _analyze_multimodal_content(self, primary_text: str, document_text: str) -> Dict[str, Any]:
        """
        Analyze multimodal content to extract structured insights for story generation.
        Returns analysis of features, stakeholders, conflicts, etc.
        """
        if not primary_text and not document_text:
            return normalize_analysis_data({
                "core_features": [],
                "stakeholders": ["user", "administrator"],
                "technical_constraints": [],
                "business_goals": [],
                "conflicts": [],
                "gaps": ["No requirements provided"]
            })
        
        try:
            chain = self.content_analysis_prompt | self.llm | self.parser
            analysis = chain.invoke({
                "primary_text": primary_text or "No primary text provided",
                "document_text": document_text or "No document content provided"
            })
            
            # Normalize the analysis to ensure consistent types
            normalized_analysis = normalize_analysis_data(analysis)
            
            print(f"[CONTENT_ANALYSIS] Extracted {len(normalized_analysis.get('core_features', []))} features")
            print(f"[CONTENT_ANALYSIS] Identified {len(normalized_analysis.get('stakeholders', []))} stakeholders")
            
            return normalized_analysis
            
        except Exception as e:
            print(f"[CONTENT_ANALYSIS_ERROR] {e}")
            # Return basic analysis on failure
            return normalize_analysis_data({
                "core_features": ["Core functionality from requirements"],
                "stakeholders": ["user", "administrator"],
                "technical_constraints": [],
                "business_goals": [],
                "conflicts": [f"Analysis failed: {str(e)}"],
                "gaps": ["Manual review recommended"]
            })
    
    def _resolve_source_conflicts(self, analysis: Dict[str, Any], primary_text: str, document_text: str) -> str:
        """
        Generate conflict resolution guidance for the LLM prompt.
        """
        conflicts = analysis.get("conflicts", [])
        
        if not conflicts:
            return "No conflicts detected between sources. Integrate all requirements harmoniously."
        
        resolution_guidance = ["CONFLICTS DETECTED - RESOLUTION STRATEGY:"]
        
        for i, conflict in enumerate(conflicts, 1):
            conflict_str = safe_string_extract(conflict)
            resolution_guidance.append(f"{i}. CONFLICT: {conflict_str}")
            resolution_guidance.append(f"   RESOLUTION: Prioritize primary requirements, use documents for context only")
        
        resolution_guidance.append("\nGENERAL RULE: When in doubt, favor explicit primary requirements over document implications.")
        
        return "\n".join(resolution_guidance)
    
    def _create_source_analysis_summary(self, analysis: Dict[str, Any], source_metadata: Dict[str, Any]) -> str:
        """
        Create a summary of source analysis for the LLM prompt.
        """
        summary_parts = []
        
        try:
            # Source composition
            if source_metadata.get("has_primary_text") and source_metadata.get("has_documents"):
                dist = source_metadata.get("content_distribution", {})
                summary_parts.append(f"MULTIMODAL INPUT: {dist.get('primary_percentage', 0):.0f}% primary text, {dist.get('document_percentage', 0):.0f}% documents")
            elif source_metadata.get("has_primary_text"):
                summary_parts.append("INPUT TYPE: Primary text requirements only")
            elif source_metadata.get("has_documents"):
                summary_parts.append(f"INPUT TYPE: Document-based requirements ({source_metadata.get('document_count', 1)} documents)")
            
            # Key extracted elements
            core_features = analysis.get('core_features', [])
            summary_parts.append(f"CORE FEATURES IDENTIFIED: {len(core_features)}")
            
            # Safe handling of stakeholders
            stakeholders = analysis.get('stakeholders', [])
            if stakeholders:
                stakeholder_strings = [safe_string_extract(s) for s in stakeholders[:5] if s]
                stakeholder_strings = [s for s in stakeholder_strings if s.strip()]  # Filter empty
                if stakeholder_strings:
                    summary_parts.append(f"STAKEHOLDERS IDENTIFIED: {', '.join(stakeholder_strings)}")
            
            # Safe handling of technical constraints
            tech_constraints = analysis.get("technical_constraints", [])
            if tech_constraints:
                constraint_strings = [safe_string_extract(c) for c in tech_constraints[:3] if c]
                constraint_strings = [c for c in constraint_strings if c.strip()]  # Filter empty
                if constraint_strings:
                    summary_parts.append(f"TECHNICAL CONSTRAINTS: {', '.join(constraint_strings)}")
            
            # Safe handling of business goals
            business_goals = analysis.get("business_goals", [])
            if business_goals:
                goal_strings = [safe_string_extract(g) for g in business_goals[:3] if g]
                goal_strings = [g for g in goal_strings if g.strip()]  # Filter empty
                if goal_strings:
                    summary_parts.append(f"BUSINESS GOALS: {', '.join(goal_strings)}")
            
            # Safe handling of gaps
            gaps = analysis.get("gaps", [])
            if gaps:
                gap_strings = [safe_string_extract(g) for g in gaps[:2] if g]
                gap_strings = [g for g in gap_strings if g.strip()]  # Filter empty
                if gap_strings:
                    summary_parts.append(f"GAPS IDENTIFIED: {', '.join(gap_strings)}")
            
        except Exception as e:
            print(f"[SOURCE_ANALYSIS_ERROR] Error creating summary: {e}")
            summary_parts = [
                "INPUT TYPE: Requirements provided",
                "CORE FEATURES IDENTIFIED: Analysis in progress",
                "STAKEHOLDERS IDENTIFIED: user, administrator"
            ]
        
        return "\n".join(summary_parts)
    
    def _format_multimodal_feedback(self, state: ProjectManagementState) -> tuple:
        """
        Format validation feedback specifically for multimodal iteration improvements.
        """
        iteration_count = state.get("iteration_count", 0)
        
        if iteration_count == 0:
            return "", "", ""
        
        feedback_section = "\n=== MULTIMODAL VALIDATION FEEDBACK ===\n"
        iteration_instructions = "\n6. **CRITICAL**: Address multimodal feedback and improve source integration"
        feedback_focus = "\n6. **Improve multimodal processing and source coverage**"
        
        detailed_feedback = state.get("detailed_feedback", {})
        
        if detailed_feedback:
            feedback_section += f"**Validation Score**: {state.get('validation_score', 0):.1f}/100\n\n"
            
            # Source coverage issues
            if detailed_feedback.get("missing_requirements"):
                feedback_section += "**MISSING REQUIREMENTS (check all sources)**:\n"
                for req in detailed_feedback["missing_requirements"]:
                    feedback_section += f"- {req}\n"
                feedback_section += "\n"
            
            # Multimodal integration feedback
            if detailed_feedback.get("recommendations"):
                feedback_section += "**MULTIMODAL INTEGRATION IMPROVEMENTS**:\n"
                for rec in detailed_feedback["recommendations"]:
                    feedback_section += f"- {rec}\n"
                feedback_section += "\n"
            
            # Critical issues
            if detailed_feedback.get("critical_issues"):
                feedback_section += "**CRITICAL ISSUES TO FIX**:\n"
                for issue in detailed_feedback["critical_issues"]:
                    feedback_section += f"- {issue}\n"
                feedback_section += "\n"
        
        # Previous iteration reference
        previous_stories = state.get("previous_user_stories", [])
        if previous_stories:
            feedback_section += f"**PREVIOUS ITERATION**: {len(previous_stories)} stories generated - improve based on feedback\n"
        
        return feedback_section, iteration_instructions, feedback_focus
    
    def generate_stories(self, state: ProjectManagementState) -> ProjectManagementState:
        """
        Enhanced story generation method with full multimodal support.
        """
        start_time = datetime.now()
        
        try:
            # Store previous stories
            current_stories = state.get("user_stories", [])
            if current_stories:
                state["previous_user_stories"] = current_stories
            
            # Parse multimodal content
            multimodal_data = self._parse_multimodal_documentation(state)
            primary_requirements = multimodal_data["primary_requirements"]
            document_content = multimodal_data["document_content"]
            source_metadata = multimodal_data["source_metadata"]
            project_context = multimodal_data["project_context"]
            
            # Analyze content across sources
            content_analysis = self._analyze_multimodal_content(primary_requirements, document_content)
            
            # Create source analysis summary
            source_analysis = self._create_source_analysis_summary(content_analysis, source_metadata)
            
            # Resolve conflicts between sources
            conflict_resolution = self._resolve_source_conflicts(content_analysis, primary_requirements, document_content)
            
            # Format validation feedback for iteration
            feedback_section, iteration_instructions, feedback_focus = self._format_multimodal_feedback(state)
            
            # Log multimodal processing info
            iteration_count = state.get("iteration_count", 0)
            print(f"[MULTIMODAL_GEN] Iteration {iteration_count + 1}")
            print(f"[MULTIMODAL_GEN] Primary text: {len(primary_requirements)} chars")
            print(f"[MULTIMODAL_GEN] Document content: {len(document_content)} chars")
            print(f"[MULTIMODAL_GEN] Features identified: {len(content_analysis.get('core_features', []))}")
            
            # Safe stakeholder display
            stakeholders = content_analysis.get('stakeholders', [])
            if stakeholders:
                stakeholder_preview = [safe_string_extract(s) for s in stakeholders[:3]]
                stakeholder_preview = [s for s in stakeholder_preview if s.strip()]
                print(f"[MULTIMODAL_GEN] Stakeholders: {', '.join(stakeholder_preview)}")
            
            if content_analysis.get('conflicts'):
                print(f"[MULTIMODAL_GEN] Conflicts detected: {len(content_analysis['conflicts'])}")
            
            # Generate stories using enhanced multimodal prompt
            chain = self.multimodal_story_prompt | self.llm | self.parser
            
            raw_stories = chain.invoke({
                "primary_requirements": primary_requirements or "No primary requirements provided",
                "document_content": document_content or "No supporting documentation provided",
                "source_analysis": source_analysis,
                "conflict_resolution": conflict_resolution,
                "project_context": json.dumps(project_context) if project_context else "No specific context",
                "feedback_section": feedback_section,
                "iteration_instructions": iteration_instructions,
                "feedback_focus": feedback_focus,
                "json_schema": USER_STORY_JSON_SCHEMA
            })
            
            # Ensure we have a list
            if not isinstance(raw_stories, list):
                raw_stories = [raw_stories] if raw_stories else []
            
            # Validate and enhance each story with multimodal insights
            validated_stories = []
            for idx, story in enumerate(raw_stories):
                story_id = story.get("id", f"US{idx+1:03d}")
                
                # Enhanced technical notes with multimodal insights
                technical_notes = story.get("technical_notes", "")
                tech_constraints = content_analysis.get("technical_constraints", [])
                if tech_constraints:
                    constraint_strings = [safe_string_extract(c) for c in tech_constraints[:2] if c]
                    constraint_strings = [c for c in constraint_strings if c.strip()]
                    if constraint_strings:
                        technical_notes += f" Consider: {', '.join(constraint_strings)}"
                
                validated_story = {
                    "id": story_id,
                    "title": story.get("title", ""),
                    "description": story.get("description", ""),
                    "acceptance_criteria": story.get("acceptance_criteria", []),
                    "priority": story.get("priority", "medium"),
                    "estimated_points": story.get("estimated_points", 3),
                    "dependencies": story.get("dependencies", []),
                    "technical_notes": technical_notes.strip(),
                    "source_traceability": {
                        "primary_coverage": bool(primary_requirements and any(
                            word in story.get("title", "").lower() + story.get("description", "").lower()
                            for word in primary_requirements.lower().split()[:10]
                        )),
                        "document_coverage": bool(document_content and any(
                            word in story.get("title", "").lower() + story.get("description", "").lower()
                            for word in document_content.lower().split()[:10]
                        ))
                    }
                }
                
                # Fix story format if needed
                if validated_story["title"] and not self._is_valid_story_format(validated_story["title"]):
                    validated_story["title"] = self._fix_story_format(validated_story["title"])
                
                # Ensure minimum acceptance criteria
                if len(validated_story["acceptance_criteria"]) < 3:
                    while len(validated_story["acceptance_criteria"]) < 3:
                        base_criteria = validated_story["acceptance_criteria"][-1] if validated_story["acceptance_criteria"] else "System responds successfully"
                        validated_story["acceptance_criteria"].append(f"Enhanced: {base_criteria}")
                
                validated_stories.append(validated_story)
            
            # Ensure sequential IDs
            for i, story in enumerate(validated_stories):
                story["id"] = f"US{i+1:03d}"
            
            # Enhanced coverage check with multimodal awareness
            validated_stories = self._ensure_multimodal_coverage(
                primary_requirements, document_content, content_analysis, validated_stories
            )
            
            # Update state with multimodal metadata
            state["user_stories"] = validated_stories
            state["current_phase"] = "story_validation"
            state["multimodal_metadata"] = {
                "source_analysis": content_analysis,
                "source_distribution": source_metadata.get("content_distribution", {}),
                "conflicts_resolved": len(content_analysis.get("conflicts", [])),
                "stories_with_primary_coverage": sum(1 for s in validated_stories if s.get("source_traceability", {}).get("primary_coverage", False)),
                "stories_with_document_coverage": sum(1 for s in validated_stories if s.get("source_traceability", {}).get("document_coverage", False))
            }
            
            processing_time = (datetime.now() - start_time).total_seconds()
            if "processing_time" not in state:
                state["processing_time"] = {}
            state["processing_time"]["multimodal_story_generation"] = processing_time
            
            print(f"[MULTIMODAL_GEN] Generated {len(validated_stories)} stories in {processing_time:.1f}s")
            
        except Exception as e:
            state["last_error"] = f"Multimodal story generation failed: {str(e)}"
            state["user_stories"] = []
            state["current_phase"] = "error"
            print(f"[MULTIMODAL_GEN_ERROR] {str(e)}")
            import traceback
            traceback.print_exc()
        
        return state
    
    def _ensure_multimodal_coverage(self, primary_text: str, document_text: str, analysis: Dict[str, Any], stories: List[Dict]) -> List[Dict]:
        """
        Enhanced coverage check that considers both primary requirements and document content.
        """
        all_content = f"{primary_text} {document_text}".lower()
        story_content = " ".join([
            f"{s.get('title', '')} {s.get('description', '')} {' '.join(s.get('acceptance_criteria', []))}"
            for s in stories
        ]).lower()
        
        missing_elements = []
        
        # Check coverage of identified core features (with safe string extraction)
        core_features = analysis.get("core_features", [])
        for feature in core_features[:5]:  # Check top 5 features
            feature_str = safe_string_extract(feature).lower()
            if feature_str and feature_str not in story_content:
                missing_elements.append(f"core_feature_{len(missing_elements)}")
        
        # Check technical constraints coverage
        technical_constraints = analysis.get("technical_constraints", [])
        for constraint in technical_constraints:
            constraint_str = safe_string_extract(constraint).lower()
            constraint_keywords = ["security", "performance", "scalability", "authentication"]
            if any(keyword in constraint_str for keyword in constraint_keywords):
                if not any(keyword in story_content for keyword in constraint_keywords):
                    missing_elements.append("technical_constraints")
                    break
        
        # Generate missing stories if needed
        if missing_elements:
            additional_stories = self._generate_multimodal_gap_stories(missing_elements, analysis, len(stories))
            stories.extend(additional_stories)
        
        return stories
    
    def _generate_multimodal_gap_stories(self, missing_elements: List[str], analysis: Dict[str, Any], current_count: int) -> List[Dict]:
        """
        Generate stories to fill gaps identified in multimodal analysis.
        """
        gap_stories = []
        
        # Templates enhanced with multimodal insights
        stakeholders = analysis.get("stakeholders", ["user", "administrator"])
        primary_stakeholder = "user"
        if stakeholders:
            primary_stakeholder_raw = stakeholders[0] if stakeholders else "user"
            primary_stakeholder = safe_string_extract(primary_stakeholder_raw)
            if not primary_stakeholder.strip():
                primary_stakeholder = "user"
        
        for idx, element in enumerate(missing_elements[:3]):  # Limit to 3 additional stories
            if element.startswith("core_feature_"):
                story = {
                    "id": f"US{current_count + idx + 1:03d}",
                    "title": f"As a {primary_stakeholder}, I want to access core system functionality so that I can complete essential tasks",
                    "description": "Implement core feature identified in requirements analysis but not covered by existing stories",
                    "acceptance_criteria": [
                        "Core functionality is accessible through the UI",
                        "Feature works according to requirements specification",
                        "Error handling is implemented for edge cases",
                        "Feature integrates properly with existing system"
                    ],
                    "priority": "high",
                    "estimated_points": 5,
                    "dependencies": [],
                    "technical_notes": f"Implement missing core feature identified in multimodal analysis. Reference both primary requirements and supporting documentation."
                }
            elif element == "technical_constraints":
                # Safe extraction of technical constraints
                tech_constraints = analysis.get('technical_constraints', [])
                constraint_strings = [safe_string_extract(c) for c in tech_constraints[:3] if c]
                constraint_strings = [c for c in constraint_strings if c.strip()]
                constraints_text = ', '.join(constraint_strings) if constraint_strings else "various technical requirements"
                
                story = {
                    "id": f"US{current_count + idx + 1:03d}",
                    "title": f"As a system administrator, I want robust technical infrastructure so that the system meets all constraints",
                    "description": "Implement technical requirements and constraints identified across multiple requirement sources",
                    "acceptance_criteria": [
                        "System meets performance requirements",
                        "Security constraints are properly implemented",
                        "Scalability requirements are addressed",
                        "Technical documentation is complete"
                    ],
                    "priority": "high",
                    "estimated_points": 8,
                    "dependencies": [],
                    "technical_notes": f"Address technical constraints from multimodal analysis: {constraints_text}"
                }
            else:
                # Generic gap story
                story = {
                    "id": f"US{current_count + idx + 1:03d}",
                    "title": f"As a {primary_stakeholder}, I want complete system coverage so that all requirements are addressed",
                    "description": "Address requirements gap identified in multimodal analysis",
                    "acceptance_criteria": [
                        "Gap in requirements is properly addressed",
                        "Implementation aligns with both primary and document requirements",
                        "Functionality is tested and validated"
                    ],
                    "priority": "medium",
                    "estimated_points": 3,
                    "dependencies": [],
                    "technical_notes": "Fill requirements gap identified through multimodal content analysis"
                }
            
            gap_stories.append(story)
        
        return gap_stories
    
    def _is_valid_story_format(self, title: str) -> bool:
        """Check if story follows the standard format"""
        pattern = r"^As a .+, I want .+ so that .+"
        return bool(re.match(pattern, title, re.IGNORECASE))
    
    def _fix_story_format(self, title: str) -> str:
        """Attempt to fix story format"""
        if "want" in title.lower():
            return title
        return f"As a user, I want {title} so that I can complete my tasks"