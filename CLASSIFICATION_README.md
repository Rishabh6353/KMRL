# KMRL AI Document Classification System

## Overview

This document describes the new AI-powered document classification feature added to the KMRL AI Summarizer system. The feature uses Google's Gemini API to automatically classify documents into predefined categories relevant to KMRL's operations.

## Features

### 🎯 Document Classification Categories
- **Invoice**: Bills, payment requests, financial invoices
- **Policy**: Company policies, procedures, guidelines, compliance documents  
- **Report**: Analysis reports, status reports, investigation reports, performance reports
- **Purchase Order**: Purchase requests, procurement documents, vendor orders
- **Other**: Documents that don't fit the above categories

### 🚀 Key Capabilities
- **AI-Powered Classification**: Uses Google Gemini API for intelligent document analysis
- **Demo Mode**: Works without API key using mock classification
- **Multiple File Formats**: Supports PDF, DOCX, DOC, and image files (PNG, JPG, JPEG, TIFF, GIF)
- **Confidence Scoring**: Provides confidence levels for classification results
- **Real-time Processing**: Instant classification results with detailed reasoning
- **Department Routing**: Automatically suggests appropriate departments based on document type

## Installation & Setup

### 1. Install Dependencies

```bash
# Install the new Gemini API dependency
pip install google-generativeai

# Or install all dependencies from requirements.txt
pip install -r requirements.txt
```

### 2. Configure API Key (REQUIRED for Real AI Classification)

**⚠️ IMPORTANT**: For actual Gemini AI-powered classification, you MUST provide a valid API key.

1. Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a `.env` file in the project root:
   ```bash
   GEMINI_API_KEY=your-gemini-api-key-here
   ```
3. Or set it as an environment variable:
   ```bash
   export GEMINI_API_KEY=your-gemini-api-key-here
   ```

**Demo Mode**: Without an API key, the system runs in demo mode using simple keyword-based classification. This is NOT real Gemini AI classification - just for testing the UI and workflow.

### 3. Run the Application

```bash
python app.py
```

Visit `http://localhost:5000/classify` to access the classification interface.

## Usage

### Web Interface

1. **Navigate to Classification Page**
   - Click "Classify" in the navigation menu
   - Or visit `/classify` directly

2. **Upload Document**
   - Click "Choose File" and select your document
   - Supported formats: PDF, DOCX, DOC, PNG, JPG, JPEG, TIFF, GIF
   - Maximum file size: 100MB

3. **Get Results**
   - Click "Classify Document"
   - View classification results including:
     - Predicted document type
     - Confidence score
     - Recommended department
     - AI reasoning (when using Gemini API)

### API Endpoint

You can also classify documents programmatically:

```bash
curl -X POST -F "file=@your-document.pdf" http://localhost:5000/classify_document
```

**Response Format:**
```json
{
    "success": true,
    "message": "Document classified successfully",
    "document_name": "example.pdf",
    "predicted_type": "Invoice",
    "confidence": 0.92,
    "reasoning": "This document contains invoice-specific keywords like 'amount due', 'payment terms', and financial amounts.",
    "method": "gemini_api",
    "api_available": true
}
```

## Technical Implementation

### Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Frontend  │    │  Flask Backend   │    │  Gemini API     │
│                 │    │                  │    │                 │
│ - classify.html │───▶│ - /classify      │───▶│ - Text Analysis │
│ - Upload Form   │    │ - /classify_     │    │ - Classification │
│ - Results UI    │    │   document       │    │ - Confidence    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Key Components

1. **GeminiDocumentClassifier** (`backend/modules/classification/gemini_classification.py`)
   - Handles API communication with Google Gemini
   - Provides fallback mock classification
   - Manages confidence scoring and reasoning

2. **Flask Routes** (`app.py`)
   - `/classify` - Renders classification interface
   - `/classify_document` - Processes document uploads and returns JSON results

3. **Frontend Interface** (`frontend/templates/classify.html`)
   - Modern, responsive UI
   - Real-time classification results
   - Department routing suggestions

### Classification Process

1. **Document Upload**: File is uploaded and temporarily stored
2. **Text Extraction**: Uses existing OCR/PyMuPDF functionality
3. **AI Analysis**: Text is sent to Gemini API for classification
4. **Result Processing**: Classification results are formatted and returned
5. **Cleanup**: Temporary files are removed

## Configuration

### Environment Variables

```bash
# Required for full functionality
GEMINI_API_KEY=your-gemini-api-key-here

# Optional: Other configurations
SECRET_KEY=your-secret-key
DEBUG=True
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=104857600
```

### Customization

You can modify the classification categories in `backend/modules/classification/gemini_classification.py`:

```python
self.document_categories = [
    "Invoice",
    "Policy", 
    "Report",
    "Purchase Order",
    "Other"
]
```

## Testing

Run the test suite to verify the installation:

```bash
python test_classification.py
```

The test script will:
- Verify Gemini classifier initialization
- Test classification with sample documents
- Check Flask app integration
- Validate API endpoints

## Demo Mode

When no API key is provided, the system operates in demo mode:

- **Mock Classifications**: Provides realistic sample results
- **Keyword-based Analysis**: Uses simple keyword matching
- **Confidence Scoring**: Simulates confidence levels
- **Full UI Functionality**: All features work except real AI analysis

This allows you to test the complete workflow without requiring an API key.

## Integration with Existing System

The classification feature seamlessly integrates with the existing KMRL AI Summarizer:

- **Preserves Existing Functionality**: All original features remain intact
- **Enhanced Document Processing**: Classification is integrated into the upload workflow
- **Database Integration**: Classification results can be stored in the existing document database
- **Consistent UI/UX**: Follows the same design patterns as existing pages

## Troubleshooting

### Common Issues

1. **"Gemini API not available"**
   - Install the dependency: `pip install google-generativeai`
   - Check your API key configuration

2. **"File type not allowed"**
   - Ensure your file format is supported
   - Check file extension is correct

3. **"Text extraction failed"**
   - Verify the document contains extractable text
   - For images, ensure OCR dependencies are installed

### Debug Mode

Enable debug logging by setting `DEBUG=True` in your environment or `.env` file.

## Future Enhancements

Potential improvements for the classification system:

1. **Batch Processing**: Classify multiple documents at once
2. **Custom Categories**: Allow users to define custom document types
3. **Learning Mode**: Improve classification based on user feedback
4. **Integration**: Direct integration with KMRL's document management system
5. **Analytics**: Track classification accuracy and usage patterns

## Support

For issues or questions about the classification system:

1. Check the troubleshooting section above
2. Review the test script output for diagnostic information
3. Ensure all dependencies are properly installed
4. Verify your API key configuration

## License

This classification feature is part of the KMRL AI Summarizer system and follows the same licensing terms.
