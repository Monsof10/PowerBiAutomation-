# Power BI Automation System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Clean Code](https://img.shields.io/badge/Code-Clean%20%26%20Modular-success)](https://github.com/highMorHealth/powerbiAutomation)

Automate Power BI report generation, PDF processing, and email distribution using clean code principles and modular architecture.

## Features

- **Power BI REST API**: Official Microsoft API for reliable report export
- **Modular Design**: Each file ~60 lines, single responsibility
- **Clean Code**: Follows NASA coding standards
- **PDF Processing**: Split reports with thumbnail generation
- **Email Distribution**: Send selected pages to multiple recipients
- **Web Interface**: Streamlit UI with progress tracking

## Quick Start

### Installation

```bash
# Clone and setup
git clone https://github.com/highMorHealth/powerbiAutomation.git
cd powerbiAutomation

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Configuration

```bash
# Copy template
cp env.example .env

# Edit with your credentials
nano .env
```

Required settings:
```env
POWERBI_EMAIL=your.email@company.com
POWERBI_PASSWORD=your_password
POWERBI_REPORT_URL=https://app.powerbi.com/groups/workspace/reports/report

EMAIL_ADDRESS=your.email@company.com
EMAIL_PASSWORD=your_password
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
```

### Run

```bash
streamlit run app.py
```

## Architecture

### Clean Code Structure

```
powerbiAutomation/
├── app.py                     # Main UI (75 lines)
├── config.py                  # Configuration (45 lines)
├── powerbi.py                 # Power BI facade (60 lines)
├── pdf_service.py             # PDF facade (45 lines)
├── email_service_facade.py    # Email facade (45 lines)
│
├── auth/                      # Authentication (66 lines)
│   ├── powerbi_auth.py
│   └── __init__.py
│
├── api/                       # Power BI API (143 lines)
│   ├── powerbi_client.py
│   ├── report_exporter.py
│   └── __init__.py
│
├── pdf/                       # PDF processing (143 lines)
│   ├── splitter.py
│   ├── thumbnail_generator.py
│   └── __init__.py
│
├── email/                     # Email system (133 lines)
│   ├── smtp_client.py
│   ├── email_service.py
│   └── __init__.py
│
└── utils/                     # Utilities (53 lines)
    ├── logger.py
    └── __init__.py
```

**Total: ~914 lines** (vs 1500+ in monolithic version)

### Design Principles

✅ **Single Responsibility** - Each module has one clear purpose
✅ **Clean Code** - Functions under 30 lines, files under 80 lines
✅ **DRY** - No code duplication
✅ **Separation of Concerns** - Clear boundaries between layers
✅ **Testability** - Easy to test individual components
✅ **Maintainability** - Easy to understand and modify

## Usage

### Simple API

```python
# Export report
import powerbi
pdf_path = powerbi.export_report("https://app.powerbi.com/...")

# Process PDF
import pdf_service
pdfs, thumbs = pdf_service.split_pdf(pdf_path)

# Send emails
import email_service_facade
email_service_facade.send_pdfs(pdfs, ["user@company.com"], "Report", "Here's your report")
```

### Authentication

**Password Auth** (Simple):
- Set credentials in `.env`
- Works for accounts without MFA

**Device Code** (For MFA):
- Automatic fallback if password fails
- Follow on-screen instructions

## Testing

```bash
# Verify setup
python test_setup.py

# Check all imports and configuration
```

## Email Providers

**Outlook/Office 365:**
```env
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
```

**Gmail:**
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
# Use App Password from https://myaccount.google.com/apppasswords
```

## Troubleshooting

### Import Errors
```bash
pip install -r requirements.txt --upgrade
```

### Authentication Fails
- Verify credentials in `.env`
- For MFA accounts, device code flow will activate automatically

### Email Fails
- Use App Password for Gmail
- Verify SMTP settings for your provider

## Development

### Code Standards

- **NASA Coding Standards** - Reliability and safety
- **Clean Code Principles** - Readability and maintainability
- **PEP 8** - Python style guide
- **Type Hints** - Better IDE support
- **Docstrings** - All public functions documented

### Adding Features

1. Fork repository
2. Create feature branch
3. Follow existing module structure (~60 lines per file)
4. Add tests
5. Submit pull request

## Project Stats

- **Total Lines**: ~914 (Python code)
- **Modules**: 13 focused modules
- **Packages**: 5 (auth, api, pdf, email, utils)
- **Avg File Size**: 60-70 lines
- **Max File Size**: 79 lines



## Support

- **Issues**: GitHub Issues
- **Setup Problems**: Run `python test_setup.py`
- **Logs**: Check `logs/automation.log`

---

**Built with clean code principles for maintainability and reliability**

**Version:** 2.0.0 (Refactored)
**Status:** Production Ready
**Last Updated:** October 2025
