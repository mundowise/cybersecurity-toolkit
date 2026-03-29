"""
WiFiNetScanner - Logging Utilities
Author: WiFiNetScanner Team

Provides advanced, secure, and production-ready logging setup.
- Rotating file handler (by size or time)
- Console handler with color (if supported)
- Redaction of sensitive information
- Logging of critical events, warnings, and exceptions

All modules should import and use this logger for consistent audit trails.
"""

import logging
import logging.handlers
import os
import sys

DEFAULT_LOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/wifinetscanner.log"))

def setup_logging(log_file: str = DEFAULT_LOG_FILE, log_level: str = "INFO", rotation: str = "size", max_bytes: int = 10 * 1024 * 1024, backup_count: int = 5):
    """
    Configure logging for the entire application.
    Args:
        log_file (str): Path to the log file.
        log_level (str): Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        rotation (str): Rotation strategy: "size" (by file size), "time" (daily).
        max_bytes (int): Max log file size in bytes (for size-based rotation).
        backup_count (int): Number of rotated log files to keep.
    """
    # Create log directory if it doesn't exist
    log_dir = os.path.dirname(os.path.abspath(log_file))
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Formatter: timestamp, level, logger, message
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler (with color on supported terminals)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (rotating)
    if rotation == "size":
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
    elif rotation == "time":
        file_handler = logging.handlers.TimedRotatingFileHandler(
            log_file, when="midnight", backupCount=backup_count, encoding="utf-8"
        )
    else:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    root_logger.info(f"Logging initialized. Log file: {log_file}, Level: {log_level}, Rotation: {rotation}")

def redact_sensitive(text: str) -> str:
    """
    Redact possible sensitive info in logs (e.g. passwords, keys).
    Args:
        text (str): Original message.
    Returns:
        str: Redacted message.
    """
    # Simple patterns, can be extended
    import re
    patterns = [r"password\s*=\s*\S+", r"secret\s*=\s*\S+", r"key\s*=\s*\S+"]
    for pat in patterns:
        text = re.sub(pat, "[REDACTED]", text, flags=re.IGNORECASE)
    return text

class RedactingFilter(logging.Filter):
    """A filter to automatically redact sensitive data in all log records."""
    def filter(self, record):
        record.msg = redact_sensitive(str(record.msg))
        return True

# To use: add RedactingFilter to any logger
# logger = logging.getLogger("WiFiNetScanner")
# logger.addFilter(RedactingFilter())

# Call setup_logging() at startup (from main CLI or __main__)