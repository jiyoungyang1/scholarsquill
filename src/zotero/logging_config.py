"""
Logging configuration for Zotero integration.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_zotero_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    console_output: bool = True
) -> logging.Logger:
    """
    Configure logging for Zotero integration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        console_output: Whether to output logs to console

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("scholarsquill.zotero")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    logger.handlers = []

    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Add console handler if requested
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Add file handler if log file specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # File gets all logs
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "scholarsquill.zotero") -> logging.Logger:
    """
    Get logger instance for Zotero components.

    Args:
        name: Logger name (sub-module)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Pre-configured logger for quick access
zotero_logger = get_logger()
