"""
Email Sender Module
Handles sending emails with PDF attachments
"""
import logging
from pathlib import Path
from typing import List, Dict
import yagmail
import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EmailSender:
    """Handles sending emails with attachments using yagmail"""
    
    def __init__(self, email_address=None, email_password=None, smtp_server=None, smtp_port=None):
        """
        Initialize Email Sender
        
        Args:
            email_address: Sender email address
            email_password: Sender email password (app password for Gmail)
            smtp_server: SMTP server address
            smtp_port: SMTP server port
        """
        self.email_address = email_address or config.EMAIL_ADDRESS
        self.email_password = email_password or config.EMAIL_PASSWORD
        self.smtp_server = smtp_server or config.SMTP_SERVER
        self.smtp_port = smtp_port or config.SMTP_PORT
        
        if not self.email_address or not self.email_password:
            raise ValueError("Email credentials not provided")
        
        self.yag = None
        self._initialize_yagmail()
    
    def _initialize_yagmail(self):
        """Initialize yagmail client"""
        try:
            logger.info("Initializing email client...")
            self.yag = yagmail.SMTP(
                user=self.email_address,
                password=self.email_password,
                host=self.smtp_server,
                port=self.smtp_port
            )
            logger.info("Email client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize email client: {e}")
            raise Exception(f"Email initialization failed: {e}")
    
    def send_email(self, to_addresses, subject, body, attachments=None):
        """
        Send an email with optional attachments
        
        Args:
            to_addresses: Single email address (string) or list of addresses
            subject: Email subject
            body: Email body text
            attachments: Single file path or list of file paths
            
        Returns:
            Boolean indicating success
        """
        # Ensure to_addresses is a list
        if isinstance(to_addresses, str):
            to_addresses = [to_addresses]
        
        # Ensure attachments is a list or None
        if attachments and isinstance(attachments, (str, Path)):
            attachments = [attachments]
        
        # Convert Path objects to strings
        if attachments:
            attachments = [str(att) for att in attachments]
        
        logger.info(f"Sending email to: {', '.join(to_addresses)}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Attachments: {len(attachments) if attachments else 0}")
        
        try:
            self.yag.send(
                to=to_addresses,
                subject=subject,
                contents=body,
                attachments=attachments
            )
            logger.info("Email sent successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise Exception(f"Email sending failed: {e}")
    
    def send_multiple_emails(self, recipients_config):
        """
        Send multiple emails with different configurations
        
        Args:
            recipients_config: List of dictionaries with email configurations
                Each dict should have: 'to', 'subject', 'body', 'attachments'
        
        Returns:
            Dictionary with success/failure counts and details
        """
        results = {
            'sent': 0,
            'failed': 0,
            'details': []
        }
        
        for idx, config in enumerate(recipients_config, 1):
            try:
                logger.info(f"Sending email {idx}/{len(recipients_config)}...")
                
                self.send_email(
                    to_addresses=config['to'],
                    subject=config['subject'],
                    body=config['body'],
                    attachments=config.get('attachments')
                )
                
                results['sent'] += 1
                results['details'].append({
                    'recipient': config['to'],
                    'status': 'success',
                    'message': 'Email sent successfully'
                })
                
            except Exception as e:
                results['failed'] += 1
                results['details'].append({
                    'recipient': config['to'],
                    'status': 'failed',
                    'message': str(e)
                })
                logger.error(f"Failed to send email to {config['to']}: {e}")
        
        logger.info(f"Email sending complete: {results['sent']} sent, {results['failed']} failed")
        return results
    
    def send_pdf_to_recipients(self, pdf_files, recipients, subject, body):
        """
        Send PDF files to multiple recipients
        
        Args:
            pdf_files: List of PDF file paths to attach
            recipients: List of recipient email addresses
            subject: Email subject
            body: Email body
            
        Returns:
            Dictionary with results
        """
        logger.info(f"Sending {len(pdf_files)} PDF(s) to {len(recipients)} recipient(s)")
        
        # Ensure inputs are lists
        if isinstance(pdf_files, (str, Path)):
            pdf_files = [pdf_files]
        if isinstance(recipients, str):
            recipients = [recipients]
        
        # Validate files exist
        for pdf_file in pdf_files:
            if not Path(pdf_file).exists():
                raise FileNotFoundError(f"PDF file not found: {pdf_file}")
        
        results = {
            'sent': [],
            'failed': []
        }
        
        for recipient in recipients:
            try:
                self.send_email(
                    to_addresses=recipient,
                    subject=subject,
                    body=body,
                    attachments=pdf_files
                )
                results['sent'].append(recipient)
                
            except Exception as e:
                results['failed'].append({
                    'recipient': recipient,
                    'error': str(e)
                })
        
        return results
    
    def close(self):
        """Close the email connection"""
        if self.yag:
            try:
                self.yag.close()
                logger.info("Email client closed")
            except:
                pass


def send_email_with_attachments(to_addresses, subject, body, attachments=None,
                                 email_address=None, email_password=None):
    """
    Convenience function to send an email with attachments
    
    Args:
        to_addresses: Recipient email address(es)
        subject: Email subject
        body: Email body
        attachments: File path(s) to attach
        email_address: Sender email (optional, uses config)
        email_password: Sender password (optional, uses config)
        
    Returns:
        Boolean indicating success
    """
    sender = EmailSender(email_address, email_password)
    try:
        result = sender.send_email(to_addresses, subject, body, attachments)
        sender.close()
        return result
    except Exception as e:
        sender.close()
        raise


if __name__ == "__main__":
    # Test the email sender
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python email_sender.py <recipient_email> [attachment_path]")
        sys.exit(1)
    
    recipient = sys.argv[1]
    attachment = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        sender = EmailSender()
        sender.send_email(
            to_addresses=recipient,
            subject="Test Email from Power BI Automation",
            body="This is a test email from the Power BI automation system.",
            attachments=attachment
        )
        print("Email sent successfully!")
        sender.close()
        
    except Exception as e:
        print(f"Error: {e}")

