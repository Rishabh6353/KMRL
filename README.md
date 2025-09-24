# Intelligent Document Processing System

A comprehensive web-based document processing system that automatically ingests, extracts, summarizes, classifies, and routes documents using advanced AI and machine learning techniques.

## Features

### Core Functionality
- **Document Ingestion**: Upload and store documents (PDF, images, Word, Excel, text files)
- **Text Extraction**: OCR and text extraction from various document formats
- **Information Extraction**: Named entity recognition, key-value pairs, table extraction
- **Document Classification**: ML-based and rule-based document type classification
- **Text Summarization**: Multiple summarization techniques (extractive, abstractive)
- **Document Routing**: Automatic routing to departments based on content and rules
- **Cloud Storage**: Support for AWS S3, Google Cloud Storage, Azure Blob Storage

### Web Interface
- **Dashboard**: Overview of document processing status and statistics
- **Upload Interface**: Drag-and-drop file upload with progress tracking
- **Document Management**: Browse, search, filter, and manage processed documents
- **Document Details**: Detailed view with extracted content, entities, and processing logs
- **Bulk Operations**: Process, delete, and export multiple documents
- **Real-time Updates**: Auto-refresh for processing status

### Technical Features
- **RESTful API**: Complete API for programmatic access
- **Database Support**: SQLite and MongoDB for flexible data storage
- **Scalable Architecture**: Modular design for easy extension
- **Error Handling**: Comprehensive error tracking and logging
- **Security**: File validation, type checking, and secure storage

## Tech Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite (default), MongoDB (for extracted data)
- **Cloud Storage**: AWS S3, Google Cloud Storage, Azure Blob Storage
- **OCR**: Tesseract, OpenCV, PIL
- **NLP/ML**: spaCy, NLTK, Gensim, Transformers, scikit-learn, TensorFlow, PyTorch

### Frontend
- **Framework**: Bootstrap 5
- **Icons**: Font Awesome
- **JavaScript**: Vanilla JS with modern ES6+ features
- **UI Components**: Cards, modals, progress bars, drag-and-drop

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Tesseract OCR (for text extraction)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd intelligent-document-processing
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Tesseract OCR**
   - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
   - **macOS**: `brew install tesseract`
   - **Windows**: Download from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)

5. **Download spaCy models**
   ```bash
   python -m spacy download en_core_web_sm
   python -m spacy download en_core_web_md
   ```

6. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

7. **Initialize database**
   ```bash
   python -c "
   from app import app, db
   with app.app_context():
       db.create_all()
   "
   ```

8. **Run the application**
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5000`

## Configuration

### Environment Variables (.env)

```env
# Database Configuration
DATABASE_URL=sqlite:///documents.db
MONGODB_URI=mongodb://localhost:27017/document_processing

# File Upload Configuration
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=104857600  # 100MB
ALLOWED_EXTENSIONS=pdf,png,jpg,jpeg,tiff,gif,doc,docx,txt,csv,xls,xlsx

# Cloud Storage Configuration (Optional)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_S3_BUCKET=your_s3_bucket
AWS_REGION=us-east-1

GCP_CREDENTIALS_FILE=path/to/gcp-credentials.json
GCP_BUCKET_NAME=your_gcp_bucket

AZURE_STORAGE_CONNECTION_STRING=your_azure_connection_string
AZURE_CONTAINER_NAME=your_azure_container

# External API Keys (Optional)
OPENAI_API_KEY=your_openai_api_key
HUGGINGFACE_API_TOKEN=your_huggingface_token

# Email Configuration (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Application Settings
SECRET_KEY=your_secret_key_here
DEBUG=False
```

## Usage

### Web Interface

1. **Dashboard**: Visit the home page to see processing statistics and recent activity
2. **Upload Documents**: Use the upload page to add new documents
3. **Browse Documents**: Use the documents page to view and manage uploaded files
4. **Process Documents**: Documents can be processed individually or in bulk
5. **View Details**: Click on any document to see detailed extraction results

### API Endpoints

#### Document Operations
- `POST /api/upload` - Upload a document
- `GET /api/documents` - List documents with filtering and pagination
- `GET /api/document/<id>` - Get document details
- `POST /api/process/<id>` - Process a document
- `DELETE /api/document/<id>` - Delete a document
- `GET /api/download/<id>` - Download original document
- `GET /api/preview/<id>` - Preview document
- `GET /api/export/<id>` - Export processed data

#### Processing Operations
- `POST /api/extract/<id>` - Extract text and entities
- `POST /api/classify/<id>` - Classify document type
- `POST /api/summarize/<id>` - Generate summary
- `POST /api/route/<id>` - Route document to department

### Document Processing Pipeline

1. **Upload**: Document is uploaded and stored
2. **Extraction**: Text, entities, and key-value pairs are extracted
3. **Classification**: Document type is determined using ML models
4. **Summarization**: Key information is summarized
5. **Routing**: Document is routed to appropriate department

## Project Structure

```
intelligent-document-processing/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── .env                           # Environment configuration
├── backend/
│   ├── config/
│   │   └── config.py              # Application configuration
│   ├── database/
│   │   └── models.py              # Database models
│   ├── modules/
│   │   ├── ingestion/
│   │   │   └── document_ingestion.py
│   │   ├── extraction/
│   │   │   └── information_extraction.py
│   │   ├── classification/
│   │   │   └── document_classification.py
│   │   ├── summarization/
│   │   │   └── text_summarization.py
│   │   └── routing/
│   │       └── document_routing.py
│   └── utils/
│       └── helpers.py             # Utility functions
├── frontend/
│   ├── templates/                 # Jinja2 templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── upload.html
│   │   ├── documents.html
│   │   └── document_detail.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           ├── main.js
│           ├── upload.js
│           ├── documents.js
│           └── document-detail.js
├── models/                        # ML model storage
├── uploads/                       # Document storage
└── README.md
```

## Features in Detail

### Document Ingestion
- Support for multiple file formats (PDF, images, Word, Excel, text)
- File validation and size limits
- Local and cloud storage options
- Metadata extraction and storage

### Information Extraction
- OCR for scanned documents and images
- Named Entity Recognition (NER) for people, organizations, locations
- Key-value pair extraction for forms and structured documents
- Table extraction and processing
- Confidence scoring for extracted information

### Document Classification
- Machine learning models for automatic classification
- Rule-based classification for specific document types
- Support for custom classification models
- Confidence scoring and manual override options

### Text Summarization
- Extractive summarization using sentence ranking
- Abstractive summarization with transformer models
- Keyword extraction and topic modeling
- Customizable summary length and style

### Document Routing
- Department mapping based on document type and content
- Email notifications for new documents
- Webhook integration for external systems
- Custom routing rules and workflows

## Development

### Adding New Features

1. **Backend Modules**: Add new processing modules in `backend/modules/`
2. **API Endpoints**: Extend `app.py` with new routes
3. **Database Models**: Update `backend/database/models.py`
4. **Frontend Pages**: Add templates in `frontend/templates/`
5. **JavaScript**: Add functionality in `frontend/static/js/`

### Testing

Run the test suite:
```bash
python -m pytest tests/
```

### Deployment

1. **Production Configuration**: Update `.env` for production settings
2. **Web Server**: Use gunicorn or similar WSGI server
3. **Database**: Use PostgreSQL or MySQL for production
4. **Storage**: Configure cloud storage for scalability
5. **Monitoring**: Add logging and monitoring solutions

## Troubleshooting

### Common Issues

1. **Tesseract not found**: Ensure Tesseract is installed and in PATH
2. **spaCy models missing**: Download required language models
3. **Database errors**: Check database connection and permissions
4. **File upload errors**: Verify upload directory permissions
5. **OCR quality issues**: Ensure good image quality and resolution

### Performance Optimization

1. **Use cloud storage** for large files
2. **Enable caching** for processed results
3. **Use background processing** for large documents
4. **Optimize database queries** with indexes
5. **Use CDN** for static assets

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting section

## Acknowledgments

- Tesseract OCR for text extraction
- spaCy for natural language processing
- Bootstrap for UI components
- Flask for web framework
- All open-source contributors# IntelligentDocumentProcessing
