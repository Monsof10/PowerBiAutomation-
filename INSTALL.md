# Install & Run (Local Machine)

1. Create project folder and copy files (already included in ZIP).
2. Create a virtual environment:
   python3 -m venv venv
   source venv/bin/activate
3. Install requirements:
   pip install -r requirements.txt
4. Copy .env.example to .env and fill values.
5. (Optional) If using Playwright:
   playwright install
6. Run once to test:
   python3 automation.py
7. Logs: OUTPUT_DIR/automation.log
