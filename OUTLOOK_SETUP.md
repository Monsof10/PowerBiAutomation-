# Outlook/Office 365 Email Configuration

## ✅ Your Configuration is Set for Outlook

The system has been configured to use Outlook/Office 365 email instead of Gmail.

## 📧 Outlook SMTP Settings (Already Configured)

```env
EMAIL_ADDRESS=abdirisaq@highmor.com
EMAIL_PASSWORD=your_outlook_password_here
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
```

## 🔐 Authentication Options

### Option 1: Regular Password (Recommended if no 2FA)

If your Outlook account **does not** have 2-Factor Authentication:
```env
EMAIL_PASSWORD=YourRegularOutlookPassword
```

### Option 2: App Password (If 2FA is Enabled)

If your Outlook account **has** 2-Factor Authentication:

1. Go to: https://account.microsoft.com/security
2. Click on "Advanced security options"
3. Under "App passwords", click "Create a new app password"
4. Copy the generated password
5. Use it in your `.env` file:
   ```env
   EMAIL_PASSWORD=xxxx-xxxx-xxxx-xxxx
   ```

### Option 3: Organization Account

If using a company/organization Outlook account:
- Use your organization email password
- Check with IT if SMTP is allowed
- May require OAuth (more complex setup)

## ⚙️ Configuration Steps

### 1. Copy the Template
```bash
cp env.example .env
```

### 2. Edit Your Credentials
```bash
nano .env  # or use your preferred editor
```

### 3. Update These Fields
```env
# Power BI Credentials
POWERBI_EMAIL=abdirisaq@highmor.com
POWERBI_PASSWORD=your_powerbi_password

# Power BI Report URL
POWERBI_REPORT_URL=https://app.powerbi.com/groups/YOUR-WORKSPACE/reports/YOUR-REPORT

# Email Configuration (Already set for Outlook)
EMAIL_ADDRESS=abdirisaq@highmor.com
EMAIL_PASSWORD=your_outlook_password

# SMTP Settings (Already correct for Outlook)
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
```

## 🧪 Test Email Configuration

Create a test file `test_outlook.py`:

```python
from email_sender import EmailSender

# Test Outlook email
sender = EmailSender(
    email_address='abdirisaq@highmor.com',
    email_password='your_password',
    smtp_server='smtp.office365.com',
    smtp_port=587
)

try:
    sender.send_email(
        to_addresses='your.test@email.com',
        subject='Test Email from Power BI Automation',
        body='If you receive this, Outlook email is working!',
        attachments=None
    )
    print("✅ Email sent successfully!")
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    sender.close()
```

Run the test:
```bash
python test_outlook.py
```

## 🔧 Troubleshooting Outlook Email

### Error: "Authentication failed"

**Solutions:**
1. Verify email and password are correct
2. Check if 2FA is enabled (use App Password if yes)
3. Ensure SMTP is enabled for your account
4. Check with IT if using company email

### Error: "Connection refused"

**Solutions:**
1. Verify SMTP settings:
   - Server: `smtp.office365.com`
   - Port: `587`
2. Check firewall/network settings
3. Ensure port 587 is not blocked

### Error: "Relay access denied"

**Solutions:**
1. Use your actual Outlook email as sender
2. Don't try to send from a different email
3. Authenticate properly before sending

### Company/Organization Email Issues

If using company Outlook:
1. Check with IT if SMTP is allowed
2. May need to whitelist the application
3. Some organizations require OAuth instead of password
4. VPN might be required

## 📝 Common Outlook Configurations

### Personal Outlook.com
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```
or
```env
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
```

### Office 365 Business
```env
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
```

### Exchange Server (On-Premises)
```env
SMTP_SERVER=your-exchange-server.company.com
SMTP_PORT=587  # or 25, check with IT
```

## 🔐 Security Best Practices

1. **Use App Password** if 2FA is enabled
2. **Don't share** your `.env` file
3. **Keep** `.env` out of version control (already in `.gitignore`)
4. **Rotate passwords** regularly
5. **Use strong passwords**

## ✅ Verification Checklist

Before running the full automation:

- [ ] `.env` file created from `env.example`
- [ ] Outlook email address added
- [ ] Outlook password/App Password added
- [ ] SMTP server set to `smtp.office365.com`
- [ ] SMTP port set to `587`
- [ ] Power BI credentials added
- [ ] Power BI report URL added
- [ ] Test email sent successfully

## 🚀 Next Steps

1. Complete your `.env` configuration
2. Run setup verification:
   ```bash
   python test_setup.py
   ```
3. Test email separately:
   ```bash
   python test_outlook.py
   ```
4. Run the full application:
   ```bash
   streamlit run main.py
   ```

## 📚 Additional Resources

- [Microsoft Account Security](https://account.microsoft.com/security)
- [Outlook SMTP Settings](https://support.microsoft.com/en-us/office/pop-imap-and-smtp-settings-8361e398-8af4-4e97-b147-6c6c4ac95353)
- [App Passwords Guide](https://support.microsoft.com/en-us/account-billing/using-app-passwords-with-apps-that-don-t-support-two-step-verification-5896ed9b-4263-e681-128a-a6f2979a7944)

## 💡 Pro Tips

1. **Test email first** before running full automation
2. **Keep credentials secure** - never commit `.env` to git
3. **Use descriptive subjects** for better email organization
4. **Monitor the first run** to ensure everything works
5. **Check spam folder** if test emails don't arrive

---

**You're all set for Outlook! 🎉**

Continue with the main setup in `QUICKSTART.md` or `START_HERE.md`

