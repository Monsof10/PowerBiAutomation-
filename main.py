"""
Power BI Automation - Main Streamlit Application
"""
import streamlit as st
import time
from pathlib import Path
import logging
from datetime import datetime

# Import our modules
import config
from powerbi_automation import PowerBIAutomation
from pdf_handler import PDFHandler
from email_sender import EmailSender

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Power BI Automation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'automation_complete' not in st.session_state:
    st.session_state.automation_complete = False
if 'pdf_path' not in st.session_state:
    st.session_state.pdf_path = None
if 'split_pdfs' not in st.session_state:
    st.session_state.split_pdfs = []
if 'selected_pdfs' not in st.session_state:
    st.session_state.selected_pdfs = []
if 'email_sent' not in st.session_state:
    st.session_state.email_sent = False


def run_automation_pipeline():
    """Run the complete automation pipeline"""
    status_container = st.empty()
    progress_bar = st.progress(0)
    
    try:
        # Step 1: Power BI Automation
        status_container.info("🚀 Step 1/3: Automating Power BI...")
        progress_bar.progress(10)
        
        automation = PowerBIAutomation(headless=False)
        
        status_container.info("🌐 Starting browser...")
        automation.start_browser()
        progress_bar.progress(20)
        
        status_container.info("🔐 Logging into Power BI...")
        automation.login()
        progress_bar.progress(40)
        
        status_container.info("📄 Navigating to report...")
        automation.navigate_to_report()
        progress_bar.progress(50)
        
        status_container.info("📅 Applying date filter...")
        automation.apply_date_filter()
        progress_bar.progress(60)
        
        status_container.info("💾 Exporting report to PDF...")
        pdf_path = automation.export_to_pdf()
        progress_bar.progress(70)
        
        automation.close()
        st.session_state.pdf_path = pdf_path
        
        # Step 2: PDF Processing
        status_container.info("🔪 Step 2/3: Splitting PDF into pages...")
        progress_bar.progress(75)
        
        handler = PDFHandler(pdf_path)
        split_pdfs = handler.split_pdf()
        progress_bar.progress(85)
        
        status_container.info("🖼️ Generating thumbnails...")
        try:
            handler.generate_thumbnails()
        except Exception as e:
            logger.warning(f"Could not generate thumbnails: {e}")
        
        progress_bar.progress(95)
        
        st.session_state.split_pdfs = split_pdfs
        st.session_state.selected_pdfs = split_pdfs.copy()  # Select all by default
        
        # Step 3: Complete
        progress_bar.progress(100)
        status_container.success("✅ Automation completed successfully!")
        st.session_state.automation_complete = True
        
        time.sleep(2)
        st.rerun()
        
    except Exception as e:
        progress_bar.empty()
        status_container.error(f"❌ Error during automation: {str(e)}")
        logger.error(f"Automation failed: {e}", exc_info=True)
        st.error(f"Automation failed: {str(e)}")
        
        # Try to close browser if it's still open
        try:
            if 'automation' in locals():
                automation.close()
        except:
            pass


def display_pdf_preview():
    """Display PDF preview and selection interface"""
    st.header("📄 PDF Preview & Selection")
    
    if not st.session_state.split_pdfs:
        st.warning("No PDFs available. Please run the automation first.")
        return
    
    st.success(f"✅ Report split into {len(st.session_state.split_pdfs)} pages")
    
    # Select/Deselect all buttons
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("✓ Select All"):
            st.session_state.selected_pdfs = st.session_state.split_pdfs.copy()
            st.rerun()
    with col2:
        if st.button("✗ Deselect All"):
            st.session_state.selected_pdfs = []
            st.rerun()
    
    st.divider()
    
    # Display PDFs in a grid
    cols_per_row = 3
    for idx in range(0, len(st.session_state.split_pdfs), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for col_idx, col in enumerate(cols):
            pdf_idx = idx + col_idx
            if pdf_idx >= len(st.session_state.split_pdfs):
                break
            
            pdf_path = st.session_state.split_pdfs[pdf_idx]
            
            with col:
                # Check if thumbnail exists
                thumbnail_path = pdf_path.with_suffix('.png')
                
                if thumbnail_path.exists():
                    st.image(str(thumbnail_path), use_container_width=True)
                else:
                    st.info(f"Page {pdf_idx + 1}")
                
                # Checkbox for selection
                is_selected = pdf_path in st.session_state.selected_pdfs
                selected = st.checkbox(
                    f"Send Page {pdf_idx + 1}",
                    value=is_selected,
                    key=f"pdf_check_{pdf_idx}"
                )
                
                if selected and pdf_path not in st.session_state.selected_pdfs:
                    st.session_state.selected_pdfs.append(pdf_path)
                elif not selected and pdf_path in st.session_state.selected_pdfs:
                    st.session_state.selected_pdfs.remove(pdf_path)
                
                # Download button
                with open(pdf_path, 'rb') as f:
                    st.download_button(
                        label="⬇️ Download",
                        data=f.read(),
                        file_name=pdf_path.name,
                        mime="application/pdf",
                        key=f"download_{pdf_idx}"
                    )
    
    st.divider()
    st.info(f"📋 {len(st.session_state.selected_pdfs)} page(s) selected for sending")


def display_email_interface():
    """Display email configuration and sending interface"""
    st.header("📧 Email Configuration")
    
    if not st.session_state.selected_pdfs:
        st.warning("⚠️ Please select at least one PDF to send.")
        return
    
    # Email configuration
    col1, col2 = st.columns(2)
    
    with col1:
        recipients_input = st.text_area(
            "Recipients (one per line or comma-separated)",
            value="\n".join(config.DEFAULT_RECIPIENTS) if config.DEFAULT_RECIPIENTS else "",
            height=150,
            help="Enter email addresses, one per line or separated by commas"
        )
        
        subject = st.text_input(
            "Email Subject",
            value=config.DEFAULT_SUBJECT,
            help="Subject line for the email"
        )
    
    with col2:
        body = st.text_area(
            "Email Body",
            value=config.DEFAULT_BODY,
            height=150,
            help="Body text for the email"
        )
        
        # Parse recipients
        recipients = []
        if recipients_input:
            # Handle both newlines and commas
            recipients_input = recipients_input.replace('\n', ',')
            recipients = [r.strip() for r in recipients_input.split(',') if r.strip()]
        
        st.info(f"📮 Will send to {len(recipients)} recipient(s)")
    
    st.divider()
    
    # Send email section
    if not recipients:
        st.warning("⚠️ Please enter at least one recipient email address.")
        return
    
    # Show summary
    with st.expander("📋 Review Before Sending", expanded=True):
        st.write("**Selected PDFs:**")
        for pdf in st.session_state.selected_pdfs:
            st.write(f"  - {pdf.name}")
        
        st.write("\n**Recipients:**")
        for recipient in recipients:
            st.write(f"  - {recipient}")
        
        st.write(f"\n**Subject:** {subject}")
        st.write(f"**Body:** {body[:100]}{'...' if len(body) > 100 else ''}")
    
    # Send button
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        send_button = st.button("📤 Send Emails", type="primary", use_container_width=True)
    
    if send_button:
        # Confirmation
        with st.spinner("Sending emails..."):
            send_emails(recipients, subject, body)


def send_emails(recipients, subject, body):
    """Send emails to recipients"""
    try:
        status_container = st.empty()
        progress_bar = st.progress(0)
        
        status_container.info("📧 Initializing email sender...")
        sender = EmailSender()
        progress_bar.progress(20)
        
        status_container.info("📤 Sending emails...")
        
        results = {
            'sent': [],
            'failed': []
        }
        
        total = len(recipients)
        for idx, recipient in enumerate(recipients):
            try:
                sender.send_email(
                    to_addresses=recipient,
                    subject=subject,
                    body=body,
                    attachments=st.session_state.selected_pdfs
                )
                results['sent'].append(recipient)
                logger.info(f"Email sent to {recipient}")
            except Exception as e:
                results['failed'].append({'recipient': recipient, 'error': str(e)})
                logger.error(f"Failed to send to {recipient}: {e}")
            
            progress_bar.progress(20 + int((idx + 1) / total * 80))
        
        sender.close()
        progress_bar.progress(100)
        
        # Display results
        status_container.empty()
        progress_bar.empty()
        
        st.success(f"✅ Successfully sent {len(results['sent'])} email(s)!")
        
        if results['sent']:
            with st.expander("✅ Successful Deliveries", expanded=True):
                for recipient in results['sent']:
                    st.write(f"  ✓ {recipient}")
        
        if results['failed']:
            with st.expander("❌ Failed Deliveries", expanded=True):
                for failure in results['failed']:
                    st.write(f"  ✗ {failure['recipient']}: {failure['error']}")
        
        st.session_state.email_sent = True
        
        # Log to file
        log_email_activity(recipients, subject, results)
        
    except Exception as e:
        st.error(f"❌ Error sending emails: {str(e)}")
        logger.error(f"Email sending failed: {e}", exc_info=True)


def log_email_activity(recipients, subject, results):
    """Log email activity to file"""
    log_entry = f"\n{'='*80}\n"
    log_entry += f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    log_entry += f"Subject: {subject}\n"
    log_entry += f"Recipients: {', '.join(recipients)}\n"
    log_entry += f"Sent: {len(results['sent'])}\n"
    log_entry += f"Failed: {len(results['failed'])}\n"
    log_entry += f"{'='*80}\n"
    
    log_file = config.LOGS_FOLDER / 'email_activity.log'
    with open(log_file, 'a') as f:
        f.write(log_entry)


def display_sidebar():
    """Display sidebar with information and controls"""
    with st.sidebar:
        st.title("📊 Power BI Automation")
        st.markdown("---")
        
        # Configuration status
        st.subheader("⚙️ Configuration Status")
        
        config_checks = {
            "Power BI Email": bool(config.POWERBI_EMAIL),
            "Power BI Password": bool(config.POWERBI_PASSWORD),
            "Report URL": bool(config.POWERBI_REPORT_URL),
            "Email Address": bool(config.EMAIL_ADDRESS),
            "Email Password": bool(config.EMAIL_PASSWORD)
        }
        
        all_configured = all(config_checks.values())
        
        for key, value in config_checks.items():
            if value:
                st.success(f"✅ {key}")
            else:
                st.error(f"❌ {key}")
        
        st.markdown("---")
        
        # System information
        st.subheader("ℹ️ System Information")
        st.write(f"**Downloads Folder:** `{config.DOWNLOADS_FOLDER.name}`")
        st.write(f"**Output Folder:** `{config.OUTPUT_FOLDER.name}`")
        st.write(f"**Logs Folder:** `{config.LOGS_FOLDER.name}`")
        
        st.markdown("---")
        
        # Help section
        with st.expander("❓ Help & Troubleshooting"):
            st.markdown("""
            **Configuration:**
            - Create a `.env` file from `env.example`
            - Add your Power BI credentials
            - Add your email credentials
            - Update the report URL
            
            **Gmail Setup:**
            - Use App Password, not regular password
            - Enable 2FA first, then create App Password
            - [Gmail App Password Guide](https://support.google.com/accounts/answer/185833)
            
            **Common Issues:**
            - **Login fails:** Check credentials, may need MFA
            - **Export fails:** Check report permissions
            - **Email fails:** Verify email credentials
            """)
        
        st.markdown("---")
        
        # Reset button
        if st.button("🔄 Reset Session", use_container_width=True):
            st.session_state.automation_complete = False
            st.session_state.pdf_path = None
            st.session_state.split_pdfs = []
            st.session_state.selected_pdfs = []
            st.session_state.email_sent = False
            st.rerun()
        
        return all_configured


def main():
    """Main application"""
    st.title("📊 Power BI Automation System")
    st.markdown("Automate Power BI report generation, PDF processing, and email distribution")
    
    # Display sidebar and get configuration status
    all_configured = display_sidebar()
    
    if not all_configured:
        st.error("⚠️ Configuration incomplete! Please check the sidebar and update your `.env` file.")
        st.info("💡 Copy `env.example` to `.env` and fill in your credentials.")
        return
    
    # Main workflow
    if not st.session_state.automation_complete:
        # Step 1: Start automation
        st.header("🚀 Start Automation")
        st.write("Click the button below to start the Power BI automation process.")
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("▶️ Start Automation", type="primary", use_container_width=True):
                run_automation_pipeline()
    
    else:
        # Step 2 & 3: Preview and Email
        tab1, tab2 = st.tabs(["📄 PDF Preview", "📧 Email Configuration"])
        
        with tab1:
            display_pdf_preview()
        
        with tab2:
            display_email_interface()
        
        # Show success message if emails were sent
        if st.session_state.email_sent:
            st.balloons()
            st.success("🎉 Process completed successfully!")


if __name__ == "__main__":
    main()

