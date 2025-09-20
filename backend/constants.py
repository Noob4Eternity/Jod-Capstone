# ==================== CONSTANTS / SCHEMA (API-READY) ====================

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