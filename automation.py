# automation.py
import os
import sys
import logging
from dotenv import load_dotenv
from processor import run_once

load_dotenv()  # load .env if present

# Configuration via environment variables
OUTPUT_DIR = os.getenv("OUTPUT_DIR", r"C:\Users\Nasef\Downloads\project folder")
os.makedirs(OUTPUT_DIR, exist_ok=True)

LOG_FILE = os.path.join(OUTPUT_DIR, "automation.log")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s:%(levelname)s:%(message)s",
                    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)])

if __name__ == "__main__":
    ok = run_once()
    sys.exit(0 if ok else 1)
