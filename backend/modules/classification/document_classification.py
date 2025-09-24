import os
import pickle
import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.pipeline import Pipeline
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import spacy
import re
import logging
from datetime import datetime

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

class DocumentClassificationService:
    def __init__(self, config):
        self.config = config
        self.model_path = config.get('CLASSIFICATION_MODEL_PATH', 'models/classification_model.pkl')
        self.stemmer = PorterStemmer()
        
        # Initialize spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logging.warning("spaCy English model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Initialize stop words
        try:
            self.stop_words = set(stopwords.words('english'))
        except:
            self.stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
        
        # Default document categories
        self.default_categories = [
            'invoice',
            'contract',
            'resume',
            'letter',
            'report',
            'legal_document',
            'financial_statement',
            'technical_manual',
            'policy_document',
            'academic_paper',
            'other'
        ]
        
        # Load trained model if exists
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self._load_model()
    
    def preprocess_text(self, text):
        """Clean and preprocess text for classification"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Remove extra whitespaces
        text = re.sub(r'\s+', ' ', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and stem
        tokens = [self.stemmer.stem(token) for token in tokens 
                 if token not in self.stop_words and len(token) > 2]
        
        return ' '.join(tokens)
    
    def extract_features(self, text):
        """Extract features from text for classification"""
        features = {}
        
        # Basic text statistics
        features['word_count'] = len(text.split())
        features['char_count'] = len(text)
        features['sentence_count'] = len(text.split('.'))
        features['avg_word_length'] = np.mean([len(word) for word in text.split()]) if text.split() else 0
        
        # Keywords presence (simplified approach)
        invoice_keywords = ['invoice', 'bill', 'payment', 'amount', 'due', 'total', 'tax']
        contract_keywords = ['agreement', 'contract', 'terms', 'conditions', 'party', 'whereas']
        resume_keywords = ['experience', 'education', 'skills', 'employment', 'work', 'university']
        legal_keywords = ['court', 'law', 'legal', 'attorney', 'plaintiff', 'defendant']
        
        features['invoice_keywords'] = sum(1 for word in invoice_keywords if word in text.lower())
        features['contract_keywords'] = sum(1 for word in contract_keywords if word in text.lower())
        features['resume_keywords'] = sum(1 for word in resume_keywords if word in text.lower())
        features['legal_keywords'] = sum(1 for word in legal_keywords if word in text.lower())
        
        # Document structure indicators
        features['has_date'] = bool(re.search(r'\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2}', text))
        features['has_email'] = bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text))
        features['has_phone'] = bool(re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text))
        features['has_currency'] = bool(re.search(r'\$[\d,]+\.?\d*', text))
        
        return features
    
    def rule_based_classification(self, text):
        """Simple rule-based classification as fallback"""
        text_lower = text.lower()
        
        # Invoice detection
        if any(word in text_lower for word in ['invoice', 'bill', 'payment', 'amount due', 'total']):
            if any(word in text_lower for word in ['$', 'usd', 'total', 'subtotal']):
                return 'invoice', 0.8
        
        # Contract detection
        if any(word in text_lower for word in ['agreement', 'contract', 'terms and conditions', 'whereas']):
            return 'contract', 0.7
        
        # Resume detection
        if any(word in text_lower for word in ['experience', 'education', 'skills', 'employment history']):
            if any(word in text_lower for word in ['university', 'degree', 'work experience']):
                return 'resume', 0.75
        
        # Legal document detection
        if any(word in text_lower for word in ['court', 'legal', 'attorney', 'law', 'plaintiff', 'defendant']):
            return 'legal_document', 0.7
        
        # Report detection
        if any(word in text_lower for word in ['executive summary', 'conclusion', 'analysis', 'findings']):
            return 'report', 0.6
        
        return 'other', 0.5
    
    def create_training_data(self):
        """Create sample training data for model training"""
        # This is a simplified example. In practice, you'd have a labeled dataset
        training_data = []
        
        # Sample invoice texts
        invoice_samples = [
            "Invoice #12345 Date: 01/15/2024 Bill To: John Doe Amount Due: $1,500.00 Payment Terms: Net 30",
            "INVOICE Company ABC Total Amount: $2,450.00 Tax: $245.00 Due Date: February 15, 2024",
            "Bill Number: INV-2024-001 Customer: XYZ Corp Subtotal: $1,200 Total: $1,320"
        ]
        
        # Sample contract texts
        contract_samples = [
            "This Agreement is entered into between Party A and Party B. Terms and Conditions: Whereas Party A agrees to provide services",
            "CONTRACT FOR SERVICES This contract outlines the terms and conditions between the contractor and client",
            "EMPLOYMENT AGREEMENT This agreement sets forth the terms of employment between employer and employee"
        ]
        
        # Sample resume texts
        resume_samples = [
            "John Smith Education: Bachelor of Science, Computer Science Work Experience: Software Developer at ABC Corp Skills: Python, Java",
            "Jane Doe University of California, Berkeley Employment History: Marketing Manager, 5 years experience",
            "Resume - Software Engineer Education: Master's in Computer Science Skills: Machine Learning, Data Analysis"
        ]
        
        # Add samples to training data
        for text in invoice_samples:
            training_data.append((text, 'invoice'))
        for text in contract_samples:
            training_data.append((text, 'contract'))
        for text in resume_samples:
            training_data.append((text, 'resume'))
        
        return training_data
    
    def train_model(self, training_data=None, algorithm='naive_bayes'):
        """Train the classification model"""
        try:
            if training_data is None:
                training_data = self.create_training_data()
            
            # Prepare data
            texts = [self.preprocess_text(text) for text, label in training_data]
            labels = [label for text, label in training_data]
            
            # Create vectorizer
            self.vectorizer = TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 2),
                stop_words='english'
            )
            
            # Vectorize texts
            X = self.vectorizer.fit_transform(texts)
            y = labels
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Select algorithm
            if algorithm == 'naive_bayes':
                classifier = MultinomialNB()
            elif algorithm == 'logistic_regression':
                classifier = LogisticRegression(random_state=42)
            elif algorithm == 'svm':
                classifier = SVC(probability=True, random_state=42)
            elif algorithm == 'random_forest':
                classifier = RandomForestClassifier(n_estimators=100, random_state=42)
            else:
                classifier = MultinomialNB()
            
            # Train model
            classifier.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = classifier.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            print(f"Model trained with accuracy: {accuracy:.2f}")
            print("\nClassification Report:")
            print(classification_report(y_test, y_pred))
            
            # Save model
            self.model = classifier
            self._save_model()
            
            return {
                'success': True,
                'accuracy': accuracy,
                'algorithm': algorithm,
                'training_samples': len(training_data)
            }
            
        except Exception as e:
            logging.error(f"Error training model: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def classify_document(self, text):
        """Classify a document"""
        try:
            if not text or len(text.strip()) < 10:
                return {
                    'success': False,
                    'error': 'Text too short for classification',
                    'category': 'other',
                    'confidence': 0.0
                }
            
            # Try ML model first if available
            if self.model and self.vectorizer:
                processed_text = self.preprocess_text(text)
                text_vector = self.vectorizer.transform([processed_text])
                
                # Get prediction and probabilities
                prediction = self.model.predict(text_vector)[0]
                probabilities = self.model.predict_proba(text_vector)[0]
                confidence = max(probabilities)
                
                # Get all class probabilities
                classes = self.model.classes_
                prob_dict = dict(zip(classes, probabilities))
                
                return {
                    'success': True,
                    'category': prediction,
                    'confidence': float(confidence),
                    'all_probabilities': {k: float(v) for k, v in prob_dict.items()},
                    'method': 'machine_learning'
                }
            
            # Fallback to rule-based classification
            category, confidence = self.rule_based_classification(text)
            
            return {
                'success': True,
                'category': category,
                'confidence': confidence,
                'method': 'rule_based'
            }
            
        except Exception as e:
            logging.error(f"Error classifying document: {str(e)}")
            
            # Final fallback
            category, confidence = self.rule_based_classification(text)
            return {
                'success': False,
                'error': str(e),
                'category': category,
                'confidence': confidence,
                'method': 'rule_based_fallback'
            }
    
    def batch_classify(self, texts):
        """Classify multiple documents"""
        results = []
        for i, text in enumerate(texts):
            result = self.classify_document(text)
            result['document_index'] = i
            results.append(result)
        return results
    
    def _save_model(self):
        """Save the trained model"""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            
            model_data = {
                'model': self.model,
                'vectorizer': self.vectorizer,
                'timestamp': datetime.now().isoformat(),
                'categories': self.default_categories
            }
            
            with open(self.model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            logging.info(f"Model saved to {self.model_path}")
            
        except Exception as e:
            logging.error(f"Error saving model: {str(e)}")
    
    def _load_model(self):
        """Load a trained model"""
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                
                self.model = model_data['model']
                self.vectorizer = model_data['vectorizer']
                
                logging.info(f"Model loaded from {self.model_path}")
                return True
            
        except Exception as e:
            logging.error(f"Error loading model: {str(e)}")
        
        return False
    
    def get_model_info(self):
        """Get information about the current model"""
        if self.model and self.vectorizer:
            return {
                'model_available': True,
                'model_type': type(self.model).__name__,
                'vocabulary_size': len(self.vectorizer.vocabulary_) if hasattr(self.vectorizer, 'vocabulary_') else 0,
                'categories': list(self.model.classes_) if hasattr(self.model, 'classes_') else self.default_categories
            }
        else:
            return {
                'model_available': False,
                'categories': self.default_categories
            }