from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pymongo
from pymongo import MongoClient
import os

db = SQLAlchemy()

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    file_type = db.Column(db.String(50))
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='uploaded')
    
    # Processing results
    extracted_text = db.Column(db.Text)
    summary = db.Column(db.Text)
    classification = db.Column(db.String(100))
    confidence_score = db.Column(db.Float)
    department = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'status': self.status,
            'extracted_text': self.extracted_text,
            'summary': self.summary,
            'classification': self.classification,
            'confidence_score': self.confidence_score,
            'department': self.department
        }

class ProcessingLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    module = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text)
    processing_time = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    document = db.relationship('Document', backref=db.backref('logs', lazy=True))

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(255))
    description = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)

class MongoDBManager:
    def __init__(self, uri=None):
        self.uri = uri or os.environ.get('MONGO_URI', 'mongodb://localhost:27017/document_processing')
        self.client = None
        self.db = None
        
    def connect(self):
        try:
            self.client = MongoClient(self.uri)
            self.db = self.client.get_default_database()
            return True
        except Exception as e:
            print(f"MongoDB connection error: {e}")
            return False
    
    def store_extracted_data(self, document_id, extracted_data):
        if not self.db:
            self.connect()
        
        try:
            collection = self.db.extracted_data
            document = {
                'document_id': document_id,
                'extracted_data': extracted_data,
                'timestamp': datetime.utcnow()
            }
            result = collection.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error storing extracted data: {e}")
            return None
    
    def get_extracted_data(self, document_id):
        if not self.db:
            self.connect()
        
        try:
            collection = self.db.extracted_data
            return collection.find_one({'document_id': document_id})
        except Exception as e:
            print(f"Error retrieving extracted data: {e}")
            return None
    
    def store_processing_metadata(self, document_id, metadata):
        if not self.db:
            self.connect()
        
        try:
            collection = self.db.processing_metadata
            document = {
                'document_id': document_id,
                'metadata': metadata,
                'timestamp': datetime.utcnow()
            }
            result = collection.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error storing processing metadata: {e}")
            return None