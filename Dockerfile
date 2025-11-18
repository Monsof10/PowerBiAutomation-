FROM python:3.11-slim

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
# If you plan to use Playwright in a container, uncomment and run the install:
# RUN playwright install --with-deps

ENV OUTPUT_DIR=/app/output
RUN mkdir -p /app/output

CMD ["python3", "automation.py"]
