"""
Process sample documents for testing classification and routing
"""

import os
import sys
import sqlite3
from datetime import datetime

# Define functions from app.py
def extract_text_basic(file_path):
    """Basic text extraction with fallbacks."""
    text = ""
    
    try:
        # Try text files first
        if file_path.lower().endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                
    except Exception as e:
        print(f"Text extraction failed: {e}")
        text = f"Text extraction failed: {str(e)}"
    
    return text

def classify_document_basic(text):
    """Enhanced document classification with more document types."""
    if not text:
        return "unknown"
        
    text_lower = text.lower()
    
    # Define document types with associated keywords
    document_types = {
        "invoice": ["invoice", "bill", "payment", "amount due", "total due", "tax", "receipt", "purchase", "order", "price", "quantity", "subtotal"],
        "contract": ["contract", "agreement", "terms", "conditions", "legal", "parties", "signed", "binding", "clause", "hereby", "obligations"],
        "resume": ["resume", "cv", "curriculum vitae", "experience", "education", "skills", "job", "career", "employment", "reference", "qualification", "certification"],
        "report": ["report", "analysis", "summary", "findings", "conclusion", "results", "research", "data", "statistics", "quarterly", "annual"],
        "letter": ["letter", "dear", "sincerely", "regards", "attention", "thank you", "request", "inquiry", "responding"],
        "memo": ["memo", "memorandum", "internal", "office", "attention", "notification", "announcement"],
        "proposal": ["proposal", "project", "plan", "strategy", "initiative", "budget", "timeline", "objectives", "goals", "recommended"],
        "manual": ["manual", "guide", "instruction", "step", "procedure", "tutorial", "how to", "operation", "user guide"],
        "policy": ["policy", "guidelines", "compliance", "rules", "regulation", "procedure", "protocol", "standard operating procedure", "sop"],
        "financial": ["financial", "statement", "balance", "income", "revenue", "expense", "profit", "loss", "asset", "liability", "cash flow", "fiscal"]
    }
    
    # Score each document type based on keyword matches
    scores = {}
    for doc_type, keywords in document_types.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        scores[doc_type] = score
    
    # Find the document type with the highest score
    max_score = max(scores.values()) if scores else 0
    
    # If we have matches, return the document type with the highest score
    if max_score > 0:
        # Get all document types with the highest score
        best_matches = [doc_type for doc_type, score in scores.items() if score == max_score]
        return best_matches[0]  # Return the first best match
    
    # If no specific type is identified
    return "general"

def summarize_text_basic(text, max_sentences=3):
    """Basic text summarization."""
    if not text or len(text) < 100:
        return text
    
    # Simple sentence extraction
    sentences = text.split('.')
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    if len(sentences) <= max_sentences:
        return text
    
    # Return first few sentences as summary
    return '. '.join(sentences[:max_sentences]) + '.'

def main():
    # Connect to the database
    db_path = os.path.join('instance', 'documents.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Department mapping
    department_mapping = {
        'invoice': 'Finance',
        'financial': 'Finance',
        'contract': 'Legal',
        'policy': 'Legal',
        'resume': 'HR',
        'letter': 'Administration',
        'memo': 'Administration',
        'report': 'Analytics',
        'proposal': 'Business Development',
        'manual': 'Technical Documentation',
        'general': 'General Office'
    }
    
    # Process test_invoice.txt
    file_path = os.path.join('uploads', 'test_invoice.txt')
    if os.path.exists(file_path):
        # Extract text
        extracted_text = extract_text_basic(file_path)
        
        # Classify document
        doc_type = classify_document_basic(extracted_text)
        
        # Summarize
        summary = summarize_text_basic(extracted_text)
        
        # Get department
        department = department_mapping.get(doc_type, 'General Office')
        
        print(f'Test invoice - Type: {doc_type}, Department: {department}')
        
        # Create document record
        cursor.execute('''
            INSERT INTO document (filename, original_filename, file_type, file_size, upload_date, status, 
                                 extracted_text, summary, document_type, department)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'test_invoice.txt',
            'test_invoice.txt',
            'text/plain',
            os.path.getsize(file_path),
            datetime.now().isoformat(),
            'processed',
            extracted_text,
            summary,
            doc_type,
            department
        ))
        conn.commit()
    
    # Process test_contract.txt
    file_path = os.path.join('uploads', 'test_contract.txt')
    if os.path.exists(file_path):
        # Extract text
        extracted_text = extract_text_basic(file_path)
        
        # Classify document
        doc_type = classify_document_basic(extracted_text)
        
        # Summarize
        summary = summarize_text_basic(extracted_text)
        
        # Get department
        department = department_mapping.get(doc_type, 'General Office')
        
        print(f'Test contract - Type: {doc_type}, Department: {department}')
        
        # Create document record
        cursor.execute('''
            INSERT INTO document (filename, original_filename, file_type, file_size, upload_date, status, 
                                 extracted_text, summary, document_type, department)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'test_contract.txt',
            'test_contract.txt',
            'text/plain',
            os.path.getsize(file_path),
            datetime.now().isoformat(),
            'processed',
            extracted_text,
            summary,
            doc_type,
            department
        ))
        conn.commit()
    
    # Process test_resume.txt
    file_path = os.path.join('uploads', 'test_resume.txt')
    if os.path.exists(file_path):
        # Extract text
        extracted_text = extract_text_basic(file_path)
        
        # Classify document
        doc_type = classify_document_basic(extracted_text)
        
        # Summarize
        summary = summarize_text_basic(extracted_text)
        
        # Get department
        department = department_mapping.get(doc_type, 'General Office')
        
        print(f'Test resume - Type: {doc_type}, Department: {department}')
        
        # Create document record
        cursor.execute('''
            INSERT INTO document (filename, original_filename, file_type, file_size, upload_date, status, 
                                 extracted_text, summary, document_type, department)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'test_resume.txt',
            'test_resume.txt',
            'text/plain',
            os.path.getsize(file_path),
            datetime.now().isoformat(),
            'processed',
            extracted_text,
            summary,
            doc_type,
            department
        ))
        conn.commit()
    
    # Close connection
    conn.close()

if __name__ == "__main__":
    main()