import os
import logging
import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
import mimetypes

# Email body templates
EMAIL_BODY = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="x-apple-disable-message-reformatting">
<title></title>
<!--[if mso]>
<noscript>
<xml>
<o:OfficeDocumentSettings>
<o:PixelsPerInch>96</o:PixelsPerInch>
</o:OfficeDocumentSettings>
</xml>
</noscript>
<![endif]-->
<style>
table, td, div, h1, p {font-family: Arial, sans-serif;}
</style>
</head>
<body style="margin:0;padding:0;">
<table role="presentation" style="width:100%;border-collapse:collapse;border:0;border-spacing:0;background:#a3c7ff;">
<tr>
<td align="center" style="padding:0;">
<table role="presentation" style="width:602px;border-collapse:collapse;border:0;border-spacing:0;text-align:left;">
<tr>
<td align="center" style="padding:40px 0 30px 0;background:#ffffff;">
<b>This report is powered by</b><br>
<a href="https://www.highmor.com">
    <img src="cid:logo1" width="120" height="60" />
    </a><br>
</td>
</tr>
<tr>
<td style="background:#FFFFFF;color:#2157BE;padding:36px 30px 42px 30px; text-align:center;font-size:200%; border:0;">
    <img src="cid:logo2" width="170" height="170" alt="Report Logo" style="display:block; margin:0 auto; border:0; padding:0;" /><br>
    <b>Power BI Monthly Report</b>
</td>
</tr>
<tr>
<td align="center" style="padding:10px 10px 10px 30px;background:#2157BE;">
</td>
</tr>
<tr>
<td style="background:#ffffff;padding:10px 10px 10px 10px;font-size:150%; color:#000000; line-height:1.4;">
<p>Good morning,</p>
<p>Please find the attached PDF data report for your reference. If you have any questions or would like an image of the map (page 6 of the dashboard), please contact Mackie at <a href="mailto:omcc@highmor.com">omcc@highmor.com</a>.</p>
<p>Warm regards,</p>
<p><strong>highMor Data Analytics Team</strong></p>
</td>
</tr>
<tr>
<td align="center" style="padding:30px 30px 30px 30px;background:#2157BE;">
</td>
</tr>
</table>
</td>
</tr>
</table>
</body>
</html>"""

EMAIL_BODY_NO_ACTIVATIONS = """<!DOCTYPE html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="x-apple-disable-message-reformatting">
<title></title>
<!--[if mso]>
<noscript>
<xml>
<o:OfficeDocumentSettings>
<o:PixelsPerInch>96</o:PixelsPerInch>
</o:OfficeDocumentSettings>
</xml>
</noscript>
<![endif]-->
<style>
      table, td, div, h1, p {font-family: Arial, sans-serif;}
</style>
</head>
<body style="margin:0;padding:0;">
<table role="presentation" style="width:100%;border-collapse:collapse;border:0;border-spacing:0;background:#a3c7ff;">
<tr>
<td align="center" style="padding:0;">
<table role="presentation" style="width:602px;border-collapse:collapse;border:1px solid #cccccc;border-spacing:0;text-align:left;">
<tr>
<td align="center" style="padding:40px 0 30px 0;background:#ffffff;">
<b>This report is powered by</b><br>
<a href="https://www.highmor.com"> <!-- Your hyperlink goes here -->
    <img src="cid:logo1" width="120" height="60" />
    </a>
<br> <b style="color: #0B65BA;">Transfer Center Software</b>
</td>
</tr>
</td>
</tr>
<tr>
<td align="center" style="padding:10px 10px 10px 30px;background:#2157BE;">
</td>
</tr>
<tr>
<td style="background:#FFFFFF;color:#2157BE;padding:36px 30px 42px 30px; text-align:center;font-size:200%;">
<img src="cid:logo2" width="170" height="170" style="display:block; margin:0 auto; border:0; padding:0;" />
<br>
<b>Power BI Monthly Report</b>
</td>
</tr>
<tr>
<td align="center" style="padding:10px 10px 10px 30px;background:#2157BE;">
</td>
</tr>
<tr>
<td style="background:#ffffff;padding:10px 10px 10px 10px;font-size:150%;">
<p><br>
                        Good morning,<br><br>
                        There were no accepted patients to your facilities last month via OMCC. If you have any questions or concerns, please contact our support team at omcc@highmor.com.
<br><br>
                        Warm regards,<br><br>
                        highMor Data Analytics Team<br>
</p>
</td>
</tr>
<tr>
<td align="center" style="padding:30px 30px 30px 30px;background:#2157BE;">
</td>
</tr>
</table>
</td>
</tr>
</table>
</body>
</html>"""

def send_email_with_attachment(smtp_host, smtp_port, smtp_user, smtp_pass,
                               from_addr, to_addr, subject, body, attachment_path):
    """Send an HTML email with a PDF attachment and inline images (logo1, logo2).

    The message structure is:
    multipart/mixed
      multipart/related
        multipart/alternative
          text/plain
          text/html
        image (cid:logo1)
        image (cid:logo2)
      application/pdf (attachment)
    """
    logging.info("Preparing email to %s", to_addr)
    # Root container
    msg_root = MIMEMultipart('mixed')
    msg_root['Subject'] = subject
    msg_root['From'] = from_addr
    msg_root['To'] = to_addr

    # Related part for HTML + inline images
    related = MIMEMultipart('related')
    alt = MIMEMultipart('alternative')
    related.attach(alt)

    # Plain text fallback
    alt.attach(MIMEText('This message contains HTML content and a PDF attachment.', 'plain'))
    # HTML body
    alt.attach(MIMEText(body, 'html'))

    # Attach inline images from emailtemp folder
    base_dir = os.path.dirname(__file__)
    image_paths = [os.path.join(base_dir, 'emailtemp', 'highmor.png'),
                   os.path.join(base_dir, 'emailtemp', 'omcc.png')]
    cids = ['logo1', 'logo2']
    for cid, path in zip(cids, image_paths):
        if os.path.exists(path):
            with open(path, 'rb') as imgf:
                img_data = imgf.read()
            try:
                subtype = mimetypes.guess_type(path)[0].split('/')[1]
            except Exception:
                subtype = None
            if subtype:
                img = MIMEImage(img_data, _subtype=subtype)
            else:
                img = MIMEImage(img_data)
            img.add_header('Content-ID', f'<{cid}>')
            img.add_header('Content-Disposition', 'inline', filename=os.path.basename(path))
            related.attach(img)
        else:
            logging.warning('Inline image not found: %s', path)

    # Attach the related part to root
    msg_root.attach(related)

    # Attach the PDF
    with open(attachment_path, 'rb') as f:
        pdf = MIMEApplication(f.read(), _subtype='pdf')
        pdf.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
        msg_root.attach(pdf)

    logging.info("Connecting to SMTP %s:%s", smtp_host, smtp_port)
    try:
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=60)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg_root)
        server.quit()
        logging.info("Email sent to %s", to_addr)
    except smtplib.SMTPAuthenticationError as e:
        if "basic authentication is disabled" in str(e) or "535" in str(e):
            logging.error("Authentication failed. For Gmail accounts, you need an App Password: "
                         "1. Go to https://myaccount.google.com/security "
                         "2. Enable 2-Step Verification if not already enabled "
                         "1. Go to https://myaccount.google.com/apppasswords "
                         "2. Generate an App Password for 'Mail' "
                         "3. Use the App Password instead of your regular password in SMTP_PASS")
            raise
        else:
            raise

def send_email_without_attachment(smtp_host, smtp_port, smtp_user, smtp_pass,
                                  from_addr, to_addr, subject, body):
    """Send HTML email (no attachment) with inline images from emailtemp folder."""
    logging.info("Preparing email to %s (no attachment)", to_addr)
    msg_root = MIMEMultipart('related')
    msg_root['Subject'] = subject
    msg_root['From'] = from_addr
    msg_root['To'] = to_addr

    alt = MIMEMultipart('alternative')
    alt.attach(MIMEText('This message contains HTML content.', 'plain'))
    alt.attach(MIMEText(body, 'html'))
    msg_root.attach(alt)

    # Attach inline images
    base_dir = os.path.dirname(__file__)
    image_paths = [os.path.join(base_dir, 'emailtemp', 'highmor.png'),
                   os.path.join(base_dir, 'emailtemp', 'omcc.png')]
    cids = ['logo1', 'logo2']
    for cid, path in zip(cids, image_paths):
        if os.path.exists(path):
            with open(path, 'rb') as imgf:
                img_data = imgf.read()
            try:
                subtype = mimetypes.guess_type(path)[0].split('/')[1]
            except Exception:
                subtype = None
            if subtype:
                img = MIMEImage(img_data, _subtype=subtype)
            else:
                img = MIMEImage(img_data)
            img.add_header('Content-ID', f'<{cid}>')
            img.add_header('Content-Disposition', 'inline', filename=os.path.basename(path))
            msg_root.attach(img)
        else:
            logging.warning('Inline image not found: %s', path)

    logging.info("Connecting to SMTP %s:%s", smtp_host, smtp_port)
    try:
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=60)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg_root)
        server.quit()
        logging.info("Email sent to %s (no attachment)", to_addr)
    except smtplib.SMTPAuthenticationError as e:
        if "basic authentication is disabled" in str(e) or "535" in str(e):
            logging.error("Authentication failed. For Gmail accounts, you need an App Password: "
                         "1. Go to https://myaccount.google.com/security "
                         "2. Enable 2-Step Verification if not already enabled "
                         "1. Go to https://myaccount.google.com/apppasswords "
                         "2. Generate an App Password for 'Mail' "
                         "3. Use the App Password instead of your regular password in SMTP_PASS")
            raise
        else:
            raise
