import logging
from logging.handlers import TimedRotatingFileHandler
import os
from datetime import datetime

# Create logs directory if it doesn't exist
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Include the current date in the log file name
date_str = datetime.now().strftime("%Y-%m-%d")  
LOG_FILE = os.path.join(LOG_DIR, f"api_{date_str}.log")


# Create a handler that rotates the log at midnight
handler = TimedRotatingFileHandler(
    LOG_FILE,
    when="midnight",    # Rotate at midnight
    interval=1,         # Every day
    backupCount=7,     # Keep last 14 days
    encoding="utf-8"
)

# Optional: set the log file suffix format (e.g., api.log.2025-12-18)
handler.suffix = "%Y-%m-%d"

# Define log format
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S'
)
handler.setFormatter(formatter)

# Create logger
logger = logging.getLogger("api_logger")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Prevent double logging if root logger is used elsewhere
logger.propagate = False

