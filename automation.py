# automation.py
import os
import sys
import logging
import time
import smtplib
from email.message import EmailMessage
import requests
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from pdf_utils import remove_pages

# Optional import for Playwright mode
try:
    from playwright_download import download_with_playwright
    PLAYWRIGHT_AVAILABLE = True
except Exception:
    PLAYWRIGHT_AVAILABLE = False

load_dotenv()  # load .env if present

# Configuration via environment variables
DOWNLOAD_URL = os.getenv("DOWNLOAD_URL")       # direct PDF link (preferred)
USE_PLAYWRIGHT = os.getenv("USE_PLAYWRIGHT", "false").lower() == "true"
PLAYWRIGHT_LOGIN_URL = os.getenv("PLAYWRIGHT_LOGIN_URL", "")
PLAYWRIGHT_USERNAME = os.getenv("PLAYWRIGHT_USERNAME", "")
PLAYWRIGHT_PASSWORD = os.getenv("PLAYWRIGHT_PASSWORD", "")
PLAYWRIGHT_DOWNLOAD_SELECTOR = os.getenv("PLAYWRIGHT_DOWNLOAD_SELECTOR", "")
PLAYWRIGHT_START_DATE_SELECTOR = os.getenv("PLAYWRIGHT_START_DATE_SELECTOR", "")
PLAYWRIGHT_END_DATE_SELECTOR = os.getenv("PLAYWRIGHT_END_DATE_SELECTOR", "")
PLAYWRIGHT_START_CALENDAR_BUTTON = os.getenv("PLAYWRIGHT_START_CALENDAR_BUTTON", "")
PLAYWRIGHT_END_CALENDAR_BUTTON = os.getenv("PLAYWRIGHT_END_CALENDAR_BUTTON", "")

OUTPUT_DIR = os.getenv("OUTPUT_DIR", r"C:\Users\Nasef\Downloads\project folder")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# If environment variables for start/end selectors are not set, default to the
# selectors provided by the user (useful for local testing). These are the
# Power BI date input selectors you supplied.
if not PLAYWRIGHT_START_DATE_SELECTOR:
    PLAYWRIGHT_START_DATE_SELECTOR = "input[aria-label^=\"Start date\"]"
if not PLAYWRIGHT_END_DATE_SELECTOR:
    PLAYWRIGHT_END_DATE_SELECTOR = "input[aria-label^=\"End date\"]"


SMTP_HOST = os.getenv("SMTP_HOST", "smtp.office365.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
EMAIL_FROM = os.getenv("EMAIL_FROM", SMTP_USER)
EMAIL_TO = os.getenv("EMAIL_TO")
EMAIL_SUBJECT = os.getenv("EMAIL_SUBJECT", "Monthly Report")
EMAIL_BODY = os.getenv("EMAIL_BODY", "Please find the attached PDF report.")
REMOVE_PAGES = os.getenv("REMOVE_PAGES", "")  # comma-separated indexes, e.g., "0,2"
ENDING_FACILITIES = os.getenv("ENDING_FACILITIES", "")  # comma-separated list


LOG_FILE = os.path.join(OUTPUT_DIR, "automation.log")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s:%(levelname)s:%(message)s",
                    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)])

def download_via_requests(url, out_path):
    logging.info("Downloading PDF via requests: %s", url)
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        f.write(r.content)
    return out_path

def send_email_with_attachment(smtp_host, smtp_port, smtp_user, smtp_pass,
                               from_addr, to_addr, subject, body, attachment_path):
    logging.info("Preparing email to %s", to_addr)
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.set_content(body)
    with open(attachment_path, "rb") as f:
        data = f.read()
    msg.add_attachment(data, maintype="application", subtype="pdf", filename=os.path.basename(attachment_path))
    logging.info("Connecting to SMTP %s:%s", smtp_host, smtp_port)
    server = smtplib.SMTP(smtp_host, smtp_port, timeout=60)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(smtp_user, smtp_pass)
    server.send_message(msg)
    server.quit()
    logging.info("Email sent to %s", to_addr)

def parse_pages_to_remove(s):
    if not s:
        return []
    pages = []
    for x in s.split(","):
        x = x.strip()
        if x.isdigit():
            page_num = int(x)
            if page_num > 0:  # 1-based to 0-based
                pages.append(page_num - 1)
    return pages

def run_once():
    # Calculate 3 months ago dates (first and last day of that month)
    now = datetime.now(timezone.utc)
    three_months_ago = now - relativedelta(months=3)
    start_date = three_months_ago.replace(day=1)
    end_date = (three_months_ago + relativedelta(months=1, day=1)) - relativedelta(days=1)
    logging.info(f"Three months ago range: {start_date.strftime('%Y-%m-%d')} -> {end_date.strftime('%Y-%m-%d')}")
    ts = now.strftime("%Y%m%dT%H%M%SZ")
    raw_path = os.path.join(OUTPUT_DIR, f"raw_report_{ts}.pdf")
    modified_path = os.path.join(OUTPUT_DIR, f"modified_report_{ts}.pdf")
    try:
        # 1) Download
        if USE_PLAYWRIGHT:
            if not PLAYWRIGHT_AVAILABLE:
                raise RuntimeError("Playwright mode requested but not available.")
            logging.info("Using Playwright for download...")
            download_with_playwright(
                login_url=PLAYWRIGHT_LOGIN_URL,
                username=PLAYWRIGHT_USERNAME,
                password=PLAYWRIGHT_PASSWORD,
                download_button_selector=PLAYWRIGHT_DOWNLOAD_SELECTOR,
                start_date_selector=PLAYWRIGHT_START_DATE_SELECTOR or None,
                end_date_selector=PLAYWRIGHT_END_DATE_SELECTOR or None,
                start_calendar_button="#ecad9678-2545-5b92-c15b-dfbf29949228",
                end_calendar_button=PLAYWRIGHT_END_CALENDAR_BUTTON or None,
                start_date=start_date,
                end_date=end_date,
                headless=False,
                output_path=raw_path,
                ending_facilities=ENDING_FACILITIES
            )
        else:
            if not DOWNLOAD_URL:
                raise RuntimeError("No DOWNLOAD_URL specified.")
            download_via_requests(DOWNLOAD_URL, raw_path)

        logging.info("Downloaded to %s", raw_path)

        # 2) Modify PDF (example: remove pages)
        pages_to_remove = parse_pages_to_remove(REMOVE_PAGES)
        if pages_to_remove:
            remove_pages(raw_path, modified_path, pages_to_remove)
            final_path = modified_path
            logging.info("Removed pages %s -> %s", pages_to_remove, modified_path)
        else:
            final_path = raw_path
            logging.info("No modification requested; using raw file.")

        # 3) Email
        send_email_with_attachment(
            smtp_host=SMTP_HOST,
            smtp_port=SMTP_PORT,
            smtp_user=SMTP_USER,
            smtp_pass=SMTP_PASS,
            from_addr=EMAIL_FROM,
            to_addr=EMAIL_TO,
            subject=EMAIL_SUBJECT,
            body=EMAIL_BODY,
            attachment_path=final_path
        )

        logging.info("Run completed successfully.")
        return True
    except Exception as e:
        logging.exception("Run failed: %s", e)
        return False

if __name__ == "__main__":
    ok = run_once()
    sys.exit(0 if ok else 1)
