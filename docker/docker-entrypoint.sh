#!/bin/sh
set -e

# Ensure log file exists
mkdir -p /var/log
touch /var/log/automation.log

# Ensure cron file is present (copied at build time)
if [ -f /etc/cron.d/automation ]; then
    chmod 0644 /etc/cron.d/automation
fi

# Start cron in foreground and also tail the log so container keeps running
cron -f &

# Tail logs
tail -n +1 -f /var/log/automation.log
