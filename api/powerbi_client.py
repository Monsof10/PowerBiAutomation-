"""
Power BI API Client - Single responsibility: API communication
"""
import requests
from utils.logger import get_logger

logger = get_logger(__name__)


class PowerBIClient:
    """Power BI REST API client"""
    
    BASE_URL = "https://api.powerbi.com/v1.0/myorg"
    
    def __init__(self, access_token):
        """Initialize client with access token"""
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def get_reports(self):
        """Get all reports"""
        url = f"{self.BASE_URL}/reports"
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        return response.json()["value"]
    
    def get_workspaces(self):
        """Get all workspaces"""
        url = f"{self.BASE_URL}/groups"
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        return response.json()["value"]
    
    def initiate_export(self, group_id, report_id):
        """Start PDF export"""
        url = f"{self.BASE_URL}/groups/{group_id}/reports/{report_id}/ExportTo"
        
        payload = {
            "format": "PDF",
            "paginatedReportConfiguration": {
                "formatSettings": {"UseReportPageSize": True}
            }
        }
        
        response = requests.post(url, headers=self.headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()["id"]
    
    def get_export_status(self, group_id, report_id, export_id):
        """Check export status"""
        url = f"{self.BASE_URL}/groups/{group_id}/reports/{report_id}/ExportTo/{export_id}"
        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def download_export(self, group_id, report_id, export_id):
        """Download exported file"""
        url = f"{self.BASE_URL}/groups/{group_id}/reports/{report_id}/ExportTo/{export_id}/file"
        response = requests.get(url, headers=self.headers, timeout=60)
        response.raise_for_status()
        return response.content

