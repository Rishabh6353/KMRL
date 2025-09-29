#!/usr/bin/env python3
"""
Test script for the KMRL AI Document Classification system.
This script tests the Gemini classification functionality.
"""

import os
import sys
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_gemini_classifier():
    """Test the Gemini document classifier."""
    print("Testing Gemini Document Classifier")
    print("=" * 50)
    
    try:
        from backend.modules.classification.gemini_classification import GeminiDocumentClassifier
        
        # Initialize classifier
        classifier = GeminiDocumentClassifier()
        
        # Test status
        status = classifier.get_status()
        print(f"Classifier Status:")
        print(f"   - API Available: {status['api_available']}")
        print(f"   - API Key Configured: {status['api_key_configured']}")
        print(f"   - Method: {status['method']}")
        print(f"   - Categories: {', '.join(status['categories'])}")
        print()
        
        # Test documents
        test_documents = [
            {
                "name": "Invoice Sample",
                "text": """
                INVOICE
                Invoice Number: INV-2024-001
                Date: January 15, 2024
                Bill To: KMRL Headquarters
                Amount Due: $5,000.00
                Payment Terms: Net 30
                Total Amount: $5,000.00
                Tax: $500.00
                """
            },
            {
                "name": "Policy Document",
                "text": """
                KMRL EMPLOYEE HANDBOOK
                Policy Number: POL-2024-001
                Effective Date: January 1, 2024
                
                This policy outlines the procedures and guidelines for all KMRL employees.
                Compliance with these policies is mandatory for all staff members.
                
                Section 1: General Guidelines
                Section 2: Safety Procedures
                Section 3: Code of Conduct
                """
            },
            {
                "name": "Monthly Report",
                "text": """
                MONTHLY PERFORMANCE REPORT
                January 2024
                
                Executive Summary:
                This report provides an analysis of KMRL's performance metrics for January 2024.
                
                Key Findings:
                - Passenger ridership increased by 12%
                - On-time performance improved to 95%
                - Revenue exceeded targets by 8%
                
                Conclusion:
                January 2024 showed positive growth across all key metrics.
                """
            },
            {
                "name": "Purchase Order",
                "text": """
                PURCHASE ORDER
                PO Number: PO-2024-001
                Vendor: Metro Equipment Ltd.
                
                Please supply the following items:
                - 50 LED Display Units
                - 25 Ticket Vending Machines
                - 100 Security Cameras
                
                Delivery Address: KMRL Station Complex
                Total Value: $150,000.00
                """
            }
        ]
        
        print("Testing Document Classification:")
        print("-" * 50)
        
        for i, doc in enumerate(test_documents, 1):
            print(f"\nTest {i}: {doc['name']}")
            print("-" * 30)
            
            result = classifier.classify_document(doc['text'], doc['name'])
            
            if result['success']:
                print(f"Success!")
                print(f"   Type: {result['predicted_type']}")
                print(f"   Confidence: {result['confidence']:.2f} ({result['confidence']*100:.0f}%)")
                print(f"   Method: {result['method']}")
                if 'reasoning' in result:
                    print(f"   Reasoning: {result['reasoning']}")
            else:
                print(f"Failed: {result.get('error', 'Unknown error')}")
        
        print(f"\nClassification test completed!")
        return True
        
    except ImportError as e:
        print(f"Import Error: {e}")
        print("Make sure to install required dependencies:")
        print("   pip install google-generativeai")
        return False
    except Exception as e:
        print(f"Test Error: {e}")
        return False

def test_app_integration():
    """Test the Flask app integration."""
    print("\nTesting Flask App Integration")
    print("=" * 50)
    
    try:
        # Import the app
        from app import app, gemini_classifier
        
        print(f"Flask app imported successfully")
        print(f"Gemini classifier available: {gemini_classifier is not None}")
        
        if gemini_classifier:
            status = gemini_classifier.get_status()
            print(f"Classifier status: {status['method']}")
        
        # Test routes
        with app.test_client() as client:
            # Test classify page
            response = client.get('/classify')
            if response.status_code == 200:
                print("/classify route working")
            else:
                print(f"/classify route failed: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"App integration error: {e}")
        return False

def main():
    """Run all tests."""
    print("KMRL AI Document Classification Test Suite")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Gemini Classifier
    test1_passed = test_gemini_classifier()
    
    # Test 2: App Integration
    test2_passed = test_app_integration()
    
    # Summary
    print("\nTest Summary")
    print("=" * 30)
    print(f"Gemini Classifier: {'PASSED' if test1_passed else 'FAILED'}")
    print(f"App Integration:  {'PASSED' if test2_passed else 'FAILED'}")
    
    if test1_passed and test2_passed:
        print("\nAll tests passed! The classification system is ready to use.")
        print("\nNext steps:")
        print("   1. Set your GEMINI_API_KEY in .env file for full functionality")
        print("   2. Run the Flask app: python app.py")
        print("   3. Visit http://localhost:5000/classify to test the interface")
    else:
        print("\nSome tests failed. Please check the errors above.")
    
    return test1_passed and test2_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
