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
EMAIL_BODY ="""<!DOCTYPE html>
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
<img src="data:image/png;base64,@{body('Get_file_content_using_path')?['$content']}" width="120" height="60" alt="highMor Logo" style="display:block;" />
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
<img src="data:image/png;base64,@{body(' Get_file_content_using_path_2 ')?['$content']}" width="150" height="150" alt="Report Logo" style="display:block; margin: 0 auto;" /><br>
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

# Alternative email body for when there are no activations
EMAIL_BODY_NO_ACTIVATIONS = """<!DOCTYPE html>
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
<a href="https://www.highmor.com"> <!-- Your hyperlink goes here -->
<img src="data:image/png;base64,@{body('Get_file_content_using_path')?['$content']}" width="120" height="60" />
</a>
<br> <b style="color: #0B65BA;">Transfer Center Software</b>
</td>
</tr>
</td>
</tr>
<tr>
<td align="center" style="padding:10px 10px 10px 30px;background:#2157BE;">
</td>
</tr>
<tr>
<td style="background:#FFFFFF;color:#2157BE;padding:36px 30px 42px 30px; text-align:center;font-size:200%;">
<img src="data:image/png;base64,@{body(' Get_file_content_using_path_2 ')?['$content']}" width="150" height="150" />
<br>
<b>Power BI Monthly Report</b>
</td>
</tr>
<tr>
<td align="center" style="padding:10px 10px 10px 30px;background:#2157BE;">
</td>
</tr>
<tr>
<td style="background:#ffffff;padding:10px 10px 10px 10px;font-size:150%;">
<p><br>
                        Good morning,<br><br>
                        There were no accepted patients to your facilities last month via OMCC. If you have any questions or concerns, please contact our support team at omcc@highmor.com.
<br><br>
                        Warm regards,<br><br>
                        highMor Data Analytics Team<br>
</p>
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
    msg.set_content(body, subtype='html')
    with open(attachment_path, "rb") as f:
        data = f.read()
    msg.add_attachment(data, maintype="application", subtype="pdf", filename=os.path.basename(attachment_path))
    logging.info("Connecting to SMTP %s:%s", smtp_host, smtp_port)
    try:
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=60)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        logging.info("Email sent to %s", to_addr)
    except smtplib.SMTPAuthenticationError as e:
        if "basic authentication is disabled" in str(e) or "535" in str(e):
            logging.error("Authentication failed. For Gmail accounts, you need an App Password: "
                         "1. Go to https://myaccount.google.com/security "
                         "2. Enable 2-Step Verification if not already enabled "
                         "1. Go to https://myaccount.google.com/apppasswords "
                         "2. Generate an App Password for 'Mail' "
                         "3. Use the App Password instead of your regular password in SMTP_PASS")
            raise
        else:
            raise

def send_email_without_attachment(smtp_host, smtp_port, smtp_user, smtp_pass,
                                  from_addr, to_addr, subject, body):
    logging.info("Preparing email to %s (no attachment)", to_addr)
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.set_content(body, subtype='html')  # HTML content for the no-activations email
    logging.info("Connecting to SMTP %s:%s", smtp_host, smtp_port)
    try:
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=60)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        logging.info("Email sent to %s (no attachment)", to_addr)
    except smtplib.SMTPAuthenticationError as e:
        if "basic authentication is disabled" in str(e) or "535" in str(e):
            logging.error("Authentication failed. For Gmail accounts, you need an App Password: "
                         "1. Go to https://myaccount.google.com/security "
                         "2. Enable 2-Step Verification if not already enabled "
                         "1. Go to https://myaccount.google.com/apppasswords "
                         "2. Generate an App Password for 'Mail' "
                         "3. Use the App Password instead of your regular password in SMTP_PASS")
            raise
        else:
            raise

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

    # Import config for facility groups
    from config import ENDING_FACILITIES_GROUPS, PDF_NAMES

    # Initialize browser once for all groups to avoid event loop issues
    browser = None
    p = None
    if USE_PLAYWRIGHT:
        from playwright.sync_api import sync_playwright
        p = sync_playwright().start()
        browser = p.chromium.launch(headless=False)

    try:
        # Process each facility group (1-12)
        for group_num in range(1, 13):
            facilities = ENDING_FACILITIES_GROUPS.get(group_num, '')
            pdf_name = PDF_NAMES.get(group_num, f'report_{group_num}.pdf')

            if not facilities:
                logging.info(f"Skipping group {group_num} - no facilities defined")
                continue

            logging.info(f"Processing group {group_num} with facilities: {facilities}")

            ts = now.strftime("%Y%m%dT%H%M%SZ")
            raw_path = os.path.join(OUTPUT_DIR, f"raw_{pdf_name}_{ts}.pdf")
            modified_path = os.path.join(OUTPUT_DIR, f"modified_{pdf_name}_{ts}.pdf")

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
                        headless=False,
                        output_path=raw_path,
                        ending_facilities=facilities,
                        reset_all_selector="button[data-testid='reset-to-default-btn']",  # Reset button selector for all groups
                        browser=browser
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
                    custom_subject = f"{EMAIL_SUBJECT} - Group {group_num}"
                    send_email_without_attachment(
                        smtp_host=SMTP_HOST,
                        smtp_port=SMTP_PORT,
                        smtp_user=SMTP_USER,
                        smtp_pass=SMTP_PASS,
                        from_addr=EMAIL_FROM,
                        to_addr=EMAIL_TO,
                        subject=custom_subject,
                        body=EMAIL_BODY_NO_ACTIVATIONS
                    )
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
                custom_subject = f"{EMAIL_SUBJECT} - Group {group_num}"
                send_email_with_attachment(
                    smtp_host=SMTP_HOST,
                    smtp_port=SMTP_PORT,
                    smtp_user=SMTP_USER,
                    smtp_pass=SMTP_PASS,
                    from_addr=EMAIL_FROM,
                    to_addr=EMAIL_TO,
                    subject=custom_subject,
                    body=EMAIL_BODY,
                    attachment_path=final_path
                )

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

if __name__ == "__main__":
    ok = run_once()
    sys.exit(0 if ok else 1)
