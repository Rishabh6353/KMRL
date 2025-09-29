"""
Gemini API-based Document Classification Service
This module provides document classification using Google's Gemini API for KMRL document processing.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple
import google.generativeai as genai

class GeminiDocumentClassifier:
    """
    Document classifier using Google's Gemini API.
    Provides classification for KMRL document types with confidence scores.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini classifier.
        
        Args:
            api_key: Google Gemini API key. If None, will use environment variable GEMINI_API_KEY
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model = None
        self.is_available = False
        
        # KMRL-specific document categories
        self.document_categories = [
            "Invoice",
            "Purchase Order",
            "Report",  # Combined Engineering Report + Incident Report
            "Policy / Circular",
            "Regulatory / Compliance",
            "Other"
        ]
        
        # Initialize Gemini if API key is available
        self._initialize_gemini()
        
        # Mock classification data for demo mode
        self.mock_classifications = {
            "invoice": {"type": "Invoice", "confidence": 0.92},
            "purchase_order": {"type": "Purchase Order", "confidence": 0.90},
            "report": {"type": "Report", "confidence": 0.85},
            "policy_circular": {"type": "Policy / Circular", "confidence": 0.88},
            "regulatory_compliance": {"type": "Regulatory / Compliance", "confidence": 0.87},
            "other": {"type": "Other", "confidence": 0.75}
        }
    
    def _initialize_gemini(self):
        """Initialize Gemini API client."""
        try:
            if self.api_key:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                self.is_available = True
                logging.info("✅ Gemini API initialized successfully")
            else:
                logging.warning("⚠️ Gemini API key not provided. Running in demo mode.")
                self.is_available = False
        except Exception as e:
            logging.error(f"❌ Failed to initialize Gemini API: {str(e)}")
            self.is_available = False
    
    def _create_classification_prompt(self, text: str) -> str:
        """
        Create a structured prompt for document classification.
        
        Args:
            text: Document text to classify
            
        Returns:
            Formatted prompt for Gemini API
        """
        prompt = f"""
You are an expert document classifier for KMRL (Kochi Metro Rail Limited). 

Analyze the following document text and classify it into EXACTLY ONE of these categories:

1. "Invoice" - If the document contains billing information, payment requests, financial amounts due, tax calculations, or invoice numbers
2. "Purchase Order" - If the document is requesting goods/services, contains procurement details, vendor information, or purchase requests
3. "Report" - If the document contains analysis, findings, investigations, performance data, engineering reports, or incident reports
4. "Policy / Circular" - If the document contains company policies, procedures, guidelines, circulars, or standard operating procedures
5. "Regulatory / Compliance" - If the document contains regulatory information, compliance requirements, legal directives, or audit findings
6. "Other" - Only if the document clearly doesn't fit any of the above categories

Document text to analyze:
{text[:3000]}

IMPORTANT INSTRUCTIONS:
- Choose the MOST APPROPRIATE category based on the document's primary purpose
- Be confident in your classification - avoid defaulting to "Other"
- Look for key indicators like amounts, dates, policy numbers, report titles, etc.
- Confidence should be high (0.8+) for clear documents, lower (0.6-0.8) for ambiguous ones

Respond with ONLY this JSON format (no other text):
{{
    "predicted_type": "Exact Category Name",
    "confidence": 0.85,
    "reasoning": "Specific explanation based on document content"
}}
"""
        return prompt
    
    def classify_document(self, text: str, document_name: str = "") -> Dict:
        """
        Classify a document using Gemini API or mock classification.
        
        Args:
            text: Document text content
            document_name: Name of the document (optional)
            
        Returns:
            Dictionary with classification results
        """
        if not text or len(text.strip()) < 10:
            return {
                "success": False,
                "error": "Text too short for classification",
                "document_name": document_name,
                "predicted_type": "Other",
                "confidence": 0.0
            }
        
        # Try Gemini API first
        if self.is_available:
            try:
                return self._classify_with_gemini(text, document_name)
            except Exception as e:
                logging.error(f"Gemini classification failed: {str(e)}")
                # Fallback to mock classification
                return self._classify_with_mock(text, document_name)
        else:
            # Use mock classification for demo mode
            return self._classify_with_mock(text, document_name)
    
    def _classify_with_gemini(self, text: str, document_name: str = "") -> Dict:
        """
        Classify document using Gemini API.
        
        Args:
            text: Document text content
            document_name: Name of the document
            
        Returns:
            Classification result dictionary
        """
        try:
            prompt = self._create_classification_prompt(text)
            response = self.model.generate_content(prompt)
            
            # Parse the JSON response
            response_text = response.text.strip()
            
            # Extract JSON from response (in case there's extra text)
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                result = json.loads(json_str)
                
                # Validate and clean the response
                predicted_type = result.get('predicted_type', 'Other')
                confidence = float(result.get('confidence', 0.5))
                reasoning = result.get('reasoning', 'No reasoning provided')
                
                # Ensure confidence is within valid range
                confidence = max(0.0, min(1.0, confidence))
                
                return {
                    "success": True,
                    "document_name": document_name,
                    "predicted_type": predicted_type,
                    "confidence": confidence,
                    "reasoning": reasoning,
                    "method": "gemini_api"
                }
            else:
                raise ValueError("Invalid JSON response format")
                
        except json.JSONDecodeError as e:
            logging.error(f"JSON parsing error: {str(e)}")
            raise Exception(f"Failed to parse Gemini response: {str(e)}")
        except Exception as e:
            logging.error(f"Gemini API error: {str(e)}")
            raise Exception(f"Gemini classification failed: {str(e)}")
    
    def _classify_with_mock(self, text: str, document_name: str = "") -> Dict:
        """
        Mock classification for demo mode when Gemini API key is not available.
        NOTE: This is NOT real Gemini AI classification - just keyword-based fallback.
        For actual Gemini AI classification, you MUST provide a valid GEMINI_API_KEY.
        
        Args:
            text: Document text content
            document_name: Name of the document
            
        Returns:
            Mock classification result
        """
        text_lower = text.lower()
        
        # Enhanced keyword-based classification
        invoice_score = sum(1 for keyword in ['invoice', 'bill', 'payment', 'amount due', 'total', '$', 'billing', 'tax', 'subtotal', 'payable'] if keyword in text_lower)
        po_score = sum(1 for keyword in ['purchase order', 'purchase request', 'procurement', 'vendor', 'order', 'material requisition', 'supplier', 'quote'] if keyword in text_lower)
        report_score = sum(1 for keyword in ['report', 'analysis', 'summary', 'finding', 'conclusion', 'engineering report', 'incident report', 'investigation', 'performance', 'monthly', 'quarterly'] if keyword in text_lower)
        policy_score = sum(1 for keyword in ['policy', 'procedure', 'guideline', 'circular', 'sop', 'standard operating', 'handbook', 'manual', 'rule'] if keyword in text_lower)
        regulatory_score = sum(1 for keyword in ['regulatory', 'compliance', 'legal', 'directive', 'audit', 'regulation', 'statutory', 'mandatory'] if keyword in text_lower)
        
        # Find the category with the highest score
        scores = {
            'invoice': invoice_score,
            'purchase_order': po_score,
            'report': report_score,
            'policy_circular': policy_score,
            'regulatory_compliance': regulatory_score
        }
        
        max_score = max(scores.values())
        if max_score > 0:
            best_category = max(scores, key=scores.get)
            result = self.mock_classifications[best_category]
        else:
            result = self.mock_classifications["other"]
        
        return {
            "success": True,
            "document_name": document_name,
            "predicted_type": result["type"],
            "confidence": result["confidence"],
            "reasoning": f"⚠️ DEMO MODE: This is NOT real Gemini AI classification. Set GEMINI_API_KEY for actual AI-powered classification.",
            "method": "mock_demo"
        }
    
    def batch_classify(self, documents: List[Dict]) -> List[Dict]:
        """
        Classify multiple documents.
        
        Args:
            documents: List of documents with 'text' and optionally 'name' keys
            
        Returns:
            List of classification results
        """
        results = []
        for i, doc in enumerate(documents):
            text = doc.get('text', '')
            name = doc.get('name', f'Document_{i+1}')
            
            result = self.classify_document(text, name)
            result['document_index'] = i
            results.append(result)
        
        return results
    
    def get_classification_categories(self) -> List[str]:
        """Get available classification categories."""
        return self.document_categories.copy()
    
    def is_api_available(self) -> bool:
        """Check if Gemini API is available."""
        return self.is_available
    
    def get_status(self) -> Dict:
        """Get classifier status information."""
        return {
            "api_available": self.is_available,
            "api_key_configured": bool(self.api_key),
            "categories": self.document_categories,
            "method": "gemini_api" if self.is_available else "mock_demo"
        }
