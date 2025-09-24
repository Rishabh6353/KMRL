import os
import cv2
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import docx
import spacy
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk
from nltk.corpus import stopwords
import re
import json
from datetime import datetime
import logging

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('maxent_ne_chunker', quiet=True)
    nltk.download('words', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

class InformationExtractionService:
    def __init__(self, config):
        self.config = config
        self.tesseract_path = config.get('TESSERACT_PATH', '/usr/bin/tesseract')
        
        # Set Tesseract path if provided
        if self.tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
        
        # Initialize spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logging.warning("spaCy English model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Initialize NLTK stop words
        try:
            self.stop_words = set(stopwords.words('english'))
        except:
            self.stop_words = set()
    
    def extract_text_from_file(self, file_path):
        """
        Extract text from various file formats
        """
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.pdf':
                return self._extract_text_from_pdf(file_path)
            elif file_extension in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
                return self._extract_text_from_image(file_path)
            elif file_extension == '.docx':
                return self._extract_text_from_docx(file_path)
            elif file_extension == '.txt':
                return self._extract_text_from_txt(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
                
        except Exception as e:
            logging.error(f"Error extracting text from {file_path}: {str(e)}")
            raise
    
    def _extract_text_from_pdf(self, file_path):
        """Extract text from PDF files"""
        text = ""
        try:
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text()
            doc.close()
            return text.strip()
        except Exception as e:
            logging.error(f"Error extracting text from PDF: {str(e)}")
            raise
    
    def _extract_text_from_image(self, file_path):
        """Extract text from image files using OCR"""
        try:
            # Load and preprocess image
            image = cv2.imread(file_path)
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply noise reduction
            denoised = cv2.medianBlur(gray, 3)
            
            # Apply thresholding to get better OCR results
            _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(thresh, config='--psm 6')
            
            return text.strip()
        except Exception as e:
            logging.error(f"Error extracting text from image: {str(e)}")
            raise
    
    def _extract_text_from_docx(self, file_path):
        """Extract text from DOCX files"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logging.error(f"Error extracting text from DOCX: {str(e)}")
            raise
    
    def _extract_text_from_txt(self, file_path):
        """Extract text from TXT files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            logging.error(f"Error extracting text from TXT: {str(e)}")
            raise
    
    def extract_entities(self, text):
        """
        Extract named entities from text using spaCy and NLTK
        """
        entities = {
            'persons': [],
            'organizations': [],
            'locations': [],
            'dates': [],
            'money': [],
            'emails': [],
            'phone_numbers': [],
            'other': []
        }
        
        try:
            # Use spaCy for entity extraction if available
            if self.nlp:
                doc = self.nlp(text)
                for ent in doc.ents:
                    entity_info = {
                        'text': ent.text,
                        'label': ent.label_,
                        'start': ent.start_char,
                        'end': ent.end_char
                    }
                    
                    if ent.label_ in ['PERSON']:
                        entities['persons'].append(entity_info)
                    elif ent.label_ in ['ORG']:
                        entities['organizations'].append(entity_info)
                    elif ent.label_ in ['GPE', 'LOC']:
                        entities['locations'].append(entity_info)
                    elif ent.label_ in ['DATE', 'TIME']:
                        entities['dates'].append(entity_info)
                    elif ent.label_ in ['MONEY']:
                        entities['money'].append(entity_info)
                    else:
                        entities['other'].append(entity_info)
            
            # Use NLTK as fallback or additional extraction
            tokens = word_tokenize(text)
            pos_tags = pos_tag(tokens)
            ne_tree = ne_chunk(pos_tags)
            
            current_chunk = []
            current_label = None
            
            for chunk in ne_tree:
                if hasattr(chunk, 'label'):
                    current_chunk = [token for token, pos in chunk.leaves()]
                    current_label = chunk.label()
                    entity_text = ' '.join(current_chunk)
                    
                    entity_info = {
                        'text': entity_text,
                        'label': current_label,
                        'source': 'nltk'
                    }
                    
                    if current_label == 'PERSON':
                        entities['persons'].append(entity_info)
                    elif current_label == 'ORGANIZATION':
                        entities['organizations'].append(entity_info)
                    elif current_label in ['GPE', 'GSP']:
                        entities['locations'].append(entity_info)
                    else:
                        entities['other'].append(entity_info)
            
            # Extract emails using regex
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, text)
            entities['emails'] = [{'text': email, 'source': 'regex'} for email in emails]
            
            # Extract phone numbers using regex
            phone_pattern = r'(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'
            phone_numbers = re.findall(phone_pattern, text)
            entities['phone_numbers'] = [{'text': phone, 'source': 'regex'} for phone in phone_numbers]
            
        except Exception as e:
            logging.error(f"Error extracting entities: {str(e)}")
        
        return entities
    
    def extract_key_value_pairs(self, text):
        """
        Extract key-value pairs from text using pattern matching
        """
        key_value_pairs = {}
        
        try:
            # Common patterns for key-value extraction
            patterns = [
                r'(\w+(?:\s+\w+)*)\s*:\s*([^\n]+)',  # Key: Value
                r'(\w+(?:\s+\w+)*)\s*=\s*([^\n]+)',  # Key = Value
                r'(\w+(?:\s+\w+)*)\s*-\s*([^\n]+)',  # Key - Value
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for key, value in matches:
                    key = key.strip().lower()
                    value = value.strip()
                    if len(key) > 1 and len(value) > 1:  # Filter out single characters
                        key_value_pairs[key] = value
            
        except Exception as e:
            logging.error(f"Error extracting key-value pairs: {str(e)}")
        
        return key_value_pairs
    
    def extract_tables(self, text):
        """
        Extract table-like structures from text
        """
        tables = []
        
        try:
            lines = text.split('\n')
            current_table = []
            
            for line in lines:
                # Check if line looks like a table row (contains tabs or multiple spaces)
                if '\t' in line or re.search(r'\s{2,}', line):
                    # Split by tabs or multiple spaces
                    if '\t' in line:
                        row = line.split('\t')
                    else:
                        row = re.split(r'\s{2,}', line)
                    
                    row = [cell.strip() for cell in row if cell.strip()]
                    if len(row) > 1:
                        current_table.append(row)
                else:
                    if current_table:
                        tables.append(current_table)
                        current_table = []
            
            if current_table:
                tables.append(current_table)
                
        except Exception as e:
            logging.error(f"Error extracting tables: {str(e)}")
        
        return tables
    
    def extract_metadata(self, file_path, text):
        """
        Extract metadata from the document
        """
        metadata = {
            'file_path': file_path,
            'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            'extraction_date': datetime.now().isoformat(),
            'text_length': len(text),
            'word_count': len(text.split()),
            'sentence_count': len(sent_tokenize(text)),
            'language': 'en'  # Default to English, could be improved with language detection
        }
        
        try:
            # Extract additional file metadata
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                metadata['creation_date'] = datetime.fromtimestamp(stat.st_ctime).isoformat()
                metadata['modification_date'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
        
        except Exception as e:
            logging.error(f"Error extracting metadata: {str(e)}")
        
        return metadata
    
    def process_document(self, file_path):
        """
        Complete document processing pipeline
        """
        try:
            # Extract text
            text = self.extract_text_from_file(file_path)
            
            # Extract entities
            entities = self.extract_entities(text)
            
            # Extract key-value pairs
            key_value_pairs = self.extract_key_value_pairs(text)
            
            # Extract tables
            tables = self.extract_tables(text)
            
            # Extract metadata
            metadata = self.extract_metadata(file_path, text)
            
            return {
                'success': True,
                'text': text,
                'entities': entities,
                'key_value_pairs': key_value_pairs,
                'tables': tables,
                'metadata': metadata
            }
            
        except Exception as e:
            logging.error(f"Error processing document {file_path}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'entities': {},
                'key_value_pairs': {},
                'tables': [],
                'metadata': {}
            }