# streamlit_dashboard.py
import streamlit as st
import subprocess
import os
from pathlib import Path

OUTPUT_DIR = os.getenv("OUTPUT_DIR", r"C:\Users\Nasef\Downloads\project folder")
LOG_FILE = os.path.join(OUTPUT_DIR, "automation.log")

st.title("PDF Monthly Automation - WIP")
st.write("Trigger runs and view logs.")

if st.button("Run now"):
    st.write("Running automation...")
    p = subprocess.Popen(["python3", "automation.py"], cwd=os.getcwd())
    st.write(f"Started process pid={p.pid}")

st.write("### Logs")
if Path(LOG_FILE).exists():
    st.text(Path(LOG_FILE).read_text()[-10000:])  # last 10k chars
else:
    st.write("No logs yet.")
