import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from typing import Dict, Any

class QCAgent:
    """
    An AI agent that performs quality control on code submissions
    by comparing them to task requirements and acceptance criteria.
    """

    def __init__(self, gemini_api_key: str = None):
        api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY must be provided")

        # Use a low temperature for reliable JSON output
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            temperature=0.2,
            google_api_key=api_key
        )

        # Define the system prompt with clear instructions and a JSON schema
        self.prompt_template = ChatPromptTemplate.from_template(
            """
            You are a Senior Software Engineer and an expert Quality Control analyst.
            Your task is to review a code submission (as a code diff) against its
            project requirements and provide a structured JSON review.

            **Analysis Context:**
            ---------------------
            **1. Parent User Story (Business Goal):**
            {story_description}

            **2. Task Description (Technical Goal):**
            {task_description}

            **3. Task Acceptance Criteria (Must-Haves):**
            {acceptance_criteria}
            ---------------------

            **Submitted Code (Diff format):**
            ```diff
            {code_diff}
            ```

            **Your Analysis Task:**
            1.  **Check Acceptance Criteria:** Go through each acceptance criterion one by one.
                Determine if the submitted code meets the criterion. Provide a brief explanation.
            2.  **Code Quality Review:** Briefly comment on code readability, best practices,
                and any potential logical errors or bugs.
            3.  **Security Check:** Perform a basic check for common security vulnerabilities
                (e.g., hardcoded secrets, potential injection risks, missing error handling).
            4.  **Assign Score:** Provide an overall "QC Score" from 0 to 100 based on your analysis.
            5.  **Set Final Status:**
                - If all criteria are met and no critical issues are found, set status to "Approved".
                - If any criteria are missed or critical issues are present, set status to "Changes Requested".

            **Output Format (JSON only):**
            Provide your review in a valid JSON object with the following schema:
            {{
              "status": "Approved" | "Changes Requested",
              "qc_score": <float, 0-100>,
              "detailed_feedback": {{
                "criteria_analysis": [
                  {{
                    "criterion": "<The acceptance criterion text>",
                    "met": <boolean>,
                    "reasoning": "<Your brief explanation>"
                  }}
                ],
                "quality_review": "<Your comments on code quality and bugs>",
                "security_review": "<Your comments on security>"
              }}
            }}
            """
        )

    def analyze_submission(self, task_details: Dict[str, Any], story_details: Dict[str, Any], code_diff: str) -> Dict[str, Any]:
        """
        Analyzes a code submission and returns a structured review.
        """
        parser = JsonOutputParser()

        # Format the inputs for the prompt
        prompt = self.prompt_template.format(
            story_description=story_details.get("description", "No story description provided."),
            task_description=task_details.get("description", "No task description provided."),
            acceptance_criteria="\n".join([f"- {ac}" for ac in task_details.get("acceptance_criteria", [])]),
            code_diff=code_diff
        )

        chain = self.llm | parser

        print("[QCAgent] Analyzing submission... Calling Gemini API.")

        try:
            # Invoke the chain to get the structured JSON review
            review = chain.invoke(prompt)
            return review

        except Exception as e:
            print(f"[QCAgent] Error during AI analysis: {e}")
            # Return a default error object if parsing or the API call fails
            return {
              "status": "Changes Requested",
              "qc_score": 0.0,
              "detailed_feedback": {
                "criteria_analysis": [],
                "quality_review": f"AI analysis failed: {str(e)}",
                "security_review": "AI analysis failed."
              }
            }