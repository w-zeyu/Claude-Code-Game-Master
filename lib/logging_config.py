#!/usr/bin/env python3
"""
Centralized logging configuration for DM modules.
Provides consistent logging across all Python modules.
"""

import logging
import sys
import os
from typing import Optional


def setup_logging(level: Optional[int] = None, name: str = 'dm') -> logging.Logger:
    """Configure logging for DM modules.

    Args:
        level: Logging level. Defaults to INFO, or reads from DM_LOG_LEVEL env var.
        name: Logger name. Defaults to 'dm'.

    Returns:
        Configured logger instance.
    """
    # Get level from environment if not specified
    if level is None:
        env_level = os.environ.get('DM_LOG_LEVEL', 'INFO').upper()
        level = getattr(logging, env_level, logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        '[%(levelname)s] %(name)s: %(message)s'
    )

    # Create handler for stderr
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)

    # Get or create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding duplicate handlers
    if not logger.handlers:
        logger.addHandler(handler)

    return logger


def get_logger(module_name: str) -> logging.Logger:
    """Get a logger for a specific module.

    Args:
        module_name: Name of the module (e.g., 'npc_manager', 'session_manager')

    Returns:
        Logger instance for the module.
    """
    return logging.getLogger(f'dm.{module_name}')


# Initialize root logger on import
_root_logger = setup_logging()


class DMLogger:
    """Convenience class for module-level logging that matches existing print patterns.

    Usage:
        from logging_config import DMLogger
        log = DMLogger('npc_manager')

        log.success("Created NPC: Grimjaw")  # [SUCCESS] dm.npc_manager: Created NPC: Grimjaw
        log.error("NPC not found")           # [ERROR] dm.npc_manager: NPC not found
        log.info("Processing...")            # [INFO] dm.npc_manager: Processing...
        log.warning("Low HP!")               # [WARNING] dm.npc_manager: Low HP!
    """

    def __init__(self, module_name: str):
        self.logger = get_logger(module_name)
        self.module_name = module_name

    def success(self, message: str):
        """Log a success message (INFO level with [SUCCESS] prefix)."""
        # For now, print to stdout to match existing behavior
        print(f"[SUCCESS] {message}")

    def error(self, message: str):
        """Log an error message."""
        print(f"[ERROR] {message}", file=sys.stderr)
        self.logger.error(message)

    def warning(self, message: str):
        """Log a warning message."""
        print(f"[WARNING] {message}", file=sys.stderr)
        self.logger.warning(message)

    def info(self, message: str):
        """Log an info message."""
        print(f"[INFO] {message}")
        self.logger.info(message)

    def debug(self, message: str):
        """Log a debug message (only shown when DM_LOG_LEVEL=DEBUG)."""
        self.logger.debug(message)


# Convenience function for quick logging
def log_success(message: str):
    """Print a success message."""
    print(f"[SUCCESS] {message}")


def log_error(message: str):
    """Print an error message to stderr."""
    print(f"[ERROR] {message}", file=sys.stderr)


def log_warning(message: str):
    """Print a warning message to stderr."""
    print(f"[WARNING] {message}", file=sys.stderr)


def log_info(message: str):
    """Print an info message."""
    print(f"[INFO] {message}")
