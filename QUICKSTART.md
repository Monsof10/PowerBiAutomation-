# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

**Linux/Mac:**
```bash
./setup.sh
```

**Windows:**
```bash
setup.bat
```

**Or manually:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install packages
pip install -r requirements.txt
playwright install chromium
```

### Step 2: Configure Credentials

1. Copy `env.example` to `.env`:
   ```bash
   cp env.example .env  # Linux/Mac
   copy env.example .env  # Windows
   ```

2. Edit `.env` with your credentials:
   ```env
   POWERBI_EMAIL=your.email@example.com
   POWERBI_PASSWORD=your_password
   POWERBI_REPORT_URL=https://app.powerbi.com/groups/.../reports/...
   
   EMAIL_ADDRESS=your.email@gmail.com
   EMAIL_PASSWORD=your_gmail_app_password
   ```

### Step 3: Setup Gmail App Password

1. Go to https://myaccount.google.com/apppasswords
2. Create a new App Password
3. Copy the 16-character password to `.env`

### Step 4: Get Power BI Report URL

1. Login to https://app.powerbi.com
2. Open your report
3. Copy the URL from browser
4. Paste into `.env`

### Step 5: Run the Application

```bash
streamlit run main.py
```

The app will open at http://localhost:8501

## 📱 Using the Application

1. **Click "Start Automation"** - The system will:
   - Login to Power BI
   - Export your report
   - Split into pages

2. **Select PDFs** - Choose which pages to send

3. **Configure Email** - Add recipients and message

4. **Send!** - Click "Send Emails" and done!

## ⚠️ Common Issues

### "Login failed"
- Check your Power BI credentials in `.env`
- If MFA is enabled, complete it in the browser window

### "Email sending failed"
- Make sure you're using Gmail App Password (not regular password)
- Enable 2FA first, then create App Password

### "Thumbnails not generating"
Install Poppler:
- **Linux**: `sudo apt-get install poppler-utils`
- **Mac**: `brew install poppler`
- **Windows**: Download from https://github.com/oschwartz10612/poppler-windows/releases

## 📚 Need More Help?

See the full [README.md](README.md) for detailed documentation.

## 🎉 That's It!

You're ready to automate your Power BI reports!

