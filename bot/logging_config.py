"""Logging configuration for the trading bot."""

import logging
import logging.handlers
import os
import re
from pathlib import Path


class SecretRedactor(logging.Filter):
    """Redacts API keys and secrets from log messages."""

    SECRET_PATTERNS = [
        (re.compile(r'api_key[=:]\s*["\']?([^"\';\s]+)', re.IGNORECASE), r'api_key=[REDACTED]'),
        (re.compile(r'api_secret[=:]\s*["\']?([^"\';\s]+)', re.IGNORECASE), r'api_secret=[REDACTED]'),
        (re.compile(r'"api_key"\s*:\s*"([^"]+)"'), r'"api_key": "[REDACTED]"'),
        (re.compile(r'"api_secret"\s*:\s*"([^"]+)"'), r'"api_secret": "[REDACTED]"'),
    ]

    def filter(self, record):
        if isinstance(record.msg, str):
            for pattern, replacement in self.SECRET_PATTERNS:
                record.msg = pattern.sub(replacement, record.msg)
        if record.args:
            record.args = tuple(
                self._redact_arg(arg) if isinstance(arg, str) else arg
                for arg in record.args
            )
        return True

    def _redact_arg(self, arg):
        for pattern, replacement in self.SECRET_PATTERNS:
            arg = pattern.sub(replacement, arg)
        return arg


def setup_logging(log_dir: str = "logs", log_file: str = "trading_bot.log") -> None:
    """Configure logging with console and file handlers.

    Args:
        log_dir: Directory for log files.
        log_file: Name of the log file.
    """
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_format)

    file_handler = logging.handlers.RotatingFileHandler(
        log_path / log_file,
        maxBytes=2 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_format)

    redactor = SecretRedactor()
    console_handler.addFilter(redactor)
    file_handler.addFilter(redactor)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
