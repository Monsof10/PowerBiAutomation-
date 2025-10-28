# Troubleshooting Guide

## Quick Diagnostics

### Run Setup Verification
```bash
python test_setup.py
```

This will check:
- ✅ All packages installed
- ✅ Playwright browser ready
- ✅ Configuration complete
- ✅ Folders exist
- ✅ Poppler available

---

## Common Issues & Solutions

### 1. Power BI Login Issues

#### Problem: "Login timeout" or "Login failed"

**Possible Causes:**
- Wrong credentials
- Multi-Factor Authentication (MFA) enabled
- Network issues
- Browser automation blocked

**Solutions:**

1. **Verify Credentials**
   ```bash
   # Check your .env file
   cat .env | grep POWERBI
   ```
   - Ensure email and password are correct
   - No extra spaces or quotes

2. **Disable Headless Mode** (to see what's happening)
   ```env
   # In .env file
   HEADLESS_MODE=False
   ```
   - Run automation again
   - Watch the browser window
   - Complete MFA manually if prompted

3. **Handle MFA**
   - Option A: Disable MFA temporarily (not recommended)
   - Option B: Run with headless=False and complete MFA manually
   - Option C: Use organization-specific login if available

4. **Check Network**
   ```bash
   # Test Power BI access
   curl -I https://app.powerbi.com
   ```

---

### 2. Report Access Issues

#### Problem: "Report loading timeout" or "Access denied"

**Solutions:**

1. **Verify Report URL**
   - Log into Power BI manually
   - Navigate to your report
   - Copy exact URL from browser
   - Update in .env file

2. **Check Permissions**
   - Ensure you have view access to the report
   - Check workspace permissions
   - Try opening report manually first

3. **Report Format**
   ```
   Correct: https://app.powerbi.com/groups/abc123.../reports/def456...
   Wrong: https://app.powerbi.com/home
   ```

---

### 3. PDF Export Issues

#### Problem: "PDF export failed" or "Download timeout"

**Solutions:**

1. **Increase Timeout**
   ```python
   # In config.py
   DOWNLOAD_TIMEOUT = 300  # Increase from 120 to 300 seconds
   ```

2. **Manual Test**
   - Open report manually
   - Try File → Export → PDF
   - If it fails manually, automation will fail too

3. **Check Browser Downloads**
   - Look in `downloads/` folder
   - Check browser's default download location
   - Ensure download isn't blocked

4. **Report Too Large**
   - Simplify report visuals
   - Reduce date range
   - Split into multiple reports

---

### 4. Email Sending Issues

#### Problem: "Email sending failed" or "Authentication error"

**For Gmail Users:**

1. **Use App Password** (REQUIRED)
   ```
   DO NOT use your regular Gmail password!
   ```
   
   Steps:
   1. Enable 2-Factor Authentication
   2. Go to: https://myaccount.google.com/apppasswords
   3. Generate App Password
   4. Use 16-character password in .env

2. **Enable Less Secure Apps** (NOT RECOMMENDED)
   - Google may block this
   - App Password is better

3. **Check Account Security**
   - Check Google account security page
   - Look for blocked sign-in attempts
   - Allow access if blocked

**For Other Email Providers:**

1. **Update SMTP Settings**
   ```env
   # Outlook
   SMTP_SERVER=smtp.office365.com
   SMTP_PORT=587
   
   # Yahoo
   SMTP_SERVER=smtp.mail.yahoo.com
   SMTP_PORT=587
   
   # Custom
   SMTP_SERVER=smtp.yourdomain.com
   SMTP_PORT=587 or 465
   ```

2. **Test Email Credentials**
   ```python
   python email_sender.py recipient@example.com
   ```

**General Email Issues:**

1. **Invalid Recipients**
   - Check email addresses for typos
   - Ensure proper format: user@domain.com
   - No spaces or special characters

2. **Attachment Too Large**
   - Gmail limit: 25MB
   - Split large PDFs
   - Send fewer pages per email

3. **Firewall/Port Blocking**
   - Check if port 587 is open
   - Try port 465 (SSL)
   - Contact IT if on corporate network

---

### 5. PDF Processing Issues

#### Problem: "Error splitting PDF" or "Cannot read PDF"

**Solutions:**

1. **Verify PDF File**
   ```bash
   # Check if PDF exists
   ls -lh downloads/
   
   # Try opening manually
   xdg-open downloads/powerbi_report_*.pdf  # Linux
   open downloads/powerbi_report_*.pdf      # Mac
   start downloads\powerbi_report_*.pdf     # Windows
   ```

2. **PDF Corrupted**
   - Re-export from Power BI
   - Check PDF size (should be > 0 bytes)
   - Try opening in PDF reader

3. **Permissions Issue**
   - Check folder permissions
   - Ensure write access to output/
   ```bash
   chmod -R 755 output/  # Linux/Mac
   ```

---

### 6. Thumbnail Generation Issues

#### Problem: "Could not generate thumbnails" or "Poppler not found"

**Linux:**
```bash
# Install Poppler
sudo apt-get update
sudo apt-get install poppler-utils

# Verify installation
which pdftoppm
```

**Mac:**
```bash
# Install via Homebrew
brew install poppler

# Verify installation
which pdftoppm
```

**Windows:**

1. Download Poppler:
   https://github.com/oschwartz10612/poppler-windows/releases

2. Extract to: `C:\Program Files\poppler`

3. Add to PATH:
   - System Properties → Environment Variables
   - Add to PATH: `C:\Program Files\poppler\Library\bin`

4. Or specify in code:
   ```python
   # In pdf_handler.py, line ~60
   images = convert_from_path(
       str(pdf_path), 
       dpi=dpi,
       poppler_path=r'C:\Program Files\poppler\Library\bin'
   )
   ```

**Note:** Thumbnails are optional. The app will work without them.

---

### 7. Installation Issues

#### Problem: "Module not found" or "Import error"

**Solutions:**

1. **Reinstall Dependencies**
   ```bash
   # Activate virtual environment first
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   
   # Reinstall
   pip install -r requirements.txt --force-reinstall
   ```

2. **Install Playwright Browsers**
   ```bash
   playwright install chromium
   ```

3. **Check Python Version**
   ```bash
   python --version  # Should be 3.8+
   ```

4. **Virtual Environment Issues**
   ```bash
   # Delete and recreate
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

---

### 8. Streamlit Issues

#### Problem: "Streamlit won't start" or "Port already in use"

**Solutions:**

1. **Port in Use**
   ```bash
   # Use different port
   streamlit run main.py --server.port 8502
   
   # Or kill process using port 8501
   lsof -ti:8501 | xargs kill -9  # Linux/Mac
   ```

2. **Browser Doesn't Open**
   - Manually open: http://localhost:8501
   - Check firewall settings

3. **Streamlit Errors**
   ```bash
   # Clear cache
   streamlit cache clear
   
   # Update Streamlit
   pip install --upgrade streamlit
   ```

---

### 9. Performance Issues

#### Problem: "Automation is slow" or "Timeouts"

**Solutions:**

1. **Increase Timeouts**
   ```python
   # In config.py
   PAGE_LOAD_TIMEOUT = 60  # Increase
   DOWNLOAD_TIMEOUT = 300  # Increase
   ```

2. **Reduce Report Complexity**
   - Simplify visuals
   - Reduce data range
   - Remove unnecessary pages

3. **Network Speed**
   - Check internet connection
   - Use wired connection if possible
   - Avoid VPN if possible

---

### 10. Date Filter Issues

#### Problem: "Date filter not applied" or "Wrong data shown"

**Solutions:**

1. **Customize Filter Logic**
   The date filter automation is generic and may need customization:
   
   ```python
   # In powerbi_automation.py, method apply_date_filter()
   # Customize based on your report structure
   ```

2. **Manual Filtering**
   - Run with headless=False
   - Apply filter manually before export
   - Or skip filter automation:
     ```python
     automation.run_full_automation(apply_filter=False)
     ```

3. **Different Filter Names**
   - Your report might use different filter labels
   - Update filter text in `powerbi_automation.py`

---

## Debug Mode

### Enable Detailed Logging

```python
# In config.py
LOG_LEVEL = 'DEBUG'  # Change from 'INFO'
```

### Check Logs

```bash
# View main log
tail -f logs/automation.log

# View email log
tail -f logs/email_activity.log
```

### Screenshot on Error

Add to `powerbi_automation.py`:
```python
# In except blocks
self.page.screenshot(path='error_screenshot.png')
```

---

## Still Having Issues?

### Collect Diagnostic Information

1. **System Info**
   ```bash
   python --version
   pip list
   python test_setup.py
   ```

2. **Error Logs**
   ```bash
   cat logs/automation.log
   ```

3. **Configuration** (remove passwords)
   ```bash
   cat .env | sed 's/PASSWORD=.*/PASSWORD=***/'
   ```

### Test Modules Individually

```bash
# Test Power BI (with dummy credentials, will fail but show error)
python powerbi_automation.py

# Test PDF splitting (with sample PDF)
python pdf_handler.py sample.pdf

# Test email (with real credentials)
python email_sender.py recipient@example.com
```

---

## Get Help

### Check Documentation
- README.md - Full documentation
- QUICKSTART.md - Quick setup
- ARCHITECTURE.md - System design

### Common Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| "Import error" | Missing package | Run `pip install -r requirements.txt` |
| "Login timeout" | Can't log into Power BI | Check credentials, disable headless |
| "Email auth failed" | Wrong email password | Use App Password for Gmail |
| "PDF not found" | Export failed | Check report permissions, increase timeout |
| "Poppler not found" | Missing dependency | Install Poppler for thumbnails |

---

**Last Updated:** 2025-10-28

