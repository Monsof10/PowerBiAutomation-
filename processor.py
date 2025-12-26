import os
import logging
import time
import requests
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from pdf_utils import remove_pages
from config import ENDING_FACILITIES_GROUPS, PDF_NAMES
from email_utils import send_email_with_attachment, send_email_without_attachment, EMAIL_BODY, EMAIL_BODY_NO_ACTIVATIONS

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
PLAYWRIGHT_HEADLESS = os.getenv("PLAYWRIGHT_HEADLESS", "false").lower() == "false"

OUTPUT_DIR = os.getenv("OUTPUT_DIR", r"C:\Users\Nasef\Downloads\project folder")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# If environment variables for start/end selectors are not set, default to the
# selectors provided by the user (useful for local testing). These are the
# Power BI date input selectors you supplied.
if not PLAYWRIGHT_START_DATE_SELECTOR:
    PLAYWRIGHT_START_DATE_SELECTOR = "input[aria-label^=\"Start date\"]"
if not PLAYWRIGHT_END_DATE_SELECTOR:
    PLAYWRIGHT_END_DATE_SELECTOR = "input[aria-label^=\"End date\"]"

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

# For Outlook/Office 365, if 2FA is enabled, you need an App Password
# Generate one at: https://account.microsoft.com/security/app-passwords
# Replace SMTP_PASS with the App Password if authentication fails
EMAIL_FROM = os.getenv("EMAIL_FROM", SMTP_USER)
EMAIL_TO = os.getenv("EMAIL_TO")
EMAIL_SUBJECT = os.getenv("EMAIL_SUBJECT", "Monthly Report")

# Custom email subjects for each group
GROUP_SUBJECTS = {
    1: "OMCC Power BI Monthly Report for OHSU",
    2: "OMCC Power BI Monthly Report for Salem Health",
    3: "OMCC Power BI Monthly Report for PeaceHealth",
    4: "OMCC Power BI Monthly Report for Asante",
    5: "OMCC Power BI Monthly Report for St. Charles",
    6: "OMCC Power BI Monthly Report for Grande Ronde",
    7: "OMCC Power BI Monthly Report for Kaiser",
    8: "OMCC Power BI Monthly Report for Legacy",
    9: "OMCC Power BI Monthly Report for Providence",
    10: "OMCC Power BI Monthly Report for SW WA PeaceHealth",
    11: "OMCC Power BI Monthly Report for Oregon Health Authority",
    12: "OMCC Power BI Monthly Report for Apprise"
}

REMOVE_PAGES = os.getenv("REMOVE_PAGES", "")  # comma-separated indexes, e.g., "0,2"
ENDING_FACILITIES = os.getenv("ENDING_FACILITIES", "")  # comma-separated list

def get_recipients_for_group(group_num):
    """Return a comma-separated recipient string for the given group.
    Falls back to `EMAIL_TO` if the specific `EMAIL_GROUP_<n>` is not set.
    Returns None if no recipients are configured.
    """
    env_name = f"EMAIL_GROUP_{group_num}"
    group_val = os.getenv(env_name)
    if group_val and group_val.strip():
        return group_val.strip()
    if EMAIL_TO and EMAIL_TO.strip():
        return EMAIL_TO.strip()
    logging.warning(f"No recipients found for group {group_num} (env {env_name} or EMAIL_TO)")
    return None

def download_via_requests(url, out_path):
    logging.info("Downloading PDF via requests: %s", url)
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        f.write(r.content)
    return out_path

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
    # Calculate last month dates (first and last day of that month)
    now = datetime.now(timezone.utc)
    last_month = now - relativedelta(months=1)
    start_date = last_month.replace(day=1)
    end_date = (last_month + relativedelta(months=1, day=1)) - relativedelta(days=1)
    logging.info(f"Last month range: {start_date.strftime('%Y-%m-%d')} -> {end_date.strftime('%Y-%m-%d')}")

    # Initialize browser once for all groups to avoid event loop issues
    browser = None
    p = None
    if USE_PLAYWRIGHT:
        from playwright.sync_api import sync_playwright
        p = sync_playwright().start()
        browser = p.chromium.launch(headless=PLAYWRIGHT_HEADLESS)

    try:
        # Process each facility group (1-12)
        for group_num in range(1, 13):
            facilities = ENDING_FACILITIES_GROUPS.get(group_num, '')
            pdf_name = PDF_NAMES.get(group_num, f'report_{group_num}.pdf')

            if not facilities:
                logging.info(f"Skipping group {group_num} - no facilities defined")
                continue

            logging.info(f"Processing group {group_num} with facilities: {facilities}")

            ts = now.strftime("%Y%m%d")
            raw_path = os.path.join(OUTPUT_DIR, f"raw_{pdf_name}_{ts}.pdf")
            modified_path = os.path.join(OUTPUT_DIR, f"{pdf_name}_{ts}.pdf")

            try:
                # 1) Download with specific facility group
                if USE_PLAYWRIGHT:
                    if not PLAYWRIGHT_AVAILABLE:
                        raise RuntimeError("Playwright mode requested but not available.")
                    logging.info("Using Playwright for download...")
                    actual_path, has_activations, activation_count = download_with_playwright(
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
                        headless=PLAYWRIGHT_HEADLESS,
                        output_path=raw_path,
                        ending_facilities=facilities,
                        reset_all_selector="button[data-testid='reset-to-default-btn']",  # Reset button selector for all groups
                        browser=browser,
                        group_num=group_num
                    )
                else:
                    if not DOWNLOAD_URL:
                        raise RuntimeError("No DOWNLOAD_URL specified.")
                    actual_path = download_via_requests(DOWNLOAD_URL, raw_path)
                    # For requests download, we can't check activations, so assume there are some
                    has_activations = True
                    activation_count = 1  # Dummy value

                logging.info("Downloaded to %s", actual_path)

                # Check if we should skip PDF processing and email sending when no activations
                if not has_activations:
                    logging.info(f"No activations found for group {group_num} - sending no-activations email without PDF attachment and skipping PDF export")

                    # Send email without PDF attachment
                    custom_subject = GROUP_SUBJECTS.get(group_num, f"{EMAIL_SUBJECT} - Group {group_num}")
                    to_addr = get_recipients_for_group(group_num)
                    if to_addr:
                        send_email_without_attachment(
                            smtp_host=SMTP_HOST,
                            smtp_port=SMTP_PORT,
                            smtp_user=SMTP_USER,
                            smtp_pass=SMTP_PASS,
                            from_addr=EMAIL_FROM,
                            to_addr=to_addr,
                            subject=custom_subject,
                            body=EMAIL_BODY_NO_ACTIVATIONS
                        )
                    else:
                        logging.info(f"Skipping no-activations email for group {group_num} due to no recipient configuration.")
                    logging.info(f"Group {group_num} completed successfully (no activations email sent).")
                    continue  # Skip to next group

                # Only proceed with PDF export and processing if we have activations
                logging.info(f"Activations found ({activation_count}) for group {group_num} - proceeding with PDF export")

                # 2) Modify PDF (example: remove pages) - only if we have activations
                pages_to_remove = parse_pages_to_remove(REMOVE_PAGES)
                if pages_to_remove:
                    remove_pages(actual_path, modified_path, pages_to_remove)
                    final_path = modified_path
                    logging.info("Removed pages %s -> %s", pages_to_remove, modified_path)
                else:
                    final_path = actual_path
                    logging.info("No modification requested; using raw file.")

                # 3) Email with custom subject including group number
                custom_subject = GROUP_SUBJECTS.get(group_num, f"{EMAIL_SUBJECT} - Group {group_num}")
                to_addr = get_recipients_for_group(group_num)
                if to_addr:
                    send_email_with_attachment(
                        smtp_host=SMTP_HOST,
                        smtp_port=SMTP_PORT,
                        smtp_user=SMTP_USER,
                        smtp_pass=SMTP_PASS,
                        from_addr=EMAIL_FROM,
                        to_addr=to_addr,
                        subject=custom_subject,
                        body=EMAIL_BODY,
                        attachment_path=final_path
                    )
                else:
                    logging.info(f"Skipping email with attachment for group {group_num} due to no recipient configuration.")

                logging.info(f"Group {group_num} completed successfully.")

            except Exception as e:
                logging.exception(f"Group {group_num} failed: {e}")
                continue  # Continue to next group even if one fails
    finally:
        if browser:
            browser.close()
        if p:
            p.stop()

    logging.info("All groups processed.")
    return True
