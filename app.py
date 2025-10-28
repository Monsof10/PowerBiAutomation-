"""
Main Application - Streamlit UI
"""
import streamlit as st
from pathlib import Path
import powerbi
import pdf_service
import email_service_facade
import config

st.set_page_config(page_title="Power BI Automation", page_icon="📊", layout="wide")

# Session state
if 'pdfs' not in st.session_state:
    st.session_state.pdfs = []
if 'selected' not in st.session_state:
    st.session_state.selected = []


def run_automation():
    """Run automation pipeline"""
    with st.spinner("Exporting report..."):
        pdf_path = powerbi.export_report(config.POWERBI_REPORT_URL)
    
    with st.spinner("Processing PDF..."):
        pdfs, thumbs = pdf_service.split_pdf(pdf_path)
    
    st.session_state.pdfs = pdfs
    st.session_state.selected = pdfs.copy()
    st.success("✅ Automation complete!")


def send_emails(recipients, subject, body):
    """Send emails"""
    with st.spinner("Sending emails..."):
        results = email_service_facade.send_pdfs(
            st.session_state.selected,
            recipients,
            subject,
            body
        )
    
    st.success(f"✅ Sent to {len(results['sent'])} recipients")
    if results['failed']:
        st.error(f"❌ Failed: {len(results['failed'])}")


def main():
    """Main application"""
    st.title("📊 Power BI Automation")
    
    if not st.session_state.pdfs:
        if st.button("▶️ Start Automation"):
            run_automation()
    else:
        st.header("Select Pages")
        for idx, pdf in enumerate(st.session_state.pdfs):
            selected = st.checkbox(f"Page {idx+1}", value=pdf in st.session_state.selected)
            if selected and pdf not in st.session_state.selected:
                st.session_state.selected.append(pdf)
            elif not selected and pdf in st.session_state.selected:
                st.session_state.selected.remove(pdf)
        
        st.header("Email Configuration")
        recipients = st.text_area("Recipients (one per line)").strip().split('\n')
        subject = st.text_input("Subject", config.DEFAULT_SUBJECT)
        body = st.text_area("Body", config.DEFAULT_BODY)
        
        if st.button("📤 Send Emails"):
            send_emails(recipients, subject, body)


if __name__ == "__main__":
    main()

