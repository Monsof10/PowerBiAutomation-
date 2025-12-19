# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    procps \
    curl \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional system dependencies and fonts required by Playwright
# (some font package names used by Playwright are not available on newer Debian)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        fonts-unifont \
        fonts-liberation \
        fonts-dejavu-core \
        fonts-noto-color-emoji \
        libnss3 \
        libatk-bridge2.0-0 \
        libgtk-3-0 \
        libgbm1 \
        libasound2 \
        libx11-6 \
        libxcomposite1 \
        libxdamage1 \
        libxrandr2 \
        libpangocairo-1.0-0 \
        libpango-1.0-0 \
        libxss1 \
        libxtst6 \
        xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright browsers (already have Python package installed from requirements)
RUN playwright install chromium

# Copy the application code
COPY . .

# Create necessary directories
RUN mkdir -p output logs downloads emailtemp

# Create a cron job to run on the 1st of every month at 6 AM
RUN echo "0 6 1 * * root cd /app && python automation.py >> /app/logs/cron.log 2>&1" > /etc/cron.d/automation

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/automation

# Apply cron job
RUN crontab /etc/cron.d/automation

# Create the log file to be able to run tail
RUN touch /app/logs/cron.log

# Run the command on container startup (run cron in foreground so Docker handles signals)
CMD ["cron", "-f"]
