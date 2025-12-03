#!/usr/bin/env python3
"""Send an HTML email with inline images (CID).

This script reads configuration from `config.py` when available:
- `EMAIL_BODY` (string) will be used as the HTML body if present
- `EMAIL_HTML_TEMPLATE` (path) is used if `EMAIL_BODY` is not set
- `EMAIL_INLINE_IMAGES` and `EMAIL_INLINE_CIDS` define default image files and CIDs
- `EMAIL_ADDRESS` / `EMAIL_PASSWORD` / `SMTP_SERVER` / `SMTP_PORT` are used as SMTP defaults

It attaches images as inline MIMEImage parts and references them in HTML using `cid:...`.
"""
import os
import sys
import argparse
import base64
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib

# try to import project config for sensible defaults
try:
    import config as cfg
except Exception:
    cfg = None


def read_image_data(path: str) -> bytes:
    if path.lower().endswith('.b64'):
        text = open(path, 'r', encoding='utf-8').read().strip()
        return base64.b64decode(text)
    with open(path, 'rb') as fh:
        data = fh.read()
    if b'\x00' in data:
        return data
    try:
        text = data.decode('utf-8').strip()
        return base64.b64decode(text)
    except Exception:
        return data


def make_related_message(subject: str, sender: str, recipients, html: str, images: list):
    msg_root = MIMEMultipart('related')
    msg_root['Subject'] = subject
    msg_root['From'] = sender
    msg_root['To'] = ', '.join(recipients) if isinstance(recipients, (list, tuple)) else recipients

    msg_alt = MIMEMultipart('alternative')
    msg_root.attach(msg_alt)
    msg_alt.attach(MIMEText('This message contains HTML content with inline images.', 'plain'))
    msg_alt.attach(MIMEText(html, 'html'))

    for cid, path in images:
        try:
            img_data = read_image_data(path)
        except FileNotFoundError:
            print(f"Warning: image file not found: {path}")
            continue
        ctype, _ = mimetypes.guess_type(path)
        subtype = None
        if ctype and ctype.startswith('image/'):
            subtype = ctype.split('/', 1)[1]
        if subtype:
            img = MIMEImage(img_data, _subtype=subtype)
        else:
            img = MIMEImage(img_data)
        img.add_header('Content-ID', f'<{cid}>')
        img.add_header('Content-Disposition', 'inline', filename=os.path.basename(path))
        msg_root.attach(img)

    return msg_root


def send_message(smtp_host, smtp_port, smtp_user, smtp_pass, msg, use_ssl=False, starttls=False):
    if use_ssl:
        server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10)
    else:
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
    server.set_debuglevel(0)
    try:
        if starttls:
            server.ehlo()
            server.starttls()
            server.ehlo()
        if smtp_user and smtp_pass:
            server.login(smtp_user, smtp_pass)
        server.send_message(msg)
    finally:
        server.quit()


def default_html_template():
    return '''<!doctype html>
<html>
  <head><meta charset="utf-8" /><title>Email</title></head>
  <body>
    <h1>Monthly Report</h1>
    <p>This is an example email with inline images (CID).</p>
    <img src="cid:logo1" alt="logo1" />
    <img src="cid:logo2" alt="logo2" />
  </body>
</html>
'''


def main(argv):
    parser = argparse.ArgumentParser(description='Send HTML email with inline images (CID).')
    parser.add_argument('--to', required=True, help='Comma-separated recipient list or single address')
    parser.add_argument('--from', dest='from_addr', help='From address', default=(getattr(cfg, 'EMAIL_ADDRESS', 'no-reply@example.com') if cfg else os.environ.get('SMTP_FROM', 'no-reply@example.com')))
    parser.add_argument('--subject', default='HTML Email with Inline Images')
    parser.add_argument('--html-file', help='Path to HTML file. If omitted a default template or config.EMAIL_BODY is used.')
    parser.add_argument('--image', action='append', nargs=2, metavar=('CID', 'PATH'), help='Attach an image as inline with a Content-ID. Example: --image logo1 logo.png')
    parser.add_argument('--smtp-host', default=(getattr(cfg, 'SMTP_SERVER', None) if cfg else os.environ.get('SMTP_HOST', 'smtp.example.com')))
    parser.add_argument('--smtp-port', type=int, default=(getattr(cfg, 'SMTP_PORT', None) if cfg else int(os.environ.get('SMTP_PORT', '587'))))
    parser.add_argument('--smtp-user', default=(getattr(cfg, 'EMAIL_ADDRESS', None) if cfg else os.environ.get('SMTP_USER')))
    parser.add_argument('--smtp-pass', default=(getattr(cfg, 'EMAIL_PASSWORD', None) if cfg else os.environ.get('SMTP_PASS')))
    parser.add_argument('--use-ssl', action='store_true', help='Connect using SMTPS (SMTP over SSL)')
    parser.add_argument('--starttls', action='store_true', help='Use STARTTLS')
    parser.add_argument('--dry-run', action='store_true', help='Write the generated message to an .eml file instead of sending')
    parser.add_argument('--output-eml', default='message.eml', help='Path to write .eml when using --dry-run')

    args = parser.parse_args(argv)
    recipients = [r.strip() for r in args.to.split(',') if r.strip()]

    # HTML selection priority: explicit file > cfg.EMAIL_BODY string > cfg.EMAIL_HTML_TEMPLATE file > default
    if args.html_file:
        html = open(args.html_file, 'r', encoding='utf-8').read()
    elif cfg and getattr(cfg, 'EMAIL_BODY', None):
        html = cfg.EMAIL_BODY
    elif cfg and getattr(cfg, 'EMAIL_HTML_TEMPLATE', ''):
        tpl = cfg.EMAIL_HTML_TEMPLATE
        if not os.path.isabs(tpl) and hasattr(cfg, 'BASE_DIR'):
            tpl = os.path.join(cfg.BASE_DIR, tpl)
        if os.path.exists(tpl):
            html = open(tpl, 'r', encoding='utf-8').read()
        else:
            html = default_html_template()
    else:
        html = default_html_template()

    images = []
    if args.image:
        for cid, path in args.image:
            images.append((cid, path))
    else:
        # prefer config values
        if cfg and getattr(cfg, 'EMAIL_INLINE_IMAGES', None):
            imgs = getattr(cfg, 'EMAIL_INLINE_IMAGES')
            cids = getattr(cfg, 'EMAIL_INLINE_CIDS', [])
            for idx, img in enumerate(imgs):
                cid = cids[idx] if idx < len(cids) else f'logo{idx+1}'
                path = img
                if not os.path.isabs(path) and hasattr(cfg, 'BASE_DIR'):
                    path = os.path.join(cfg.BASE_DIR, path)
                if os.path.exists(path):
                    images.append((cid, path))
        else:
            candidates = [
                'Screenshot 2025-11-18 at 5.36.22\u202fAM.png',
                'Screenshot 2025-11-18 at 5.36.22 AM.png',
                'image.png',
            ]
            cid_names = ['logo1', 'logo2']
            idx = 0
            for c in candidates:
                if os.path.exists(c) and idx < len(cid_names):
                    images.append((cid_names[idx], c))
                    idx += 1
                if idx >= len(cid_names):
                    break

    if not images:
        print('No images found or provided. Provide --image CID PATH or set EMAIL_INLINE_IMAGES in config.')

    msg = make_related_message(args.subject, args.from_addr, recipients, html, images)

    if args.dry_run:
        with open(args.output_eml, 'wb') as fh:
            fh.write(msg.as_bytes())
        print(f'Wrote email (EML) to {args.output_eml}. Open with an email client to inspect.')
        return 0

    try:
        send_message(args.smtp_host, args.smtp_port, args.smtp_user, args.smtp_pass, msg, use_ssl=args.use_ssl, starttls=args.starttls)
        print('Message sent successfully')
    except Exception as exc:
        print('Failed to send message:', exc)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
