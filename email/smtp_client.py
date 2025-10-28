"""
SMTP Email Client - Single responsibility: Send emails via SMTP
"""
import yagmail
from utils.logger import get_logger

logger = get_logger(__name__)


class SMTPClient:
    """SMTP email client using yagmail"""
    
    def __init__(self, email_address, email_password, smtp_server, smtp_port):
        """
        Initialize SMTP client
        
        Args:
            email_address: Sender email
            email_password: Sender password/app password
            smtp_server: SMTP server address
            smtp_port: SMTP server port
        """
        self.email_address = email_address
        
        logger.info("Initializing SMTP client...")
        
        self.client = yagmail.SMTP(
            user=email_address,
            password=email_password,
            host=smtp_server,
            port=smtp_port
        )
        
        logger.info("SMTP client ready")
    
    def send(self, to_addresses, subject, body, attachments=None):
        """
        Send email
        
        Args:
            to_addresses: Recipient email(s)
            subject: Email subject
            body: Email body text
            attachments: File path(s) to attach
            
        Returns:
            bool: True if successful
        """
        # Normalize inputs
        if isinstance(to_addresses, str):
            to_addresses = [to_addresses]
        
        if attachments and isinstance(attachments, (str, Path)):
            attachments = [str(attachments)]
        elif attachments:
            attachments = [str(att) for att in attachments]
        
        logger.info(f"Sending email to: {', '.join(to_addresses)}")
        
        self.client.send(
            to=to_addresses,
            subject=subject,
            contents=body,
            attachments=attachments
        )
        
        logger.info("Email sent successfully")
        return True
    
    def close(self):
        """Close SMTP connection"""
        if self.client:
            self.client.close()
            logger.info("SMTP connection closed")

