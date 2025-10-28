"""
Configuration settings for Power BI Automation
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent
DOWNLOADS_FOLDER = BASE_DIR / os.getenv('DOWNLOADS_FOLDER', 'downloads')
OUTPUT_FOLDER = BASE_DIR / os.getenv('OUTPUT_FOLDER', 'output')
LOGS_FOLDER = BASE_DIR / os.getenv('LOGS_FOLDER', 'logs')

# Create folders if they don't exist
DOWNLOADS_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)
LOGS_FOLDER.mkdir(exist_ok=True)

# Power BI Configuration
POWERBI_EMAIL = os.getenv('POWERBI_EMAIL')
POWERBI_PASSWORD = os.getenv('POWERBI_PASSWORD')
POWERBI_REPORT_URL = os.getenv('POWERBI_REPORT_URL')

# Email Configuration
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))

# Default Email Settings
DEFAULT_RECIPIENTS = os.getenv('DEFAULT_RECIPIENTS', '').split(',')
DEFAULT_SUBJECT = os.getenv('DEFAULT_SUBJECT', 'Power BI Report - Last 30 Days')
DEFAULT_BODY = os.getenv('DEFAULT_BODY', 'Please find attached the Power BI report for the last 30 days.')

# Automation Settings
HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'False').lower() == 'true'
DOWNLOAD_TIMEOUT = 120  # seconds
PAGE_LOAD_TIMEOUT = 30  # seconds

# PDF Settings
PDF_PREFIX = "report_page"
PDF_THUMBNAIL_SIZE = (200, 280)

# Logging
LOG_FILE = LOGS_FOLDER / 'automation.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'

