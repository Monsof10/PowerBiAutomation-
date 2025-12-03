# Architecture & Project Overview

## Overview

This project is a **Power BI Monthly Report Automation System** that downloads facility-group-specific PDF reports, embeds inline logos in HTML emails, and sends them automatically. The system uses Playwright for web automation and SMTP for email delivery.

## Core Components

### Main Entry Points

**automation.py** (~500 lines)
- Orchestrates the entire workflow for 12 facility groups (1-12)
- Calls Playwright downloader for each group
- Sends emails with inline CID logos (highmor.png, omcc.png)
- Handles two email templates:
  - `EMAIL_BODY`: Standard email with PDF attachment (for groups with activations)
  - `EMAIL_BODY_NO_ACTIVATIONS`: Email without PDF (for groups with no activations or blank EFF selection)
- Special logic for group 6:
  - If EFF → "(Blank)" is selected, treats as 0 activations and sends no-activations email
  - Skips Facility Filter click and PDF export for blank selection

**playwright_download.py** (~440 lines)
- Uses Playwright for web automation and PDF export
- Logs in to Power BI using MSAL credentials
- Sets date filters (start/end of previous month)
- Handles 12 facility groups with ending facility selection
- **Group 6 Special Logic:**
  - Detects "(Blank)" selection in EFF filter
  - Early return with `has_activations=False` to skip Activations report and export
  - Returns `(output_path, False, 0)` immediately
- Clicks "Activations report101" button and extracts total count (for non-blank cases)
- Exports PDF via Power BI export functionality

### Supporting Modules

**config.py** (~100 lines)
- Loads environment variables from `.env`
- Email configuration (SMTP, FROM, TO, SUBJECT)
- HTML email templates with CID image references
- Inline image paths and CIDs (logo1, logo2)
- Output directory and PDF page removal settings

**pdf_utils.py**
- PDF manipulation utilities (page removal, etc.)

**email_service_facade.py** & **send_email_with_inline_images.py**
- Email sending with multipart MIME structure
- Inline image attachment via Content-ID (CID)
- Support for both attachment and no-attachment modes

## System Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│         automation.py (Entry Point)      │  ~500 lines
│  - Orchestrates 12 facility groups       │
│  - Loops: download → process → email    │
└──────────────────────────────────────────┬──────────────────────────────────┘
             │
┌──────────────────────────────────────────┴──────────────────────────────────┐
│    playwright_download.py (Download)     │  ~440 lines
│  - Web automation via Playwright        │
│  - Power BI login & PDF export          │
│  - Group 6 special: (Blank) detection  │
└──────────────────────────────────────────┬──────────────────────────────────┘
             │
┌──────────────────────────────────────────┴──────────────────────────────────┐
│      Email Sending Functions             │  ~200 lines
│  - send_email_with_attachment()         │
│  - send_email_without_attachment()      │
│  - Inline CID logo embedding            │
└──────────────────────────────────────────┬──────────────────────────────────┘
             │
┌──────────────────────────────────────────┴──────────────────────────────────┐
│      Configuration & Utilities           │  ~100 lines
│  - config.py (env vars, templates)      │
│  - pdf_utils.py (PDF manipulation)      │
│  - utils/logger.py (logging setup)      │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Key Features

### Email System with Inline Logos

**Inline Image Embedding (CID References)**
- Images stored in `emailtemp/` folder (IGNORED in git):
  - `highmor.png` (120×60px header logo)
  - `omcc.png` (170×170px report logo)
- Referenced in HTML templates via `cid:logo1` and `cid:logo2`
- Attached as MIME multipart/related images
- Robust across email clients (Gmail, Outlook, etc.)

**Email Templates**
1. **EMAIL_BODY** (activations present)
   - Includes PDF attachment
   - Full report message
   - Both logos displayed

2. **EMAIL_BODY_NO_ACTIVATIONS** (no activations or blank)
   - No PDF attachment
   - "No accepted patients" message
   - Both logos displayed

### Facility Group Processing

**Standard Groups (1-5, 7-12)**
- Click EFF filter
- Select ending facilities from ENDING_FACILITIES_GROUPS config
- Click Facility Filter
- Select ending facilities again
- Click Activations report101, extract count
- Export PDF if count > 0
- Send email (with or without attachment)

**Group 6 (Special Case)**
- Click EFF filter
- **Detect "(Blank)" option:**
  - If found: set `blank_selected = True`
  - If clicked: confirm by checking text presence
- **If blank selected:**
  - Skip Facility Filter entirely
  - Skip Activations report click & count extraction
  - Skip PDF export
  - Return immediately: `has_activations=False`
- Send no-activations email without PDF

## Data Flow

```
1. automation.py starts
   ↓
2. Loop through groups 1-12
   ↓
3. For each group:
   a. Call download_with_playwright(..., group_num)
      ↓
   b. Playwright script:
      - Login to Power BI
      - Set dates (previous month)
      - Click EFF filter
      - If group 6: detect "(Blank)" → return (path, False, 0)
      - Select facilities (EFF & Facility Filter)
      - Click Activations report101, extract count
      - Export PDF
      - Return (path, has_activations, count)
      ↓
   c. Back in automation.py:
      - If has_activations=False:
        send_email_without_attachment(EMAIL_BODY_NO_ACTIVATIONS)
      - Else:
        modify PDF (remove pages if configured)
        send_email_with_attachment(EMAIL_BODY)
      ↓
4. Move to next group
```

## Recent Changes (v2.0)

### Email Improvements
- ✅ Integrated inline CID logos (highmor.png, omcc.png)
- ✅ Two email templates (with/without activations)
- ✅ Removed borders and styled images for clean rendering
- ✅ Multipart MIME structure for robust email client support

### Playwright Enhancements
- ✅ Group 6 special-case logic: detect and handle "(Blank)" in EFF
- ✅ Early return when blank selected (skip activations & export)
- ✅ Facility Filter conditional: skip if EFF was blank
- ✅ Cleaned up redundant code and debug blocks

### Configuration
- ✅ Environment variables for SMTP, Power BI login, facility groups
- ✅ EMAIL_BODY and EMAIL_BODY_NO_ACTIVATIONS templates in config.py
- ✅ Inline image paths configurable

## File Structure

```
.
├── automation.py                    # Main orchestrator
├── playwright_download.py           # Playwright automation & PDF download
├── config.py                        # Configuration & templates
├── pdf_utils.py                     # PDF manipulation utilities
├── email_service_facade.py          # Email sending facade
├── send_email_with_inline_images.py # Inline image email helper
├── generate_test_eml.py             # Test EML generator
├── requirements.txt                 # Python dependencies
├── .env                             # Environment variables (IGNORED)
├── .gitignore                       # Git ignore rules
├── ARCHITECTURE.md                  # This file
├── emailtemp/                       # Email images (IGNORED)
│   ├── highmor.png
│   └── omcc.png
├── output/                          # Generated files (IGNORED)
├── downloads/                       # Temp downloads (IGNORED)
├── logs/                            # Log files (IGNORED)
├── auth/                            # Auth modules
├── api/                             # API modules
├── pdf/                             # PDF modules
└── utils/                           # Utility modules
```

## Requirements

```
playwright>=1.40.0
python-dotenv>=1.0.0
requests>=2.31.0
python-dateutil>=2.8.2
```

## Setup & Run

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   python playwright_download.py  # Optional: download browser
   ```

2. **Configure environment (.env):**
   ```
   PLAYWRIGHT_LOGIN_URL=your_power_bi_url
   PLAYWRIGHT_USERNAME=your_email
   PLAYWRIGHT_PASSWORD=your_password
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your_email@gmail.com
   SMTP_PASS=your_app_password
   EMAIL_FROM=your_email@gmail.com
   EMAIL_TO=recipient@company.com
   USE_PLAYWRIGHT=true
   ```

3. **Run automation:**
   ```bash
   python automation.py
   ```

## Git Ignore

The following are excluded from version control (in `.gitignore`):
- `.env` - Contains sensitive credentials
- `emailtemp/` - Large image files (to be added locally)
- `output/`, `downloads/`, `logs/` - Generated during runtime
- `__pycache__/`, `*.egg-info/` - Python build artifacts

---

**Last Updated:** December 3, 2025  
**Version:** 2.0  
**Status:** Production-Ready

