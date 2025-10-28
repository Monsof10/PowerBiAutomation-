"""
Email Service Facade - Simple interface for email operations
"""
from email.smtp_client import SMTPClient
from email.email_service import EmailService
import config


def create_email_service():
    """Create and return email service"""
    smtp = SMTPClient(
        config.EMAIL_ADDRESS,
        config.EMAIL_PASSWORD,
        config.SMTP_SERVER,
        config.SMTP_PORT
    )
    return EmailService(smtp)


def send_pdfs(pdf_files, recipients, subject=None, body=None):
    """
    Send PDFs to recipients
    
    Args:
        pdf_files: List of PDF paths
        recipients: List of recipient emails
        subject: Email subject (optional)
        body: Email body (optional)
        
    Returns:
        dict: Results with sent/failed lists
    """
    if subject is None:
        subject = config.DEFAULT_SUBJECT
    if body is None:
        body = config.DEFAULT_BODY
    
    service = create_email_service()
    
    try:
        results = service.send_pdfs(pdf_files, recipients, subject, body)
        return results
    finally:
        service.close()

