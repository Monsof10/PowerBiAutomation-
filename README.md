# PDF Monthly Automation - WIP

This is a work-in-progress package that provides a monthly automation:
- Download a PDF from a URL (or via Playwright for JS/login flows)
- Remove pages from the PDF
- Email the modified PDF via Outlook (SMTP)
- Logs stored in OUTPUT_DIR/automation.log

## Quick start
1. Copy `.env.example` to `.env` and fill values.
2. Install requirements:
   ```
   pip install -r requirements.txt
   ```
   If using Playwright, run:
   ```
   playwright install
   ```
3. Test run:
   ```
   python3 automation.py
   ```
4. If it works, schedule with cron/systemd or deploy to a server.

## Outlook SMTP notes
- For Office 365 / Outlook, use `smtp.office365.com` port `587` with STARTTLS.
- It's recommended to use an app password or a service account for automation.

## Playwright notes
- If the PDF requires logging into Power BI and exporting via UI, set `USE_PLAYWRIGHT=true` and update the selector and login steps in `playwright_download.py`.
- Playwright examples are placeholders—adjust selectors to match the actual page.

## Security
- Do NOT commit `.env` to source control.
- Use environment-based secrets or your cloud provider's secret store when deploying.

## Files
- automation.py: Main script that orchestrates the download, PDF modification, and emailing.
- pdf_utils.py: Utility functions for PDF manipulation (remove, extract, rotate pages).
- playwright_download.py: Handles browser automation for login-required downloads (e.g., Power BI).
- streamlit_dashboard.py: Web dashboard to trigger runs and view logs.
- requirements.txt: Python dependencies.
- Dockerfile: For containerizing the app.
- .env.example: Template for configuration.

## How It Works

### 1. Configuration
The script uses environment variables from a `.env` file for all sensitive and customizable settings. Copy `.env.example` to `.env` and fill in:
- `DOWNLOAD_URL`: Direct URL to the PDF (if not using Playwright).
- `USE_PLAYWRIGHT`: Set to `true` for browser automation (e.g., login to Power BI).
- Playwright-specific: `PLAYWRIGHT_LOGIN_URL`, `PLAYWRIGHT_USERNAME`, `PLAYWRIGHT_PASSWORD`, `PLAYWRIGHT_DOWNLOAD_SELECTOR` (adjust selectors for your site).
- `OUTPUT_DIR`: Folder for logs and downloaded PDFs (default: `/tmp/pdf_automation` on Unix, or customize for Windows).
- `REMOVE_PAGES`: Comma-separated 1-based page numbers to remove (e.g., "1,3" removes first and third pages).
- SMTP settings: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `EMAIL_FROM`, `EMAIL_TO`, `EMAIL_SUBJECT`, `EMAIL_BODY`.

**Note**: Page numbers are 1-based for user-friendliness (e.g., "1" is the first page).

### 2. Running the Script
Execute `python automation.py` to run once. It performs:
- **Download**: 
  - If `USE_PLAYWRIGHT=false` (default): Downloads via `requests.get(DOWNLOAD_URL)`.
  - If `true`: Launches Playwright browser, navigates to login URL, fills credentials, handles "Stay signed in?" prompt, loads dashboard, clicks Export > PDF, and waits for download (with timeouts and screenshots for debugging).
- **PDF Modification**: Uses PyPDF2 to remove specified pages (0-based internally). Saves as `modified_report_{timestamp}.pdf` if changes made; otherwise uses raw file.
- **Email**: Attaches the (modified) PDF and sends via SMTP (Outlook/Office 365). Uses STARTTLS for security.
- **Logging**: All steps logged to `OUTPUT_DIR/automation.log` with timestamps.

### 3. Streamlit Dashboard
Run `streamlit run streamlit_dashboard.py` for a web UI:
- Button to trigger `automation.py`.
- Displays last 10k characters of the log file.

### 4. Scheduling
- **Cron** (Linux/Mac): Use `cron_example.txt` as template (e.g., monthly on 1st).
- **Systemd** (Linux): Use `systemd_example.txt` for timer-based runs.
- **Windows**: Use Task Scheduler with a batch file calling `python automation.py`.

### 5. Docker Deployment
The project includes a `Dockerfile` and `docker-compose.yml` for easy containerization.

#### Using Docker Compose (Recommended)
1. Ensure you have a `.env` file with your configuration.
2. Run the container with cron scheduling:
   ```bash
   docker-compose up -d
   ```
   This will build the image and start the container with cron running automatically on the 1st of each month at 6 AM.

3. For manual testing:
   ```bash
   docker-compose run --rm automation python automation.py
   ```

#### Using Docker directly
```bash
# Build the image
docker build -t pdf-monthly-automation .

# Run with cron (scheduled execution)
docker run -d --name pdf-automation --env-file .env \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/emailtemp:/app/emailtemp \
  pdf-monthly-automation

# Run manually for testing
docker run --rm --env-file .env \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/emailtemp:/app/emailtemp \
  pdf-monthly-automation python automation.py
```

The Dockerfile installs Playwright with Chromium browser and sets up cron to run the automation on the 1st of each month at 6 AM UTC.


### 6. Server Deployment

For production deployment on a server, use Docker Compose for easy management:

1. **Prepare the server:**
   - Install Docker and Docker Compose
   - Clone your repository to the server
   - Create a `.env` file with your production configuration

2. **Deploy:**
   ```bash
   # Build and start the container
   docker-compose up -d

   # Check logs
   docker-compose logs -f automation

   # Stop the container
   docker-compose down
   ```

3. **Monitoring:**
   - Logs are stored in `./logs/cron.log` and `./logs/automation.log`
   - The container runs cron automatically, executing the script on the 1st of each month at 6 AM UTC
   - For different timezones, adjust the cron expression in the Dockerfile

4. **Updates:**
   ```bash
   # Pull latest changes
   git pull

   # Rebuild and restart
   docker-compose up -d --build
   ```

**Note:** The cron runs in UTC time. If you need a different timezone, modify the cron line in the Dockerfile (e.g., `0 6 1 * * root TZ=America/New_York cd /app && python automation.py >> /app/logs/cron.log 2>&1`).

### 8. Troubleshooting
- **Playwright Failures**: Check screenshots (e.g., `after_pdf_click.png`) for UI changes. Update selectors in `playwright_download.py`. Ensure `playwright install` ran.
- **PDF Errors**: Verify page numbers (1-based). Test with `pdf_utils.py` functions directly.
- **SMTP Issues**: Common error 535 means SMTP auth disabled in tenant—enable in Microsoft 365 Admin Center (https://aka.ms/smtp_auth_disabled). Use app passwords if 2FA enabled. Alternative: Switch to Gmail SMTP or Microsoft Graph API.
- **Logs**: Always check `automation.log` for details.
- **Windows Paths**: Use raw strings (r"path") for OUTPUT_DIR to handle backslashes.

For customizations, edit the respective files. Contributions welcome!
