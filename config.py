"""
Configuration - Central configuration management
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent
DOWNLOADS_FOLDER = BASE_DIR / os.getenv('DOWNLOADS_FOLDER', 'downloads')
OUTPUT_FOLDER = BASE_DIR / os.getenv('OUTPUT_FOLDER', 'output')
LOGS_FOLDER = BASE_DIR / os.getenv('LOGS_FOLDER', 'logs')

# Create folders
DOWNLOADS_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)
LOGS_FOLDER.mkdir(exist_ok=True)

# Power BI
POWERBI_EMAIL = os.getenv('POWERBI_EMAIL')
POWERBI_PASSWORD = os.getenv('POWERBI_PASSWORD')
POWERBI_REPORT_URL = os.getenv('POWERBI_REPORT_URL')

# Email
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.office365.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))

# Inline images and HTML template for emails
# Comma-separated list of image file names (relative to BASE_DIR) to embed by default
EMAIL_INLINE_IMAGES = [p for p in os.getenv('EMAIL_INLINE_IMAGES', 'email body/highmorlogo.png,email body/osmlogo.png').split(',') if p]
# Comma-separated list of Content-IDs that correspond to the images above
EMAIL_INLINE_CIDS = [c for c in os.getenv('EMAIL_INLINE_CIDS', 'logo1,logo2').split(',') if c]
# Optional HTML template file path (relative to BASE_DIR). If set, the send script will use this file.
EMAIL_HTML_TEMPLATE = os.getenv('EMAIL_HTML_TEMPLATE', '')
# HTML template content for emails from EMAIL_BODY env var
EMAIL_BODY = os.getenv('EMAIL_BODY', """<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1.0" />
  </head>
  <body style="margin:0; padding:0; background-color:#a3c7ff;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#a3c7ff;">
      <tr>
        <td align="center">
          <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border:0;">
            
            <!-- Header Section -->
            <tr>
              <td align="center" style="padding:40px 0 30px 0;">
                <b style="font-family:Arial, sans-serif;">This report is powered by</b><br />
                <img src="cid:logo1" width="120" height="60" alt="highMor Logo" style="display:block; margin-top:10px;" /><br />
                <b style="color:#0B65BA; font-family:Arial, sans-serif;">Transfer Center Software</b>
              </td>
            </tr>
            
            <!-- Divider Bar -->
            <tr>
              <td style="background-color:#2157BE; height:10px; line-height:10px; font-size:0;">&nbsp;</td>
            </tr>
            
            <!-- Main Logo + Title -->
            <tr>
              <td align="center" style="padding:36px 30px 42px 30px; color:#2157BE; font-family:Arial, sans-serif; font-size:200%;">
                <img src="cid:logo2" width="150" height="150" alt="OMCC Logo" style="display:block; margin-bottom:20px;" /><br />
                <strong>Power BI Monthly Report</strong>
              </td>
            </tr>
            
            <!-- Divider Bar -->
            <tr>
              <td style="background-color:#2157BE; height:10px; line-height:10px; font-size:0;">&nbsp;</td>
            </tr>
            
            <!-- Body Text -->
            <tr>
              <td style="background-color:#ffffff; padding:20px 30px; color:#000000; font-family:Arial, sans-serif; font-size:16px; line-height:1.4;">
                <p>Good morning,</p>
                <p>Please find the attached PDF data report for your reference. If you have any questions or would like an image of the map (page 6 of the dashboard), please contact Mackie at <a href="mailto:omcc@highmor.com">omcc@highmor.com</a>.</p>
                <p>Warm regards,</p>
                <p><strong>highMor Data Analytics Team</strong></p>
              </td>
            </tr>
            
            <!-- Footer / Padding -->
            <tr>
              <td align="center" style="padding:30px; background-color:#2157BE;">&nbsp;</td>
            </tr>
            
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
""")


DEFAULT_SUBJECT = os.getenv('DEFAULT_SUBJECT', 'Power BI Monthly Report')
DEFAULT_BODY = """Good morning,

Please find the attached PDF data report for your reference. If you have any questions or would like an image of the map (page 6 of the dashboard), please contact Mackie at omcc@highmor.com.

Warm regards,

highMor Data Analytics Team"""

# Settings
USE_API = os.getenv('USE_API', 'True').lower() == 'true'
DOWNLOAD_TIMEOUT = 300
PDF_PREFIX = "report_page"
PDF_THUMBNAIL_SIZE = (200, 280)

# Facility Groups for Multiple PDFs (1-12)
ENDING_FACILITIES_GROUPS = {
    1: "Adventist Health Portland,Doernbecher Children's Hospital,OHSU Hospital,Hillsboro Medical Center",
    2: "Salem Hospital,West Valley Hospital",
    3: "PeaceHealth Cottage Grove Medical Center,PeaceHealth Peace Harbor Medical Center,PeaceHealth Sacred Heart Medical Center - Riverbend,PeaceHealth Sacred Heart Medical Center - UD",
    4: "Asante Ashland Community Hospital,Asante Rogue Valley Medical Center,Asante Three Rivers Medical Center",
    5: "St. Charles - Bend,St. Charles - Madras,St. Charles - Redmond,St. Charles - Prineville",
    6: "Grande Ronde Hospital",
    7: "Kaiser Sunnyside Medical Center,Kaiser Westside Medical Center",
    8: "Legacy Emanuel Medical Center,Legacy Good Samaritan Hospital,Legacy Meridian Park Medical Center,Legacy Mount Hood Medical Center,Legacy Randall Children's Hospital,Legacy Silverton Medical Center,Legacy Salmon Creek Medical Center",
    9: "Providence Hood River Memorial Hospital,Providence Medford Medical Center,Providence Milwaukie Hospital,Providence Newberg Medical Center,Providence Portland Medical Center,Providence Seaside Hospital,Providence St Vincent Medical Center,Providence Willamette Falls,Providence Centralia Hospital,Providence St. Mary",
    10: "PeaceHealth Southwest Medical Center,PeaceHealth St. John Medical Center",
    11: "Select All",
    12: "Select All"
}
PDF_NAMES = {
   1: 'OMCCDashboard',
   2: 'OMCCDashboard',
   3: 'OMCCDashboard',
   4: 'OMCCDashboard',
   5: 'OMCCDashboard',
   6: 'OMCCDashboard',
   7: 'OMCCDashboard',
   8: 'OMCCDashboard',
   9: 'OMCCDashboard',
   10: 'OMCCDashboard',
   11: 'OMCCDashboard',
   12: 'OMCCDashboard'}

# Logging
LOG_FILE = LOGS_FOLDER / 'automation.log'
LOG_LEVEL = 'INFO'
