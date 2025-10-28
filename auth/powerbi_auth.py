"""
Power BI Authentication - Single responsibility: Handle authentication
"""
from msal import PublicClientApplication
from utils.logger import get_logger

logger = get_logger(__name__)


class PowerBIAuth:
    """Handle Power BI authentication via MSAL"""
    
    AUTHORITY = "https://login.microsoftonline.com/organizations"
    SCOPE = ["https://analysis.windows.net/powerbi/api/.default"]
    CLIENT_ID = "ea0616ba-638b-4df5-95b9-636659ae5121"
    
    def __init__(self, email, password):
        """Initialize authenticator"""
        self.email = email
        self.password = password
        self.app = PublicClientApplication(
            client_id=self.CLIENT_ID,
            authority=self.AUTHORITY
        )
    
    def get_token_password(self):
        """Authenticate with username/password"""
        logger.info("Authenticating with username/password...")
        
        result = self.app.acquire_token_by_username_password(
            username=self.email,
            password=self.password,
            scopes=self.SCOPE
        )
        
        if "access_token" in result:
            logger.info("Authentication successful")
            return result["access_token"]
        
        error = result.get("error_description", result.get("error"))
        raise Exception(f"Authentication failed: {error}")
    
    def get_token_device_code(self):
        """Authenticate with device code flow (for MFA)"""
        logger.info("Starting device code authentication...")
        
        flow = self.app.initiate_device_flow(scopes=self.SCOPE)
        
        if "user_code" not in flow:
            raise Exception("Failed to create device flow")
        
        print(f"\n{'='*60}")
        print("AUTHENTICATION REQUIRED")
        print(f"{'='*60}")
        print(flow["message"])
        print(f"{'='*60}\n")
        
        result = self.app.acquire_token_by_device_flow(flow)
        
        if "access_token" in result:
            logger.info("Authentication successful")
            return result["access_token"]
        
        error = result.get("error_description", result.get("error"))
        raise Exception(f"Authentication failed: {error}")

