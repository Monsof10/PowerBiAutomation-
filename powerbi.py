"""
Power BI Facade - Simple interface for Power BI operations
"""
from pathlib import Path
import time
from auth.powerbi_auth import PowerBIAuth
from api.powerbi_client import PowerBIClient
from api.report_exporter import ReportExporter
from utils.logger import setup_logger
import config

logger = setup_logger('powerbi', config.LOG_FILE, config.LOG_LEVEL)


def export_report(report_url, output_path=None, use_device_code=False):
    """
    Export Power BI report to PDF
    
    Args:
        report_url: Power BI report URL
        output_path: Output file path (optional)
        use_device_code: Use device code authentication
        
    Returns:
        Path: Path to exported PDF
    """
    if output_path is None:
        output_path = config.DOWNLOADS_FOLDER / f"report_{int(time.time())}.pdf"
    
    # Authenticate
    auth = PowerBIAuth(config.POWERBI_EMAIL, config.POWERBI_PASSWORD)
    
    try:
        token = auth.get_token_password() if not use_device_code else auth.get_token_device_code()
    except:
        logger.warning("Password auth failed, trying device code...")
        token = auth.get_token_device_code()
    
    # Export report
    client = PowerBIClient(token)
    exporter = ReportExporter(client)
    
    return exporter.export_to_pdf(report_url, output_path)


def list_reports():
    """Get list of available reports"""
    auth = PowerBIAuth(config.POWERBI_EMAIL, config.POWERBI_PASSWORD)
    token = auth.get_token_password()
    client = PowerBIClient(token)
    return client.get_reports()


def list_workspaces():
    """Get list of workspaces"""
    auth = PowerBIAuth(config.POWERBI_EMAIL, config.POWERBI_PASSWORD)
    token = auth.get_token_password()
    client = PowerBIClient(token)
    return client.get_workspaces()

