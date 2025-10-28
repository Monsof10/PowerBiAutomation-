"""
Report Export Service - Single responsibility: Export reports to PDF
"""
import time
from pathlib import Path
from .powerbi_client import PowerBIClient
from utils.logger import get_logger

logger = get_logger(__name__)


class ReportExporter:
    """Handle report export operations"""
    
    def __init__(self, client: PowerBIClient):
        """Initialize with API client"""
        self.client = client
    
    def parse_url(self, report_url):
        """Extract group ID and report ID from URL"""
        parts = report_url.split('/')
        group_id = parts[parts.index('groups') + 1]
        report_id = parts[parts.index('reports') + 1].split('?')[0]
        return group_id, report_id
    
    def export_to_pdf(self, report_url, output_path, timeout=300):
        """
        Export report to PDF
        
        Args:
            report_url: Power BI report URL
            output_path: Output file path
            timeout: Maximum wait time in seconds
            
        Returns:
            Path: Path to exported PDF
        """
        logger.info(f"Exporting report: {report_url}")
        
        group_id, report_id = self.parse_url(report_url)
        
        # Initiate export
        export_id = self.client.initiate_export(group_id, report_id)
        logger.info(f"Export initiated: {export_id}")
        
        # Wait for completion
        self._wait_for_export(group_id, report_id, export_id, timeout)
        
        # Download file
        content = self.client.download_export(group_id, report_id, export_id)
        
        # Save to file
        output_path = Path(output_path)
        output_path.write_bytes(content)
        
        logger.info(f"PDF saved: {output_path}")
        return output_path
    
    def _wait_for_export(self, group_id, report_id, export_id, timeout):
        """Wait for export to complete"""
        start_time = time.time()
        
        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError("Export timeout exceeded")
            
            status_data = self.client.get_export_status(group_id, report_id, export_id)
            status = status_data["status"]
            
            logger.info(f"Export status: {status}")
            
            if status == "Succeeded":
                return
            elif status == "Failed":
                error = status_data.get("error", "Unknown error")
                raise Exception(f"Export failed: {error}")
            
            time.sleep(5)

