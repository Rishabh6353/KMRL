from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import sys
import logging
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.config.config import config
from backend.database.models import db, Document, ProcessingLog, Department, MongoDBManager
from backend.modules.ingestion.document_ingestion import DocumentIngestionService
from backend.modules.extraction.information_extraction import InformationExtractionService
from backend.modules.summarization.text_summarization import SummarizationService
from backend.modules.classification.document_classification import DocumentClassificationService
from backend.modules.routing.document_routing import DocumentRoutingService
from backend.utils.helpers import (
    validate_file_upload, format_file_size, ProcessingStatus,
    create_processing_metadata, setup_logging
)

# Setup logging
setup_logging(log_level='INFO')
logger = logging.getLogger(__name__)

def create_app(config_name='development'):
    app = Flask(__name__, 
                template_folder='frontend/templates',
                static_folder='frontend/static')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Initialize services
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Initialize services
        app.ingestion_service = DocumentIngestionService(app.config)
        app.extraction_service = InformationExtractionService(app.config)
        app.summarization_service = SummarizationService(app.config)
        app.classification_service = DocumentClassificationService(app.config)
        app.routing_service = DocumentRoutingService(app.config)
        app.mongodb_manager = MongoDBManager(app.config.get('MONGO_URI'))
        
        # Connect to MongoDB
        app.mongodb_manager.connect()
    
    # Routes
    @app.route('/')
    def index():
        """Main dashboard"""
        try:
            # Get recent documents
            recent_docs = Document.query.order_by(Document.upload_date.desc()).limit(10).all()
            
            # Get processing statistics
            total_docs = Document.query.count()
            completed_docs = Document.query.filter_by(status='completed').count()
            pending_docs = Document.query.filter_by(status='pending').count()
            failed_docs = Document.query.filter_by(status='failed').count()
            
            stats = {
                'total': total_docs,
                'completed': completed_docs,
                'pending': pending_docs,
                'failed': failed_docs
            }
            
            return render_template('index.html', 
                                 recent_documents=recent_docs,
                                 statistics=stats)
        except Exception as e:
            logger.error(f"Error loading dashboard: {e}")
            return render_template('index.html', 
                                 recent_documents=[],
                                 statistics={'total': 0, 'completed': 0, 'pending': 0, 'failed': 0})
    
    @app.route('/upload')
    def upload_page():
        """Upload page"""
        return render_template('upload.html')
    
    @app.route('/api/upload', methods=['POST'])
    def upload_file():
        """Handle file upload"""
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            
            # Validate file
            errors = validate_file_upload(
                file, 
                app.config['ALLOWED_EXTENSIONS'],
                app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024)
            )
            
            if errors:
                return jsonify({'error': '; '.join(errors)}), 400
            
            # Upload file
            upload_result = app.ingestion_service.upload_file(file)
            
            if 'error' in upload_result:
                return jsonify({'error': upload_result['error']}), 500
            
            # Create database record
            document = Document(
                filename=upload_result['filename'],
                original_filename=upload_result['original_filename'],
                file_path=upload_result['file_path'],
                file_size=upload_result['file_size'],
                file_type=upload_result['file_type'],
                status=ProcessingStatus.PENDING
            )
            
            db.session.add(document)
            db.session.commit()
            
            # Start processing asynchronously (in a real app, use Celery)
            process_document_pipeline(document.id)
            
            return jsonify({
                'success': True,
                'document_id': document.id,
                'message': 'File uploaded successfully and processing started'
            })
            
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/document/<int:doc_id>')
    def get_document(doc_id):
        """Get document details"""
        try:
            document = Document.query.get_or_404(doc_id)
            return jsonify(document.to_dict())
        except Exception as e:
            logger.error(f"Error getting document {doc_id}: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/documents')
    def list_documents():
        """List all documents"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            status = request.args.get('status')
            
            query = Document.query
            
            if status:
                query = query.filter_by(status=status)
            
            documents = query.order_by(Document.upload_date.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            return jsonify({
                'documents': [doc.to_dict() for doc in documents.items],
                'total': documents.total,
                'pages': documents.pages,
                'current_page': page
            })
            
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/process/<int:doc_id>', methods=['POST'])
    def process_document(doc_id):
        """Process a specific document"""
        try:
            document = Document.query.get_or_404(doc_id)
            
            if document.status == ProcessingStatus.PROCESSING:
                return jsonify({'error': 'Document is already being processed'}), 400
            
            # Start processing
            result = process_document_pipeline(doc_id)
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Error processing document {doc_id}: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/statistics')
    def get_statistics():
        """Get processing statistics"""
        try:
            stats = {
                'total_documents': Document.query.count(),
                'completed': Document.query.filter_by(status='completed').count(),
                'pending': Document.query.filter_by(status='pending').count(),
                'processing': Document.query.filter_by(status='processing').count(),
                'failed': Document.query.filter_by(status='failed').count(),
                'by_category': {},
                'by_department': {},
                'recent_activity': []
            }
            
            # Get category distribution
            categories = db.session.query(Document.classification, db.func.count(Document.id)).group_by(Document.classification).all()
            stats['by_category'] = {cat[0] or 'unclassified': cat[1] for cat in categories}
            
            # Get department distribution
            departments = db.session.query(Document.department, db.func.count(Document.id)).group_by(Document.department).all()
            stats['by_department'] = {dept[0] or 'unassigned': dept[1] for dept in departments}
            
            # Get recent activity
            recent_logs = ProcessingLog.query.order_by(ProcessingLog.timestamp.desc()).limit(10).all()
            stats['recent_activity'] = [{
                'document_id': log.document_id,
                'module': log.module,
                'status': log.status,
                'message': log.message,
                'timestamp': log.timestamp.isoformat() if log.timestamp else None
            } for log in recent_logs]
            
            return jsonify(stats)
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/documents')
    def documents_page():
        """Documents management page"""
        return render_template('documents.html')
    
    @app.route('/document/<int:doc_id>')
    def document_detail(doc_id):
        """Document detail page"""
        try:
            document = Document.query.get_or_404(doc_id)
            logs = ProcessingLog.query.filter_by(document_id=doc_id).order_by(ProcessingLog.timestamp.desc()).all()
            return render_template('document_detail.html', document=document, logs=logs)
        except Exception as e:
            logger.error(f"Error loading document detail {doc_id}: {e}")
            flash(f'Error loading document: {e}', 'error')
            return redirect(url_for('documents_page'))
    
    def process_document_pipeline(document_id):
        """Complete document processing pipeline"""
        try:
            document = Document.query.get(document_id)
            if not document:
                return {'error': 'Document not found'}
            
            # Update status
            document.status = ProcessingStatus.PROCESSING
            db.session.commit()
            
            # Log start
            log_entry = ProcessingLog(
                document_id=document_id,
                module='pipeline',
                status='started',
                message='Document processing started'
            )
            db.session.add(log_entry)
            db.session.commit()
            
            # Step 1: Text Extraction
            try:
                extraction_result = app.extraction_service.process_document(document.file_path)
                
                if extraction_result['success']:
                    document.extracted_text = extraction_result['text']
                    
                    # Store extracted data in MongoDB
                    app.mongodb_manager.store_extracted_data(document_id, extraction_result)
                    
                    # Log success
                    log_entry = ProcessingLog(
                        document_id=document_id,
                        module='extraction',
                        status='completed',
                        message='Text extraction completed successfully'
                    )
                    db.session.add(log_entry)
                else:
                    raise Exception(extraction_result.get('error', 'Text extraction failed'))
                    
            except Exception as e:
                log_entry = ProcessingLog(
                    document_id=document_id,
                    module='extraction',
                    status='failed',
                    message=str(e)
                )
                db.session.add(log_entry)
                document.status = ProcessingStatus.FAILED
                db.session.commit()
                return {'error': f'Text extraction failed: {e}'}
            
            # Step 2: Classification
            try:
                classification_result = app.classification_service.classify_document(document.extracted_text)
                
                if classification_result['success']:
                    document.classification = classification_result['category']
                    document.confidence_score = classification_result['confidence']
                    
                    log_entry = ProcessingLog(
                        document_id=document_id,
                        module='classification',
                        status='completed',
                        message=f"Classified as {classification_result['category']} (confidence: {classification_result['confidence']:.2f})"
                    )
                    db.session.add(log_entry)
                else:
                    raise Exception('Classification failed')
                    
            except Exception as e:
                log_entry = ProcessingLog(
                    document_id=document_id,
                    module='classification',
                    status='failed',
                    message=str(e)
                )
                db.session.add(log_entry)
            
            # Step 3: Summarization
            try:
                summary_result = app.summarization_service.generate_summary(document.extracted_text)
                
                if summary_result['success']:
                    document.summary = summary_result['summary']
                    
                    log_entry = ProcessingLog(
                        document_id=document_id,
                        module='summarization',
                        status='completed',
                        message=f"Summary generated using {summary_result['method_used']} method"
                    )
                    db.session.add(log_entry)
                else:
                    raise Exception(summary_result.get('error', 'Summarization failed'))
                    
            except Exception as e:
                log_entry = ProcessingLog(
                    document_id=document_id,
                    module='summarization',
                    status='failed',
                    message=str(e)
                )
                db.session.add(log_entry)
            
            # Step 4: Routing
            try:
                document_info = {
                    'id': document.id,
                    'classification': document.classification,
                    'confidence': document.confidence_score,
                    'extracted_text': document.extracted_text,
                    'original_filename': document.original_filename,
                    'file_type': document.file_type,
                    'file_size': document.file_size,
                    'upload_date': document.upload_date.isoformat() if document.upload_date else None,
                    'summary': document.summary
                }
                
                routing_result = app.routing_service.route_document(document_info)
                
                if routing_result['success']:
                    document.department = routing_result['routing_result']['department_id']
                    
                    log_entry = ProcessingLog(
                        document_id=document_id,
                        module='routing',
                        status='completed',
                        message=f"Routed to {routing_result['routing_result']['department_name']}"
                    )
                    db.session.add(log_entry)
                else:
                    raise Exception(routing_result.get('error', 'Routing failed'))
                    
            except Exception as e:
                log_entry = ProcessingLog(
                    document_id=document_id,
                    module='routing',
                    status='failed',
                    message=str(e)
                )
                db.session.add(log_entry)
            
            # Update final status
            document.status = ProcessingStatus.COMPLETED
            
            # Final log
            log_entry = ProcessingLog(
                document_id=document_id,
                module='pipeline',
                status='completed',
                message='Document processing completed successfully'
            )
            db.session.add(log_entry)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Document processed successfully',
                'document': document.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error in processing pipeline for document {document_id}: {e}")
            
            # Update status to failed
            if document:
                document.status = ProcessingStatus.FAILED
                log_entry = ProcessingLog(
                    document_id=document_id,
                    module='pipeline',
                    status='failed',
                    message=str(e)
                )
                db.session.add(log_entry)
                db.session.commit()
            
            return {'error': str(e)}
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return render_template('500.html'), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)