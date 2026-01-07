#!/bin/bash

LOG_DIR="/home/ltsoptio/fastapi_project/logs"
CRON_LOG_DIR="$LOG_DIR/cron"
CRON_LOG="$CRON_LOG_DIR/cleanup.log"

# Ensure cron log directory exists
mkdir -p "$CRON_LOG_DIR"

echo "Cleanup started at $(date)" >> "$CRON_LOG"

find "$LOG_DIR" -type f -name "*.log" -mtime +30 -exec rm -f {} \;

echo "Cleanup finished at $(date)" >> "$CRON_LOG"
