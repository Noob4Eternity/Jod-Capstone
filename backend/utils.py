# ==================== UTILITY FUNCTIONS FOR TYPE SAFETY ====================

from typing import Any, List, Dict
import re

def safe_string_extract(obj: Any) -> str:
    """Safely extract string from various object types"""
    if isinstance(obj, str):
        return obj
    elif isinstance(obj, dict):
        # Try common string fields in dictionaries
        for key in ['text', 'content', 'description', 'title', 'value']:
            if key in obj and isinstance(obj[key], str):
                return obj[key]
        # Fall back to string representation
        return str(obj)
    elif isinstance(obj, (list, tuple)):
        # Join list elements if they're strings
        string_items = [safe_string_extract(item) for item in obj if item]
        return ' '.join(string_items)
    elif obj is None:
        return ""
    else:
        return str(obj)

def safe_list_extract(obj: Any) -> List[str]:
    """Safely extract list of strings from various object types"""
    if isinstance(obj, list):
        return [safe_string_extract(item) for item in obj if item]
    elif isinstance(obj, str):
        # Split string by common delimiters
        if ',' in obj:
            return [item.strip() for item in obj.split(',') if item.strip()]
        elif ';' in obj:
            return [item.strip() for item in obj.split(';') if item.strip()]
        else:
            return [obj] if obj.strip() else []
    elif obj is None:
        return []
    else:
        return [safe_string_extract(obj)]

def normalize_analysis_data(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize analysis data to ensure consistent types"""
    normalized = {}
    
    # Define expected fields and their types
    field_configs = {
        'core_features': (list, []),
        'stakeholders': (list, ['user']),
        'technical_constraints': (list, []),
        'business_goals': (list, []),
        'conflicts': (list, []),
        'gaps': (list, [])
    }
    
    for field, (expected_type, default_value) in field_configs.items():
        raw_value = analysis.get(field, default_value)
        
        if expected_type == list:
            normalized[field] = safe_list_extract(raw_value)
        else:
            normalized[field] = default_value
    
    return normalized

def _clean_extracted_text(text: str) -> str:
    """Clean and normalize extracted text from documents"""
    # Remove excessive whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    
    # Remove strange characters that sometimes appear in PDFs
    text = re.sub(r'[^\w\s\.,;:!?\-()[\]{}"\'/\\+=*&%$#@|<>~`]', '', text)
    
    # Fix common PDF extraction issues
    text = text.replace('•', '-')
    text = text.replace('○', '-')
    text = text.replace('▪', '-')
    
    return text.strip()