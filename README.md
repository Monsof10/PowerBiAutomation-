# Power BI Automation System

A comprehensive Python application that automates Power BI report generation, PDF processing, and email distribution without requiring Power BI Premium subscription.

## 🌟 Features

- **🤖 Automated Power BI Interaction**: Uses Playwright to automate Power BI Service
- **📄 PDF Processing**: Splits exported reports into individual pages
- **🖼️ Visual Preview**: Streamlit interface with PDF thumbnails
- **📧 Email Distribution**: Send selected PDFs to multiple recipients
- **📊 Progress Tracking**: Real-time progress indicators for all operations
- **🔐 Secure Configuration**: Environment-based credential management

## 📋 Prerequisites

- Python 3.8 or higher
- Power BI account with access to reports
- Gmail account (or other SMTP email service)
- Poppler (for PDF to image conversion)

## 🚀 Installation

### 1. Clone or Download the Project

```bash
cd powerbiAutomation
```

### 2. Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright Browsers

```bash
playwright install chromium
```

### 5. Install Poppler (for PDF thumbnails)

**Windows:**
1. Download Poppler from: https://github.com/oschwartz10612/poppler-windows/releases
2. Extract to a folder (e.g., `C:\Program Files\poppler`)
3. Add the `bin` folder to your system PATH

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get update
sudo apt-get install poppler-utils
```

**Mac:**
```bash
brew install poppler
```

## ⚙️ Configuration

### 1. Create Environment File

Copy the example environment file and rename it:

```bash
# Linux/Mac
cp env.example .env

# Windows
copy env.example .env
```

### 2. Configure Your Credentials

Edit the `.env` file with your information:

```env
# Power BI Credentials
POWERBI_EMAIL=your.email@example.com
POWERBI_PASSWORD=your_password

# Power BI Report URL
POWERBI_REPORT_URL=https://app.powerbi.com/groups/workspace-id/reports/report-id

# Email Configuration (Gmail)
EMAIL_ADDRESS=your.email@gmail.com
EMAIL_PASSWORD=your_app_password_here

# Default Recipients
DEFAULT_RECIPIENTS=recipient1@example.com,recipient2@example.com

# Email Settings
DEFAULT_SUBJECT=Power BI Report - Last 30 Days
DEFAULT_BODY=Please find attached the Power BI report for the last 30 days.
```

### 3. Gmail App Password Setup

For Gmail, you need to use an App Password (not your regular password):

1. Enable 2-Factor Authentication on your Google account
2. Go to: https://myaccount.google.com/apppasswords
3. Create a new App Password for "Mail"
4. Use this 16-character password in your `.env` file

### 4. Get Your Power BI Report URL

1. Log into Power BI Service (app.powerbi.com)
2. Navigate to your report
3. Copy the URL from the browser address bar
4. Paste it in the `.env` file

## 🎯 Usage

### Running the Application

```bash
streamlit run main.py
```

The application will open in your default web browser (typically at http://localhost:8501)

### Application Workflow

1. **Start Automation**
   - Click "Start Automation" button
   - The system will:
     - Log into Power BI
     - Navigate to your report
     - Apply last 30 days filter
     - Export as PDF
     - Split PDF into pages

2. **Preview & Select PDFs**
   - View thumbnails of all pages
   - Select which pages to send
   - Download individual pages if needed

3. **Configure Email**
   - Add/edit recipient email addresses
   - Customize subject and body
   - Review before sending

4. **Send Emails**
   - Click "Send Emails"
   - Monitor progress
   - View success/failure summary

## 📁 Project Structure

```
powerbiAutomation/
├── main.py                    # Streamlit application
├── powerbi_automation.py      # Power BI automation logic
├── pdf_handler.py             # PDF splitting and processing
├── email_sender.py            # Email sending functionality
├── config.py                  # Configuration management
├── requirements.txt           # Python dependencies
├── env.example                # Environment variables template
├── .env                       # Your credentials (not in git)
├── .gitignore                 # Git ignore rules
├── downloads/                 # Temporary PDF storage
├── output/                    # Split PDFs storage
└── logs/                      # Application logs
```

## 🔧 Module Usage

### Power BI Automation (Standalone)

```python
from powerbi_automation import run_automation

# Run automation and get PDF path
pdf_path = run_automation(
    email="your.email@example.com",
    password="your_password",
    report_url="https://app.powerbi.com/...",
    apply_filter=True,
    headless=False
)
print(f"PDF saved to: {pdf_path}")
```

### PDF Handler (Standalone)

```python
from pdf_handler import split_pdf_file

# Split PDF into pages
split_pdfs, thumbnails = split_pdf_file(
    pdf_path="path/to/report.pdf",
    generate_thumbs=True
)

print(f"Split into {len(split_pdfs)} pages")
```

### Email Sender (Standalone)

```python
from email_sender import send_email_with_attachments

# Send email with attachments
send_email_with_attachments(
    to_addresses=["recipient@example.com"],
    subject="Power BI Report",
    body="Please find attached the report.",
    attachments=["path/to/file1.pdf", "path/to/file2.pdf"]
)
```

## 🐛 Troubleshooting

### Power BI Login Issues

**Problem:** Login fails or gets stuck

**Solutions:**
- Verify credentials in `.env` file
- Check if MFA (Multi-Factor Authentication) is enabled
  - If yes: Disable MFA temporarily OR manually complete MFA in the browser window
- Try running with `headless=False` to see what's happening
- Check internet connection

### PDF Export Issues

**Problem:** PDF export fails or times out

**Solutions:**
- Verify you have access to the report
- Check if report is too large (increase timeout in config.py)
- Ensure report has loaded completely before export
- Try exporting manually first to confirm permissions

### Email Sending Issues

**Problem:** Emails fail to send

**Solutions:**
- **Gmail:** Ensure you're using App Password, not regular password
- **Gmail:** Enable "Less secure app access" (not recommended) OR use App Password
- **Other providers:** Verify SMTP server and port settings
- Check recipient email addresses are valid
- Verify email credentials in `.env`

### PDF Thumbnail Issues

**Problem:** Thumbnails not generating

**Solutions:**
- Ensure Poppler is installed correctly
- Verify Poppler is in system PATH
- On Windows, manually specify Poppler path in `pdf_handler.py`:
  ```python
  images = convert_from_path(str(pdf_path), dpi=dpi, 
                            poppler_path=r'C:\Program Files\poppler\bin')
  ```

### Dependencies Issues

**Problem:** Import errors or missing modules

**Solutions:**
```bash
# Reinstall all dependencies
pip install -r requirements.txt --upgrade

# Install playwright browsers
playwright install chromium

# Check if virtual environment is activated
```

## 📝 Logging

The application creates detailed logs in the `logs/` folder:

- `automation.log` - Main application log
- `email_activity.log` - Email sending history

Check these logs for detailed error messages and debugging information.

## 🔒 Security Notes

- **Never commit your `.env` file** to version control (it's in `.gitignore`)
- Use App Passwords for email, not your main password
- Regularly rotate your credentials
- Be cautious with report URLs that may contain sensitive IDs
- Review recipient lists before sending emails

## 🚧 Limitations

- **No MFA Support:** Multi-factor authentication requires manual intervention
- **Report-Specific Filters:** Date filter automation may need customization for your specific report
- **Single Report:** Designed for one report at a time
- **No Premium Features:** Does not use Power BI Premium APIs (uses UI automation instead)

## 🔄 Customization

### Changing Date Filter

Edit `powerbi_automation.py`, method `apply_date_filter()`:

```python
def apply_date_filter(self, filter_option="Last 7 days"):  # Change default
    # Customize based on your report's filter structure
    ...
```

### Custom SMTP Settings

For email providers other than Gmail, update `.env`:

```env
SMTP_SERVER=smtp.office365.com  # For Outlook
SMTP_PORT=587
```

### Headless Browser

To run browser in background, update `.env`:

```env
HEADLESS_MODE=True
```

## 📚 Additional Resources

- [Power BI Documentation](https://docs.microsoft.com/en-us/power-bi/)
- [Playwright Documentation](https://playwright.dev/python/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Gmail App Passwords](https://support.google.com/accounts/answer/185833)

## 🤝 Contributing

Feel free to fork, modify, and improve this project for your needs!

## ⚠️ Disclaimer

This tool automates browser interactions with Power BI Service. Use responsibly and in accordance with your organization's policies and Microsoft's terms of service.

## 📄 License

This project is provided as-is for educational and automation purposes.

---

**Built with ❤️ using Python, Streamlit, and Playwright**

