FROM python:3.11-slim

# Install system dependencies required by Playwright and cron
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gnupg \
    fonts-liberation \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libxss1 \
    libpangocairo-1.0-0 \
    libgtk-3-0 \
    cron \
    wget \
    build-essential \
    pkg-config \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
 && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

# Install Playwright and browser binaries
RUN pip install playwright || true
RUN python -m playwright install chromium

# Add cron job
COPY docker/cron/automation /etc/cron.d/automation
RUN chmod 0644 /etc/cron.d/automation && crontab /etc/cron.d/automation

# Add entrypoint script
COPY docker/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["cron"]
