import logging
from logging.handlers import TimedRotatingFileHandler
import os
from datetime import datetime

# ============================================================
# LOG DIRECTORIES
# ============================================================

BASE_LOG_DIR = "logs"

ACCESS_LOG_DIR = os.path.join(BASE_LOG_DIR, "access")
ERROR_LOG_DIR = os.path.join(BASE_LOG_DIR, "error")

os.makedirs(ACCESS_LOG_DIR, exist_ok=True)
os.makedirs(ERROR_LOG_DIR, exist_ok=True)


# ============================================================
# LOG FILE NAMES (daily)
# ============================================================

date_str = datetime.now().strftime("%Y-%m-%d")

ACCESS_LOG_FILE = os.path.join(
    ACCESS_LOG_DIR, f"access-{date_str}.log"
)
ERROR_LOG_FILE = os.path.join(
    ERROR_LOG_DIR, f"error-{date_str}.log"
)



# ------------------ FORMATTER ------------------ #
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# ------------------ ACCESS HANDLER ------------------ #
access_handler = TimedRotatingFileHandler(
    ACCESS_LOG_FILE,
    when="midnight",
    interval=1,
    encoding="utf-8"
)
access_handler.setFormatter(formatter)
access_handler.suffix = "%Y-%m-%d"

# ------------------ ERROR HANDLER ------------------ #
error_handler = TimedRotatingFileHandler(
    ERROR_LOG_FILE,
    when="midnight",
    interval=1,
    encoding="utf-8"
)
error_handler.setFormatter(formatter)
error_handler.suffix = "%Y-%m-%d"

# ------------------ ACCESS LOGGER ------------------ #
access_logger = logging.getLogger("access_logger")
access_logger.setLevel(logging.INFO)

if not access_logger.handlers:
    access_logger.addHandler(access_handler)

access_logger.propagate = False

# ------------------ ERROR LOGGER ------------------ #
error_logger = logging.getLogger("error_logger")
error_logger.setLevel(logging.WARNING)  # 

if not error_logger.handlers:
    error_logger.addHandler(error_handler)

error_logger.propagate = False

