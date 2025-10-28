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

# Defaults
DEFAULT_RECIPIENTS = os.getenv('DEFAULT_RECIPIENTS', '').split(',')
DEFAULT_SUBJECT = os.getenv('DEFAULT_SUBJECT', 'Power BI Report')
DEFAULT_BODY = os.getenv('DEFAULT_BODY', 'Please find attached report.')

# Settings
USE_API = os.getenv('USE_API', 'True').lower() == 'true'
DOWNLOAD_TIMEOUT = 300
PDF_PREFIX = "report_page"
PDF_THUMBNAIL_SIZE = (200, 280)

# Logging
LOG_FILE = LOGS_FOLDER / 'automation.log'
LOG_LEVEL = 'INFO'
