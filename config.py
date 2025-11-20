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
EMAIL_BODY="""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="x-apple-disable-message-reformatting">
<title></title>
<!--[if mso]>
<noscript>
<xml>
<o:OfficeDocumentSettings>
<o:PixelsPerInch>96</o:PixelsPerInch>
</o:OfficeDocumentSettings>
</xml>
</noscript>
<![endif]-->
<style>
table, td, div, h1, p {font-family: Arial, sans-serif;}
</style>
</head>
<body style="margin:0;padding:0;">
<table role="presentation" style="width:100%;border-collapse:collapse;border:0;border-spacing:0;background:#a3c7ff;">
<tr>
<td align="center" style="padding:0;">
<table role="presentation" style="width:602px;border-collapse:collapse;border:1px solid #cccccc;border-spacing:0;text-align:left;">
<tr>
<td align="center" style="padding:40px 0 30px 0;background:#ffffff;">
<b>This report is powered by</b><br>
<a href="https://www.highmor.com">
<img src="data:image/png;base64,@{body('Get_file_content_using_path')?['$content']}" width="120" height="60" />
</a><br>
<b style="color: #0B65BA;">Transfer Center Software</b>
</td>
</tr>
<tr>
<td align="center" style="padding:10px 10px 10px 30px;background:#2157BE;">
</td>
</tr>
<tr>
<td style="background:#FFFFFF;color:#2157BE;padding:36px 30px 42px 30px; text-align:center;font-size:200%;">
<img src="data:image/png;base64,@{body('Get_file_content_using_path')?['$content']}" width="120" height="60" />
<b>Power BI Monthly Report</b>
</td>
</tr>
<tr>
<td align="center" style="padding:10px 10px 10px 30px;background:#2157BE;">
</td>
</tr>
<tr>
<td style="background:#ffffff;padding:10px 10px 10px 10px;font-size:150%; color:#000000; line-height:1.4;">
<p>Good morning,</p>
<p>Please find the attached PDF data report for your reference. If you have any questions or would like an image of the map (page 6 of the dashboard), please contact Mackie at <a href="mailto:omcc@highmor.com">omcc@highmor.com</a>.</p>
<p>Warm regards,</p>
<p><strong>highMor Data Analytics Team</strong></p>
</td>
</tr>
<tr>
<td align="center" style="padding:30px 30px 30px 30px;background:#2157BE;">
</td>
</tr>
</table>
</td>
</tr>
</table>
</body>
</html>"""


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
    11: "Adventist Health Portland,Doernbecher Children's Hospital,OHSU Hospital,Hillsboro Medical Center,PeaceHealth Southwest Medical Center,PeaceHealth St. John Medical Center",
    12: "Adventist Health Portland,Doernbecher Children's Hospital,OHSU Hospital,Hillsboro Medical Center,PeaceHealth Southwest Medical Center,PeaceHealth St. John Medical Center"
}
PDF_NAMES = {
   1: 'OHSU.pdf',
-    2: 'Salem_Health.pdf',
-    3: 'PeaceHealth.pdf',
-    4: 'Asante.pdf',
-    5: 'St_Charles.pdf',
-    6: 'Grande_Ronde.pdf',
-    7: 'Kaiser.pdf',
-    8: 'Legacy.pdf',
-    9: 'Providence.pdf',
-    10: 'SW_WA_PeaceHealth.pdf',
-    11: 'Oregon_Health_Authority.pdf',
-    12: 'Apprise.pdf'}

# Logging
LOG_FILE = LOGS_FOLDER / 'automation.log'
LOG_LEVEL = 'INFO'
