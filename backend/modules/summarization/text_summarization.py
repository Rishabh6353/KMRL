import re
import math
from collections import Counter, defaultdict
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import spacy
from gensim.summarization import summarize as gensim_summarize
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import logging

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

class SummarizationService:
    def __init__(self, config):
        self.config = config
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
        
        # Initialize transformer model for abstractive summarization
        self.transformer_summarizer = None
        self._init_transformer_model()
    
    def _init_transformer_model(self):
        """Initialize transformer model for abstractive summarization"""
        try:
            # Use a lightweight model for better compatibility
            model_name = "facebook/bart-large-cnn"
            self.transformer_summarizer = pipeline(
                "summarization",
                model=model_name,
                tokenizer=model_name,
                device=-1  # Use CPU
            )
        except Exception as e:
            logging.warning(f"Could not initialize transformer model: {e}")
            self.transformer_summarizer = None
    
    def preprocess_text(self, text):
        """Clean and preprocess text"""
        # Remove extra whitespaces and newlines
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep sentence endings
        text = re.sub(r'[^\w\s\.!?]', '', text)
        
        return text.strip()
    
    def calculate_sentence_scores(self, sentences, word_freq):
        """Calculate scores for sentences based on word frequencies"""
        sentence_scores = {}
        
        for sentence in sentences:
            words = word_tokenize(sentence.lower())
            words = [word for word in words if word not in self.stop_words and word.isalpha()]
            
            if len(words) > 0:
                score = sum(word_freq.get(word, 0) for word in words) / len(words)
                sentence_scores[sentence] = score
        
        return sentence_scores
    
    def extractive_summarization(self, text, num_sentences=3):
        """
        Generate extractive summary by selecting top-scored sentences
        """
        try:
            # Preprocess text
            text = self.preprocess_text(text)
            
            # Tokenize into sentences
            sentences = sent_tokenize(text)
            
            if len(sentences) <= num_sentences:
                return ' '.join(sentences)
            
            # Tokenize into words and calculate frequencies
            words = word_tokenize(text.lower())
            words = [self.stemmer.stem(word) for word in words if word not in self.stop_words and word.isalpha()]
            
            word_freq = Counter(words)
            
            # Normalize frequencies
            max_freq = max(word_freq.values()) if word_freq else 1
            for word in word_freq:
                word_freq[word] = word_freq[word] / max_freq
            
            # Calculate sentence scores
            sentence_scores = self.calculate_sentence_scores(sentences, word_freq)
            
            # Select top sentences
            top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:num_sentences]
            
            # Sort by original order
            summary_sentences = []
            for sentence in sentences:
                if any(sentence == top_sent[0] for top_sent in top_sentences):
                    summary_sentences.append(sentence)
                if len(summary_sentences) == num_sentences:
                    break
            
            return ' '.join(summary_sentences)
            
        except Exception as e:
            logging.error(f"Error in extractive summarization: {str(e)}")
            return text[:500] + "..." if len(text) > 500 else text
    
    def abstractive_summarization(self, text, max_length=150, min_length=50):
        """
        Generate abstractive summary using transformer model
        """
        try:
            if not self.transformer_summarizer:
                # Fallback to extractive if transformer not available
                return self.extractive_summarization(text)
            
            # Preprocess text
            text = self.preprocess_text(text)
            
            # Limit input length for transformer (BART has a limit)
            if len(text) > 1024:
                text = text[:1024]
            
            # Generate summary
            summary = self.transformer_summarizer(
                text,
                max_length=max_length,
                min_length=min_length,
                do_sample=False
            )
            
            return summary[0]['summary_text']
            
        except Exception as e:
            logging.error(f"Error in abstractive summarization: {str(e)}")
            # Fallback to extractive summarization
            return self.extractive_summarization(text)
    
    def gensim_summarization(self, text, ratio=0.3):
        """
        Generate summary using Gensim's TextRank algorithm
        """
        try:
            # Preprocess text
            text = self.preprocess_text(text)
            
            # Gensim requires minimum text length
            if len(text.split()) < 20:
                return text
            
            summary = gensim_summarize(text, ratio=ratio)
            
            # If summary is empty, fallback to extractive
            if not summary.strip():
                return self.extractive_summarization(text)
            
            return summary
            
        except Exception as e:
            logging.error(f"Error in Gensim summarization: {str(e)}")
            return self.extractive_summarization(text)
    
    def keyword_based_summarization(self, text, num_sentences=3):
        """
        Generate summary based on keyword density and importance
        """
        try:
            text = self.preprocess_text(text)
            sentences = sent_tokenize(text)
            
            if len(sentences) <= num_sentences:
                return ' '.join(sentences)
            
            # Extract keywords using TF-IDF-like approach
            words = word_tokenize(text.lower())
            words = [word for word in words if word not in self.stop_words and word.isalpha()]
            
            # Calculate word importance
            word_freq = Counter(words)
            total_words = len(words)
            
            # Simple TF-IDF calculation
            word_importance = {}
            for word, freq in word_freq.items():
                tf = freq / total_words
                # Simple IDF approximation (could be improved with document corpus)
                idf = math.log(total_words / freq)
                word_importance[word] = tf * idf
            
            # Score sentences based on keyword importance
            sentence_scores = {}
            for sentence in sentences:
                sentence_words = word_tokenize(sentence.lower())
                sentence_words = [word for word in sentence_words if word not in self.stop_words and word.isalpha()]
                
                if sentence_words:
                    score = sum(word_importance.get(word, 0) for word in sentence_words)
                    sentence_scores[sentence] = score / len(sentence_words)
            
            # Select top sentences
            top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:num_sentences]
            
            # Maintain original order
            summary_sentences = []
            for sentence in sentences:
                if any(sentence == top_sent[0] for top_sent in top_sentences):
                    summary_sentences.append(sentence)
                if len(summary_sentences) == num_sentences:
                    break
            
            return ' '.join(summary_sentences)
            
        except Exception as e:
            logging.error(f"Error in keyword-based summarization: {str(e)}")
            return self.extractive_summarization(text)
    
    def multi_document_summarization(self, texts, method='extractive', num_sentences=5):
        """
        Summarize multiple documents
        """
        try:
            # Combine all texts
            combined_text = ' '.join(texts)
            
            # Generate summary based on method
            if method == 'abstractive':
                return self.abstractive_summarization(combined_text, max_length=200)
            elif method == 'gensim':
                return self.gensim_summarization(combined_text)
            elif method == 'keyword':
                return self.keyword_based_summarization(combined_text, num_sentences)
            else:
                return self.extractive_summarization(combined_text, num_sentences)
                
        except Exception as e:
            logging.error(f"Error in multi-document summarization: {str(e)}")
            return "Error generating summary for multiple documents."
    
    def generate_summary(self, text, method='auto', **kwargs):
        """
        Generate summary using specified method
        
        Args:
            text: Input text to summarize
            method: Summarization method ('extractive', 'abstractive', 'gensim', 'keyword', 'auto')
            **kwargs: Additional parameters for specific methods
        
        Returns:
            dict: Summary result with metadata
        """
        try:
            if not text or len(text.strip()) < 10:
                return {
                    'success': False,
                    'error': 'Text too short to summarize',
                    'summary': text,
                    'method_used': method,
                    'original_length': len(text),
                    'summary_length': len(text)
                }
            
            # Auto-select method based on text length and available models
            if method == 'auto':
                if len(text.split()) > 500 and self.transformer_summarizer:
                    method = 'abstractive'
                elif len(text.split()) > 100:
                    method = 'gensim'
                else:
                    method = 'extractive'
            
            # Generate summary based on method
            if method == 'extractive':
                summary = self.extractive_summarization(text, kwargs.get('num_sentences', 3))
            elif method == 'abstractive':
                summary = self.abstractive_summarization(
                    text, 
                    kwargs.get('max_length', 150),
                    kwargs.get('min_length', 50)
                )
            elif method == 'gensim':
                summary = self.gensim_summarization(text, kwargs.get('ratio', 0.3))
            elif method == 'keyword':
                summary = self.keyword_based_summarization(text, kwargs.get('num_sentences', 3))
            else:
                summary = self.extractive_summarization(text)
            
            return {
                'success': True,
                'summary': summary,
                'method_used': method,
                'original_length': len(text),
                'summary_length': len(summary),
                'compression_ratio': len(summary) / len(text) if text else 0
            }
            
        except Exception as e:
            logging.error(f"Error generating summary: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'summary': text[:200] + "..." if len(text) > 200 else text,
                'method_used': method,
                'original_length': len(text),
                'summary_length': 0
            }