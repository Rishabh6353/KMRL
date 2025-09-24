import json
import smtplib
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests
from collections import defaultdict

class DocumentRoutingService:
    def __init__(self, config):
        self.config = config
        self.departments = self._load_departments()
        self.routing_rules = self._load_routing_rules()
        
        # Email configuration
        self.smtp_server = config.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = config.get('SMTP_PORT', 587)
        self.email_user = config.get('EMAIL_USER')
        self.email_password = config.get('EMAIL_PASSWORD')
        
        # Webhook configuration
        self.webhook_url = config.get('WEBHOOK_URL')
        
        # Notification settings
        self.notification_methods = config.get('NOTIFICATION_METHODS', ['email'])
    
    def _load_departments(self):
        """Load department configuration"""
        # Default departments - in practice, this would come from a database
        return {
            'finance': {
                'name': 'Finance Department',
                'email': 'finance@company.com',
                'responsible_person': 'Finance Manager',
                'categories': ['invoice', 'financial_statement', 'receipt', 'expense_report']
            },
            'hr': {
                'name': 'Human Resources',
                'email': 'hr@company.com',
                'responsible_person': 'HR Manager',
                'categories': ['resume', 'employment_contract', 'employee_handbook', 'policy_document']
            },
            'legal': {
                'name': 'Legal Department',
                'email': 'legal@company.com',
                'responsible_person': 'Legal Counsel',
                'categories': ['contract', 'legal_document', 'agreement', 'compliance_document']
            },
            'operations': {
                'name': 'Operations Department',
                'email': 'operations@company.com',
                'responsible_person': 'Operations Manager',
                'categories': ['report', 'technical_manual', 'procedure_document']
            },
            'management': {
                'name': 'Management',
                'email': 'management@company.com',
                'responsible_person': 'Executive Team',
                'categories': ['executive_summary', 'strategic_plan', 'board_document']
            },
            'archive': {
                'name': 'Document Archive',
                'email': 'archive@company.com',
                'responsible_person': 'Document Controller',
                'categories': ['other', 'unknown']
            }
        }
    
    def _load_routing_rules(self):
        """Load routing rules configuration"""
        return {
            'confidence_threshold': 0.7,  # Minimum confidence for automatic routing
            'fallback_department': 'archive',
            'priority_mapping': {
                'invoice': 'high',
                'contract': 'high',
                'legal_document': 'high',
                'financial_statement': 'medium',
                'resume': 'medium',
                'report': 'low',
                'other': 'low'
            },
            'urgent_keywords': ['urgent', 'asap', 'immediate', 'priority', 'deadline'],
            'sensitive_keywords': ['confidential', 'private', 'restricted', 'classified']
        }
    
    def determine_department(self, document_info):
        """
        Determine the appropriate department for a document
        
        Args:
            document_info: Dict containing document classification and metadata
            
        Returns:
            Dict with routing decision
        """
        try:
            category = document_info.get('classification', 'other')
            confidence = document_info.get('confidence', 0.0)
            text = document_info.get('extracted_text', '')
            
            # Check confidence threshold
            if confidence < self.routing_rules['confidence_threshold']:
                return self._create_routing_result(
                    'archive',
                    'Low confidence classification',
                    confidence,
                    needs_review=True
                )
            
            # Find department by category
            target_department = None
            for dept_id, dept_info in self.departments.items():
                if category in dept_info['categories']:
                    target_department = dept_id
                    break
            
            # Fallback to archive if no department found
            if not target_department:
                target_department = self.routing_rules['fallback_department']
            
            # Check for priority indicators
            priority = self._determine_priority(text, category)
            
            # Check for sensitive content
            is_sensitive = self._check_sensitive_content(text)
            
            return self._create_routing_result(
                target_department,
                f'Classified as {category}',
                confidence,
                priority=priority,
                is_sensitive=is_sensitive
            )
            
        except Exception as e:
            logging.error(f"Error determining department: {str(e)}")
            return self._create_routing_result(
                'archive',
                f'Error in routing: {str(e)}',
                0.0,
                needs_review=True
            )
    
    def _determine_priority(self, text, category):
        """Determine document priority"""
        text_lower = text.lower()
        
        # Check for urgent keywords
        if any(keyword in text_lower for keyword in self.routing_rules['urgent_keywords']):
            return 'urgent'
        
        # Use category-based priority
        return self.routing_rules['priority_mapping'].get(category, 'low')
    
    def _check_sensitive_content(self, text):
        """Check if document contains sensitive information"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.routing_rules['sensitive_keywords'])
    
    def _create_routing_result(self, department, reason, confidence, priority='medium', is_sensitive=False, needs_review=False):
        """Create a routing result dictionary"""
        dept_info = self.departments.get(department, {})
        
        return {
            'department_id': department,
            'department_name': dept_info.get('name', department),
            'department_email': dept_info.get('email'),
            'responsible_person': dept_info.get('responsible_person'),
            'reason': reason,
            'confidence': confidence,
            'priority': priority,
            'is_sensitive': is_sensitive,
            'needs_review': needs_review,
            'routing_timestamp': datetime.now().isoformat()
        }
    
    def route_document(self, document_info, routing_result=None):
        """
        Route a document to the appropriate department
        
        Args:
            document_info: Document information including file path, text, etc.
            routing_result: Pre-determined routing result (optional)
            
        Returns:
            Dict with routing status
        """
        try:
            if not routing_result:
                routing_result = self.determine_department(document_info)
            
            # Create notification content
            notification_data = {
                'document': document_info,
                'routing': routing_result,
                'timestamp': datetime.now().isoformat()
            }
            
            # Send notifications
            notification_results = []
            
            if 'email' in self.notification_methods:
                email_result = self._send_email_notification(notification_data)
                notification_results.append(email_result)
            
            if 'webhook' in self.notification_methods and self.webhook_url:
                webhook_result = self._send_webhook_notification(notification_data)
                notification_results.append(webhook_result)
            
            # Log routing action
            self._log_routing_action(document_info, routing_result)
            
            return {
                'success': True,
                'routing_result': routing_result,
                'notifications_sent': notification_results,
                'message': f"Document routed to {routing_result['department_name']}"
            }
            
        except Exception as e:
            logging.error(f"Error routing document: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'routing_result': routing_result
            }
    
    def _send_email_notification(self, notification_data):
        """Send email notification to department"""
        try:
            if not self.email_user or not self.email_password:
                return {'method': 'email', 'success': False, 'error': 'Email credentials not configured'}
            
            document = notification_data['document']
            routing = notification_data['routing']
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = routing['department_email']
            msg['Subject'] = f"[{routing['priority'].upper()}] New Document: {document.get('original_filename', 'Unknown')}"
            
            # Create email body
            body = self._create_email_body(notification_data)
            msg.attach(MIMEText(body, 'html'))
            
            # Attach document if available (optional)
            # Note: In production, you might want to send a link instead of the actual file
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_user, routing['department_email'], text)
            server.quit()
            
            return {
                'method': 'email',
                'success': True,
                'recipient': routing['department_email']
            }
            
        except Exception as e:
            logging.error(f"Error sending email notification: {str(e)}")
            return {
                'method': 'email',
                'success': False,
                'error': str(e)
            }
    
    def _create_email_body(self, notification_data):
        """Create HTML email body"""
        document = notification_data['document']
        routing = notification_data['routing']
        
        priority_color = {
            'urgent': '#ff4444',
            'high': '#ff8800',
            'medium': '#ffaa00',
            'low': '#00aa00'
        }.get(routing['priority'], '#666666')
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 20px;">
            <h2 style="color: #333;">New Document Received</h2>
            
            <div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                <h3>Document Information</h3>
                <p><strong>Filename:</strong> {document.get('original_filename', 'Unknown')}</p>
                <p><strong>File Type:</strong> {document.get('file_type', 'Unknown')}</p>
                <p><strong>Size:</strong> {document.get('file_size', 0)} bytes</p>
                <p><strong>Upload Date:</strong> {document.get('upload_date', 'Unknown')}</p>
            </div>
            
            <div style="background-color: #e8f4fd; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                <h3>Classification Results</h3>
                <p><strong>Category:</strong> {document.get('classification', 'Unknown')}</p>
                <p><strong>Confidence:</strong> {routing['confidence']:.2f}</p>
                <p><strong>Priority:</strong> <span style="color: {priority_color}; font-weight: bold;">{routing['priority'].upper()}</span></p>
                {f"<p><strong>⚠️ SENSITIVE CONTENT DETECTED</strong></p>" if routing['is_sensitive'] else ""}
                {f"<p><strong>⚠️ REQUIRES MANUAL REVIEW</strong></p>" if routing['needs_review'] else ""}
            </div>
            
            <div style="background-color: #fff2e8; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                <h3>Routing Information</h3>
                <p><strong>Assigned Department:</strong> {routing['department_name']}</p>
                <p><strong>Responsible Person:</strong> {routing['responsible_person']}</p>
                <p><strong>Routing Reason:</strong> {routing['reason']}</p>
            </div>
            
            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px;">
                <h3>Document Summary</h3>
                <p>{document.get('summary', 'No summary available')[:500]}...</p>
            </div>
            
            <hr style="margin: 30px 0;">
            <p style="color: #666; font-size: 12px;">
                This is an automated notification from the Intelligent Document Processing System.
                <br>Timestamp: {notification_data['timestamp']}
            </p>
        </body>
        </html>
        """
        
        return html_body
    
    def _send_webhook_notification(self, notification_data):
        """Send webhook notification"""
        try:
            response = requests.post(
                self.webhook_url,
                json=notification_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            response.raise_for_status()
            
            return {
                'method': 'webhook',
                'success': True,
                'status_code': response.status_code
            }
            
        except Exception as e:
            logging.error(f"Error sending webhook notification: {str(e)}")
            return {
                'method': 'webhook',
                'success': False,
                'error': str(e)
            }
    
    def _log_routing_action(self, document_info, routing_result):
        """Log routing action for audit trail"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'document_id': document_info.get('id'),
                'filename': document_info.get('original_filename'),
                'classification': document_info.get('classification'),
                'confidence': document_info.get('confidence'),
                'routed_to': routing_result['department_id'],
                'priority': routing_result['priority'],
                'is_sensitive': routing_result['is_sensitive'],
                'needs_review': routing_result['needs_review']
            }
            
            # In production, this would be saved to a database
            logging.info(f"Document routing: {json.dumps(log_entry)}")
            
        except Exception as e:
            logging.error(f"Error logging routing action: {str(e)}")
    
    def get_routing_statistics(self, days=30):
        """Get routing statistics (placeholder - would query database in production)"""
        # This is a placeholder. In production, you would query a database
        return {
            'total_documents': 0,
            'departments': {dept_id: 0 for dept_id in self.departments.keys()},
            'priorities': {'urgent': 0, 'high': 0, 'medium': 0, 'low': 0},
            'accuracy': 0.0,
            'manual_reviews': 0
        }
    
    def update_routing_rules(self, new_rules):
        """Update routing rules (would save to database in production)"""
        try:
            self.routing_rules.update(new_rules)
            logging.info("Routing rules updated successfully")
            return {'success': True, 'message': 'Routing rules updated'}
        except Exception as e:
            logging.error(f"Error updating routing rules: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def add_department(self, department_id, department_info):
        """Add a new department"""
        try:
            self.departments[department_id] = department_info
            logging.info(f"Department {department_id} added successfully")
            return {'success': True, 'message': f'Department {department_id} added'}
        except Exception as e:
            logging.error(f"Error adding department: {str(e)}")
            return {'success': False, 'error': str(e)}