# ==================== UTILITY FUNCTIONS ====================

import os
import re
from typing import Optional, Dict, Any

def create_multimodal_documentation(
    primary_requirements: str,
    document_path: Optional[str] = None,
    title: str = "Multimodal Project Requirements"
) -> Dict:
    """
    Create multimodal documentation from primary text and optional document file.
    This is the KEY function that formats content correctly for the multimodal agent.
    """
    
    content_parts = []
    
    # Always include primary requirements section
    if primary_requirements.strip():
        content_parts.append("=== PROJECT REQUIREMENTS (TEXT) ===")
        content_parts.append(primary_requirements.strip())
        content_parts.append("")  # Empty line
    
    # Add document content if provided
    if document_path and os.path.exists(document_path):
        try:
            document_content = _extract_text_from_file(document_path)
            if document_content.strip():
                filename = os.path.basename(document_path)
                content_parts.append(f"=== DOCUMENT: {filename} ===")
                content_parts.append(document_content.strip())
        except Exception as e:
            print(f"[WARNING] Failed to load document {document_path}: {e}")
    
    # Combine all content
    combined_content = "\n".join(content_parts)
    
    return {
        "document_type": "Combined Requirements Document",
        "title": title,
        "content": combined_content,
        "sections": {},
        "stakeholders": [],
        "business_goals": [],
        "technical_constraints": [],
        "success_criteria": []
    }

def _extract_text_from_file(file_path: str) -> str:
    """Extract text from various file formats"""
    file_extension = os.path.splitext(file_path)[1].lower()
    
    try:
        if file_extension == '.pdf':
            return _extract_text_from_pdf(file_path)
        elif file_extension == '.docx':
            return _extract_text_from_docx(file_path)
        elif file_extension in ['.txt', '.md']:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # Try as plain text
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        raise ValueError(f"Failed to extract text from {file_path}: {e}")

def _extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from PDF file"""
    try:
        import PyPDF2
        
        text_content = []
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page in pdf_reader.pages:
                text_content.append(page.extract_text())
        
        content = '\n'.join(text_content)
        return _clean_extracted_text(content)
        
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
        return _clean_extracted_text(content)
        
    except ImportError:
        raise ValueError("python-docx library not installed. Run: pip install python-docx")
    except Exception as e:
        raise ValueError(f"Failed to extract text from DOCX: {e}")

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