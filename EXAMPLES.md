# Usage Examples

## Basic Usage

### Export Power BI Report

```python
import powerbi

# Export report to PDF
pdf_path = powerbi.export_report(
    report_url="https://app.powerbi.com/groups/workspace/reports/report-id"
)
print(f"PDF saved: {pdf_path}")

# With device code authentication (for MFA)
pdf_path = powerbi.export_report(
    report_url="https://app.powerbi.com/...",
    use_device_code=True
)
```

### Process PDF

```python
import pdf_service

# Split PDF into pages
pdf_files, thumbnails = pdf_service.split_pdf(
    pdf_path="report.pdf",
    prefix="monthly_report",
    generate_thumbnails=True
)

# Get PDF info
info = pdf_service.get_pdf_info("report.pdf")
print(f"Pages: {info['pages']}, Size: {info['size_mb']:.2f} MB")
```

### Send Emails

```python
import email_service_facade

# Send PDFs to recipients
results = email_service_facade.send_pdfs(
    pdf_files=["page_1.pdf", "page_2.pdf"],
    recipients=["user1@company.com", "user2@company.com"],
    subject="Monthly Report",
    body="Please find attached your report."
)

print(f"Sent: {len(results['sent'])}")
print(f"Failed: {len(results['failed'])}")
```

## Complete Workflow

```python
import powerbi
import pdf_service
import email_service_facade

# 1. Export report
pdf_path = powerbi.export_report(
    "https://app.powerbi.com/groups/workspace/reports/report-id"
)

# 2. Split PDF
pdf_files, _ = pdf_service.split_pdf(pdf_path)

# 3. Send first 3 pages
results = email_service_facade.send_pdfs(
    pdf_files[:3],
    ["manager@company.com"],
    "Report Summary",
    "Key pages from today's report"
)
```

## Advanced Usage

### Custom Authentication

```python
from auth.powerbi_auth import PowerBIAuth
from api.powerbi_client import PowerBIClient

# Authenticate
auth = PowerBIAuth("user@company.com", "password")
token = auth.get_token_device_code()  # For MFA

# Use API client directly
client = PowerBIClient(token)
reports = client.get_reports()

for report in reports:
    print(f"{report['name']}: {report['webUrl']}")
```

### Custom PDF Processing

```python
from pdf.splitter import PDFSplitter
from pdf.thumbnail_generator import ThumbnailGenerator

# Split PDF
splitter = PDFSplitter("report.pdf", "output/")
pdf_files = splitter.split(prefix="custom_prefix")

# Generate thumbnails with custom size
generator = ThumbnailGenerator(size=(300, 400), dpi=200)
thumbnails = generator.generate(pdf_files)
```

### Custom Email Service

```python
from email.smtp_client import SMTPClient
from email.email_service import EmailService

# Create SMTP client
smtp = SMTPClient(
    email_address="sender@company.com",
    email_password="password",
    smtp_server="smtp.office365.com",
    smtp_port=587
)

# Create email service
service = EmailService(smtp)

# Send emails
results = service.send_pdfs(
    pdf_files=["report.pdf"],
    recipients=["recipient@company.com"],
    subject="Report",
    body="Your report"
)

service.close()
```

## Scheduled Automation

Create `daily_automation.py`:

```python
#!/usr/bin/env python3
import powerbi
import pdf_service
import email_service_facade
import config
from datetime import datetime

def main():
    try:
        # Export report
        pdf_path = powerbi.export_report(config.POWERBI_REPORT_URL)
        
        # Split PDF
        pdf_files, _ = pdf_service.split_pdf(pdf_path)
        
        # Send emails
        email_service_facade.send_pdfs(
            pdf_files,
            config.DEFAULT_RECIPIENTS,
            f"Daily Report - {datetime.now().strftime('%Y-%m-%d')}",
            "Please find attached today's report."
        )
        
        print("✅ Daily report sent")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
```

Schedule with cron (Linux/Mac):
```bash
# Run daily at 8 AM
0 8 * * * cd /path/to/project && ./venv/bin/python daily_automation.py
```

## Testing

### Test Power BI Connection

```python
import powerbi

# List available reports
reports = powerbi.list_reports()
for report in reports:
    print(f"- {report['name']}")

# List workspaces
workspaces = powerbi.list_workspaces()
for ws in workspaces:
    print(f"- {ws['name']}")
```

### Test Email

```python
from email.smtp_client import SMTPClient
import config

smtp = SMTPClient(
    config.EMAIL_ADDRESS,
    config.EMAIL_PASSWORD,
    config.SMTP_SERVER,
    config.SMTP_PORT
)

smtp.send(
    to_addresses="test@company.com",
    subject="Test Email",
    body="Testing email configuration",
    attachments=None
)

smtp.close()
print("✅ Email sent")
```

## Error Handling

```python
import powerbi
from utils.logger import setup_logger

logger = setup_logger('my_app', 'logs/my_app.log')

try:
    pdf_path = powerbi.export_report("https://app.powerbi.com/...")
    logger.info(f"Success: {pdf_path}")
except Exception as e:
    logger.error(f"Failed: {e}", exc_info=True)
```
