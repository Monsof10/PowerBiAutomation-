# System Architecture

## Overview

The Power BI Automation System consists of four main modules that work together to provide a complete automation solution:

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Web UI                        │
│                       (main.py)                             │
└────────────┬────────────┬────────────┬─────────────────────┘
             │            │            │
             ▼            ▼            ▼
    ┌────────────┐  ┌──────────┐  ┌─────────────┐
    │  Power BI  │  │   PDF    │  │    Email    │
    │ Automation │  │  Handler │  │   Sender    │
    └────────────┘  └──────────┘  └─────────────┘
         │               │               │
         ▼               ▼               ▼
    ┌─────────┐    ┌─────────┐    ┌──────────┐
    │Playwright│   │  pypdf  │    │ yagmail  │
    └─────────┘    └─────────┘    └──────────┘
```

## Module Breakdown

### 1. Main Application (`main.py`)

**Purpose:** Streamlit-based web interface for user interaction

**Key Features:**
- Progress tracking with visual indicators
- PDF preview with thumbnails
- Email configuration interface
- Session state management
- Error handling and user feedback

**User Flow:**
```
1. Start Automation → 2. View PDFs → 3. Select Pages → 4. Send Emails
```

### 2. Power BI Automation (`powerbi_automation.py`)

**Purpose:** Browser automation for Power BI Service

**Technology:** Playwright (Chromium browser)

**Process Flow:**
```
1. Launch Browser
2. Navigate to Power BI
3. Enter Credentials
4. Handle Authentication
5. Load Report
6. Apply Filters
7. Export PDF
8. Download File
9. Close Browser
```

**Key Methods:**
- `start_browser()` - Initialize Playwright
- `login()` - Authenticate with Power BI
- `navigate_to_report()` - Load specific report
- `apply_date_filter()` - Apply date filtering
- `export_to_pdf()` - Export and download PDF
- `run_full_automation()` - Execute complete workflow

### 3. PDF Handler (`pdf_handler.py`)

**Purpose:** PDF processing and manipulation

**Technology:** pypdf, pdf2image, Pillow

**Process Flow:**
```
1. Read Source PDF
2. Extract Metadata
3. Split into Pages
4. Generate Individual PDFs
5. Create Thumbnails (optional)
6. Save to Output Folder
```

**Key Methods:**
- `get_page_count()` - Count PDF pages
- `split_pdf()` - Split into individual pages
- `generate_thumbnails()` - Create preview images
- `get_pdf_info()` - Extract metadata
- `cleanup_all()` - Remove temporary files

### 4. Email Sender (`email_sender.py`)

**Purpose:** Email distribution with attachments

**Technology:** yagmail (Gmail SMTP wrapper)

**Process Flow:**
```
1. Initialize SMTP Connection
2. Prepare Email Content
3. Attach PDF Files
4. Send to Recipients
5. Track Success/Failure
6. Log Activity
7. Close Connection
```

**Key Methods:**
- `send_email()` - Send single email
- `send_multiple_emails()` - Batch sending
- `send_pdf_to_recipients()` - Specialized PDF sending

### 5. Configuration (`config.py`)

**Purpose:** Centralized configuration management

**Features:**
- Environment variable loading
- Path management
- Default settings
- Folder creation
- Logging configuration

## Data Flow

### Complete Automation Workflow

```
User Action (Start)
      ↓
[Streamlit UI]
      ↓
PowerBIAutomation.run_full_automation()
      ↓
1. Browser Launch (Playwright)
2. Login to Power BI
3. Navigate & Filter
4. Export PDF
      ↓
[downloads/powerbi_report.pdf]
      ↓
PDFHandler.split_pdf()
      ↓
[output/report_page_1.pdf]
[output/report_page_2.pdf]
[output/report_page_N.pdf]
      ↓
PDFHandler.generate_thumbnails()
      ↓
[output/report_page_1.png]
[output/report_page_2.png]
      ↓
[Streamlit Preview UI]
      ↓
User Selection
      ↓
EmailSender.send_email()
      ↓
[Email Delivery]
      ↓
Success/Failure Report
```

## File System Structure

```
powerbiAutomation/
│
├── Core Application Files
│   ├── main.py                    # Streamlit web interface
│   ├── powerbi_automation.py      # Browser automation
│   ├── pdf_handler.py             # PDF processing
│   ├── email_sender.py            # Email functionality
│   └── config.py                  # Configuration manager
│
├── Configuration Files
│   ├── .env                       # Credentials (user-created)
│   ├── env.example                # Template
│   └── .gitignore                 # Git exclusions
│
├── Documentation
│   ├── README.md                  # Main documentation
│   ├── QUICKSTART.md              # Quick start guide
│   └── ARCHITECTURE.md            # This file
│
├── Setup Scripts
│   ├── setup.sh                   # Linux/Mac setup
│   ├── setup.bat                  # Windows setup
│   └── test_setup.py              # Verification script
│
├── Dependencies
│   └── requirements.txt           # Python packages
│
└── Runtime Directories
    ├── downloads/                 # Temporary PDF storage
    ├── output/                    # Split PDFs
    └── logs/                      # Application logs
```

## Security Architecture

### Credential Management

```
.env file (local only)
    ↓
Environment Variables
    ↓
config.py (loads at runtime)
    ↓
Module Initialization
```

**Security Features:**
- Environment-based configuration
- .env file excluded from git
- No hardcoded credentials
- App passwords for email
- Secure SMTP connections

### Data Flow Security

1. **Power BI:** Browser automation (no API keys needed)
2. **Email:** TLS/SSL encrypted SMTP
3. **Files:** Local storage only
4. **Logs:** Local, rotatable logs

## Technology Stack

### Core Technologies
- **Python 3.8+** - Main programming language
- **Streamlit** - Web interface framework
- **Playwright** - Browser automation
- **pypdf** - PDF manipulation
- **yagmail** - Email sending

### Supporting Libraries
- **python-dotenv** - Environment configuration
- **pdf2image** - PDF to image conversion
- **Pillow** - Image processing
- **pandas** - Data management (optional)

### External Dependencies
- **Chromium** - Browser for automation
- **Poppler** - PDF rendering utilities
- **SMTP Server** - Email delivery

## Scalability & Performance

### Current Limitations
- Single report at a time
- Sequential processing
- Local file storage
- Manual initiation

### Performance Characteristics
- Browser automation: ~30-60 seconds
- PDF splitting: ~1 second per page
- Email sending: ~2-5 seconds per recipient
- Total time: ~2-5 minutes for typical workflow

### Potential Improvements
1. Batch processing multiple reports
2. Parallel email sending
3. Cloud storage integration
4. Scheduled automation
5. API-based Power BI access (requires Premium)

## Error Handling

### Error Recovery Points

```
[Start] → Browser Launch
         ↓ [Failure: Retry/Manual]
      Login
         ↓ [Failure: Check credentials]
      Navigation
         ↓ [Failure: Check URL/permissions]
      Export
         ↓ [Failure: Timeout/retry]
      PDF Split
         ↓ [Failure: Check file]
      Email Send
         ↓ [Failure: Retry individual]
[Complete]
```

### Error Handling Strategies
1. **Try-Catch Blocks** - All critical operations
2. **Logging** - Detailed error logging
3. **User Feedback** - Clear error messages
4. **Graceful Degradation** - Continue when possible
5. **Cleanup** - Always close resources

## Extension Points

### Easy Customizations
1. **Date Filters** - Modify `apply_date_filter()`
2. **Email Templates** - Customize in config
3. **PDF Naming** - Change prefix in config
4. **UI Themes** - Streamlit theming
5. **Logging Levels** - Adjust in config

### Advanced Extensions
1. **Multiple Reports** - Add report loop
2. **Scheduled Runs** - Add cron/scheduler
3. **Database Integration** - Track history
4. **Report Distribution Lists** - CSV/DB recipients
5. **Custom Filters** - Dynamic filter system

## Monitoring & Logging

### Log Files
- `logs/automation.log` - Main application log
- `logs/email_activity.log` - Email sending history

### Logged Information
- Timestamps
- Operation status
- Error messages
- Stack traces
- User actions
- Email deliveries

## Deployment Considerations

### Development
```bash
python main.py  # Direct Python
streamlit run main.py  # Streamlit dev server
```

### Production
- Use process manager (systemd, supervisor)
- Enable headless browser mode
- Set up log rotation
- Configure firewall (if remote access)
- Use reverse proxy (nginx) for Streamlit

### Environment Variables
- Development: `.env` file
- Production: System environment or secrets manager

## Maintenance

### Regular Tasks
1. Update dependencies: `pip install -r requirements.txt --upgrade`
2. Check logs: `tail -f logs/automation.log`
3. Clean temp files: Remove old files from `downloads/` and `output/`
4. Rotate credentials: Update `.env` periodically

### Troubleshooting
1. Check logs first
2. Run `python test_setup.py`
3. Test modules individually
4. Verify credentials
5. Check network connectivity

---

**Last Updated:** 2025-10-28
**Version:** 1.0.0

