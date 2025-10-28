"""
Email Service - Single responsibility: Manage email operations
"""
from pathlib import Path
from .smtp_client import SMTPClient
from utils.logger import get_logger

logger = get_logger(__name__)


class EmailService:
    """High-level email service"""
    
    def __init__(self, smtp_client: SMTPClient):
        """Initialize with SMTP client"""
        self.smtp_client = smtp_client
    
    def send_pdfs(self, pdf_files, recipients, subject, body):
        """
        Send PDF files to recipients
        
        Args:
            pdf_files: List of PDF file paths
            recipients: List of recipient emails
            subject: Email subject
            body: Email body
            
        Returns:
            dict: Results with sent/failed lists
        """
        results = {'sent': [], 'failed': []}
        
        # Validate files
        for pdf_file in pdf_files:
            if not Path(pdf_file).exists():
                raise FileNotFoundError(f"PDF not found: {pdf_file}")
        
        logger.info(f"Sending {len(pdf_files)} PDF(s) to {len(recipients)} recipient(s)")
        
        for recipient in recipients:
            try:
                self.smtp_client.send(
                    to_addresses=recipient,
                    subject=subject,
                    body=body,
                    attachments=pdf_files
                )
                results['sent'].append(recipient)
            except Exception as e:
                logger.error(f"Failed to send to {recipient}: {e}")
                results['failed'].append({'recipient': recipient, 'error': str(e)})
        
        return results
    
    def close(self):
        """Close email service"""
        self.smtp_client.close()

