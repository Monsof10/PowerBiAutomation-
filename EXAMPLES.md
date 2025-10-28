# Usage Examples

## Example 1: Basic Usage

### Step-by-Step First Run

```bash
# 1. Setup
./setup.sh  # or setup.bat on Windows

# 2. Configure
cp env.example .env
nano .env  # or use your favorite editor

# 3. Add credentials
# POWERBI_EMAIL=john@company.com
# POWERBI_PASSWORD=MySecurePassword123
# POWERBI_REPORT_URL=https://app.powerbi.com/groups/abc-123/reports/def-456
# EMAIL_ADDRESS=john@gmail.com
# EMAIL_PASSWORD=abcd efgh ijkl mnop  # Gmail App Password

# 4. Test setup
python test_setup.py

# 5. Run application
streamlit run main.py

# 6. In browser (http://localhost:8501):
# - Click "Start Automation"
# - Wait for completion (~2-5 minutes)
# - Select PDF pages to send
# - Add recipient emails
# - Click "Send Emails"
```

---

## Example 2: Using Individual Modules

### Power BI Automation Only

```python
from powerbi_automation import run_automation

# Export a report
pdf_path = run_automation(
    email="user@company.com",
    password="password",
    report_url="https://app.powerbi.com/...",
    apply_filter=True,
    headless=False  # Show browser
)

print(f"PDF saved to: {pdf_path}")
```

### PDF Processing Only

```python
from pdf_handler import PDFHandler

# Split a PDF
handler = PDFHandler('my_report.pdf')

# Get info
info = handler.get_pdf_info()
print(f"Pages: {info['pages']}")

# Split into pages
split_pdfs = handler.split_pdf(prefix="monthly_report")
print(f"Created {len(split_pdfs)} PDFs")

# Generate thumbnails
thumbnails = handler.generate_thumbnails()
print(f"Created {len(thumbnails)} thumbnails")

# Cleanup when done
handler.cleanup_all()
```

### Email Sending Only

```python
from email_sender import EmailSender

# Send email
sender = EmailSender()

sender.send_email(
    to_addresses=['client1@example.com', 'client2@example.com'],
    subject='Monthly Report - October 2025',
    body='Please find attached your monthly report.',
    attachments=['report_page_1.pdf', 'report_page_2.pdf']
)

sender.close()
```

---

## Example 3: Custom Workflow

```python
"""
Custom workflow: Export report, split, and send first 3 pages only
"""
from powerbi_automation import PowerBIAutomation
from pdf_handler import PDFHandler
from email_sender import EmailSender

# Step 1: Get report from Power BI
automation = PowerBIAutomation(headless=False)
pdf_path = automation.run_full_automation(apply_filter=True)

# Step 2: Split PDF
handler = PDFHandler(pdf_path)
all_pdfs = handler.split_pdf()

# Step 3: Select first 3 pages only
selected_pdfs = all_pdfs[:3]

# Step 4: Send emails
sender = EmailSender()
sender.send_email(
    to_addresses='manager@company.com',
    subject='Report Summary - First 3 Pages',
    body='Here are the key pages from today\'s report.',
    attachments=selected_pdfs
)
sender.close()

print("Done! Sent first 3 pages only.")
```

---

## Example 4: Batch Processing Multiple Recipients

```python
"""
Send different pages to different recipients
"""
from email_sender import EmailSender

sender = EmailSender()

# Configuration for different recipients
email_configs = [
    {
        'to': 'sales@company.com',
        'subject': 'Sales Report',
        'body': 'Here is your sales data.',
        'attachments': ['report_page_1.pdf', 'report_page_2.pdf']
    },
    {
        'to': 'marketing@company.com',
        'subject': 'Marketing Report',
        'body': 'Here is your marketing data.',
        'attachments': ['report_page_3.pdf', 'report_page_4.pdf']
    },
    {
        'to': 'executive@company.com',
        'subject': 'Executive Summary',
        'body': 'Here is the complete report.',
        'attachments': ['report_page_1.pdf', 'report_page_2.pdf', 
                       'report_page_3.pdf', 'report_page_4.pdf']
    }
]

# Send all emails
results = sender.send_multiple_emails(email_configs)

print(f"Sent: {results['sent']}")
print(f"Failed: {results['failed']}")

sender.close()
```

---

## Example 5: Scheduled Daily Reports

### Using cron (Linux/Mac)

Create a script `daily_report.py`:

```python
#!/usr/bin/env python3
"""
Daily automated report at 8 AM
"""
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from powerbi_automation import run_automation
from pdf_handler import split_pdf_file
from email_sender import send_email_with_attachments
import config

def main():
    try:
        # 1. Get report
        print("Getting Power BI report...")
        pdf_path = run_automation(headless=True)  # Run in background
        
        # 2. Split
        print("Processing PDF...")
        split_pdfs, _ = split_pdf_file(pdf_path)
        
        # 3. Send
        print("Sending emails...")
        send_email_with_attachments(
            to_addresses=config.DEFAULT_RECIPIENTS,
            subject=f"Daily Report - {datetime.now().strftime('%Y-%m-%d')}",
            body="Please find attached today's report.",
            attachments=split_pdfs
        )
        
        print("✅ Daily report sent successfully!")
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
```

Add to crontab:
```bash
# Edit crontab
crontab -e

# Add this line (runs at 8 AM daily)
0 8 * * * cd /home/user/powerbiAutomation && ./venv/bin/python daily_report.py >> logs/daily.log 2>&1
```

### Using Task Scheduler (Windows)

1. Create `daily_report.bat`:
```batch
@echo off
cd C:\Users\YourUser\powerbiAutomation
call venv\Scripts\activate
python daily_report.py >> logs\daily.log 2>&1
```

2. Open Task Scheduler
3. Create Task:
   - Trigger: Daily at 8:00 AM
   - Action: Run `daily_report.bat`

---

## Example 6: Error Handling

```python
"""
Robust error handling example
"""
from powerbi_automation import PowerBIAutomation
from email_sender import EmailSender
import logging

logger = logging.getLogger(__name__)

def automated_workflow():
    automation = None
    sender = None
    
    try:
        # Try automation
        logger.info("Starting automation...")
        automation = PowerBIAutomation(headless=False)
        automation.start_browser()
        
        try:
            automation.login()
        except Exception as e:
            logger.error(f"Login failed: {e}")
            # Take screenshot for debugging
            automation.page.screenshot(path='login_error.png')
            raise
        
        try:
            automation.navigate_to_report()
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            automation.page.screenshot(path='nav_error.png')
            raise
        
        try:
            pdf_path = automation.export_to_pdf()
        except Exception as e:
            logger.error(f"Export failed: {e}")
            automation.page.screenshot(path='export_error.png')
            raise
        
        logger.info(f"Success! PDF: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        logger.error(f"Workflow failed: {e}", exc_info=True)
        
        # Send error notification email
        try:
            sender = EmailSender()
            sender.send_email(
                to_addresses='admin@company.com',
                subject='Power BI Automation Failed',
                body=f'The automation failed with error: {str(e)}'
            )
        except:
            logger.error("Could not send error email")
        
        raise
        
    finally:
        # Cleanup
        if automation:
            automation.close()
        if sender:
            sender.close()

if __name__ == '__main__':
    try:
        automated_workflow()
    except Exception as e:
        print(f"Failed: {e}")
        exit(1)
```

---

## Example 7: Custom Date Filter

```python
"""
Custom date filter for specific report structure
"""
from powerbi_automation import PowerBIAutomation
import time

class CustomPowerBIAutomation(PowerBIAutomation):
    """Extended automation with custom filter"""
    
    def apply_custom_date_filter(self, start_date, end_date):
        """
        Apply specific date range
        Args:
            start_date: "2025-10-01"
            end_date: "2025-10-31"
        """
        try:
            # Find date filter by specific attribute
            date_filter = self.page.locator('[aria-label="Date Range"]').first
            date_filter.click()
            time.sleep(2)
            
            # Clear existing dates
            clear_button = self.page.locator('button:has-text("Clear")').first
            if clear_button.is_visible(timeout=5000):
                clear_button.click()
                time.sleep(1)
            
            # Enter start date
            start_input = self.page.locator('input[aria-label="Start date"]').first
            start_input.fill(start_date)
            time.sleep(1)
            
            # Enter end date
            end_input = self.page.locator('input[aria-label="End date"]').first
            end_input.fill(end_date)
            time.sleep(1)
            
            # Apply filter
            apply_button = self.page.locator('button:has-text("Apply")').first
            apply_button.click()
            time.sleep(3)
            
            logger.info(f"Applied date range: {start_date} to {end_date}")
            return True
            
        except Exception as e:
            logger.error(f"Custom filter failed: {e}")
            return False

# Usage
automation = CustomPowerBIAutomation()
automation.start_browser()
automation.login()
automation.navigate_to_report()
automation.apply_custom_date_filter("2025-10-01", "2025-10-31")
pdf_path = automation.export_to_pdf()
automation.close()
```

---

## Example 8: Testing Individual Components

### Test Power BI Connection

```python
"""test_powerbi.py - Test Power BI login only"""
from powerbi_automation import PowerBIAutomation

automation = PowerBIAutomation(headless=False)
automation.start_browser()

try:
    automation.login()
    print("✅ Login successful!")
    input("Press Enter to close browser...")
finally:
    automation.close()
```

### Test Email Configuration

```python
"""test_email.py - Test email sending"""
from email_sender import EmailSender

sender = EmailSender()

try:
    sender.send_email(
        to_addresses='your.email@example.com',
        subject='Test Email',
        body='If you receive this, email is working!',
        attachments=None
    )
    print("✅ Email sent! Check your inbox.")
except Exception as e:
    print(f"❌ Email failed: {e}")
finally:
    sender.close()
```

### Test PDF Processing

```python
"""test_pdf.py - Test PDF splitting"""
from pdf_handler import PDFHandler

# Use a sample PDF
handler = PDFHandler('sample.pdf')

print("PDF Info:")
info = handler.get_pdf_info()
print(f"  Pages: {info['pages']}")
print(f"  Size: {info['size_mb']:.2f} MB")

print("\nSplitting PDF...")
pdfs = handler.split_pdf()
print(f"  Created {len(pdfs)} PDFs")

print("\nGenerating thumbnails...")
thumbs = handler.generate_thumbnails()
print(f"  Created {len(thumbs)} thumbnails")

print("\n✅ All PDF operations successful!")
```

---

## Example 9: Integration with External Systems

### Slack Notification

```python
"""Send notification to Slack after completion"""
import requests
from powerbi_automation import run_automation

# Your Slack webhook URL
SLACK_WEBHOOK = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

def notify_slack(message):
    requests.post(SLACK_WEBHOOK, json={"text": message})

try:
    pdf_path = run_automation()
    notify_slack(f"✅ Power BI report generated: {pdf_path.name}")
except Exception as e:
    notify_slack(f"❌ Power BI automation failed: {str(e)}")
```

### Save to Cloud Storage

```python
"""Upload to AWS S3 after processing"""
import boto3
from powerbi_automation import run_automation
from pdf_handler import split_pdf_file

# Run automation
pdf_path = run_automation()
split_pdfs, _ = split_pdf_file(pdf_path)

# Upload to S3
s3 = boto3.client('s3')
bucket = 'my-reports-bucket'

for pdf in split_pdfs:
    s3.upload_file(
        str(pdf),
        bucket,
        f'reports/{pdf.name}'
    )
    print(f"Uploaded {pdf.name} to S3")
```

---

## Example 10: Configuration Variations

### Use Different Email Provider (Outlook)

```python
"""Using Outlook/Office 365 instead of Gmail"""
from email_sender import EmailSender

sender = EmailSender(
    email_address='user@company.com',
    email_password='your_password',
    smtp_server='smtp.office365.com',
    smtp_port=587
)

sender.send_email(
    to_addresses='recipient@example.com',
    subject='Report from Outlook',
    body='Sent via Office 365',
    attachments=['report.pdf']
)

sender.close()
```

### Run in Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy files
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install chromium --with-deps

COPY . .

# Run
CMD ["streamlit", "run", "main.py"]
```

Build and run:
```bash
docker build -t powerbi-automation .
docker run -p 8501:8501 -v $(pwd)/.env:/app/.env powerbi-automation
```

---

## Need More Examples?

Check the documentation:
- `README.md` - Full documentation
- `TROUBLESHOOTING.md` - Common issues
- `ARCHITECTURE.md` - System design

---

**Happy Automating! 🚀**

