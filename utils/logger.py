"""
Comprehensive logging system for biometric security research.
Provides structured logging with file rotation, filtering, and performance monitoring.
"""

import logging
import logging.handlers
import sys
import time
import functools
from pathlib import Path
from typing import Optional, Callable, Any
from datetime import datetime
import traceback


class ColoredFormatter(logging.Formatter):
    """
    Colored console log formatter for better readability
    """

    COLORS = {
        'DEBUG': '\033[36m',  # Cyan
        'INFO': '\033[32m',   # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',  # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    BOLD = '\033[1m'

    def format(self, record):
        """Format log record with colors"""
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{self.BOLD}{levelname}{self.RESET}"

        # Format the message
        result = super().format(record)

        return result


class PerformanceFilter(logging.Filter):
    """
    Filter to add performance metrics to log records
    """

    def filter(self, record):
        """Add performance data to record"""
        record.funcName = getattr(record, 'funcName', 'unknown')
        return True


class SecurityLogger:
    """
    Enhanced logger for security-sensitive operations
    """

    def __init__(self, name: str, config=None):
        """
        Initialize security logger

        Args:
            name: Logger name
            config: LoggingConfig instance (uses default if None)
        """
        self.logger = logging.getLogger(name)

        # Import config here to avoid circular imports
        if config is None:
            from config import get_config
            config = get_config().logging

        self.config = config

        # Clear existing handlers to avoid duplicates
        self.logger.handlers.clear()
        self.logger.setLevel(getattr(logging, config.level))

        # Create logs directory
        Path(config.log_file).parent.mkdir(parents=True, exist_ok=True)

        # Add console handler
        if config.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, config.level))

            # Use colored formatter for console
            console_formatter = ColoredFormatter(
                '%(levelname)s - %(name)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

        # Add file handler with rotation
        if config.enable_file:
            file_handler = logging.handlers.RotatingFileHandler(
                config.log_file,
                maxBytes=config.max_bytes,
                backupCount=config.backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(getattr(logging, config.level))

            # Use standard formatter for file
            file_formatter = logging.Formatter(config.log_format)
            file_handler.setFormatter(file_formatter)
            file_handler.addFilter(PerformanceFilter())
            self.logger.addHandler(file_handler)

    def debug(self, msg: str, *args, **kwargs):
        """Log debug message"""
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        """Log info message"""
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        """Log warning message"""
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        """Log error message"""
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        """Log critical message"""
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs):
        """Log exception with traceback"""
        self.logger.exception(msg, *args, **kwargs)

    def security_event(self, event_type: str, details: dict):
        """
        Log security-sensitive event

        Args:
            event_type: Type of security event
            details: Event details dictionary
        """
        timestamp = datetime.now().isoformat()
        log_msg = f"SECURITY EVENT [{event_type}] at {timestamp}: {details}"
        self.logger.warning(log_msg, extra={'event_type': event_type, 'details': details})

    def audit_log(self, action: str, user: str, resource: str, result: str):
        """
        Log audit trail for compliance

        Args:
            action: Action performed
            user: User identifier
            resource: Resource accessed
            result: Action result (success/failure)
        """
        timestamp = datetime.now().isoformat()
        audit_msg = f"AUDIT: user={user}, action={action}, resource={resource}, result={result}, time={timestamp}"
        self.logger.info(audit_msg)


def get_logger(name: str) -> SecurityLogger:
    """
    Get a configured logger instance

    Args:
        name: Logger name (typically __name__)

    Returns:
        SecurityLogger: Configured logger
    """
    return SecurityLogger(name)


def log_execution_time(logger: Optional[SecurityLogger] = None):
    """
    Decorator to log function execution time

    Args:
        logger: Logger instance (creates new one if None)

    Usage:
        @log_execution_time()
        def my_function():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = get_logger(func.__module__)

            start_time = time.time()
            func_name = f"{func.__module__}.{func.__name__}"

            logger.debug(f"Starting {func_name}")

            try:
                result = func(*args, **kwargs)
                elapsed_time = time.time() - start_time

                logger.debug(f"Completed {func_name} in {elapsed_time:.3f}s")

                return result

            except Exception as e:
                elapsed_time = time.time() - start_time
                logger.error(
                    f"Failed {func_name} after {elapsed_time:.3f}s: {str(e)}\n{traceback.format_exc()}"
                )
                raise

        return wrapper
    return decorator


def log_exceptions(logger: Optional[SecurityLogger] = None):
    """
    Decorator to log exceptions

    Args:
        logger: Logger instance (creates new one if None)

    Usage:
        @log_exceptions()
        def my_function():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = get_logger(func.__module__)

            try:
                return func(*args, **kwargs)
            except Exception as e:
                func_name = f"{func.__module__}.{func.__name__}"
                logger.exception(f"Exception in {func_name}: {str(e)}")
                raise

        return wrapper
    return decorator


class LogContext:
    """
    Context manager for logging operations with automatic success/failure logging

    Usage:
        with LogContext('enrolling user', logger) as ctx:
            # perform operation
            ctx.add_data('user_id', 'alice')
    """

    def __init__(self, operation: str, logger: SecurityLogger):
        """
        Initialize log context

        Args:
            operation: Operation description
            logger: Logger instance
        """
        self.operation = operation
        self.logger = logger
        self.start_time = None
        self.data = {}

    def __enter__(self):
        """Enter context"""
        self.start_time = time.time()
        self.logger.info(f"Starting {self.operation}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context"""
        elapsed = time.time() - self.start_time

        if exc_type is None:
            # Success
            self.logger.info(
                f"Successfully completed {self.operation} in {elapsed:.3f}s",
                extra=self.data
            )
        else:
            # Failure
            self.logger.error(
                f"Failed {self.operation} after {elapsed:.3f}s: {exc_val}",
                extra=self.data
            )

        return False  # Don't suppress exceptions

    def add_data(self, key: str, value: Any):
        """Add data to log context"""
        self.data[key] = value


# Module-level logger for utils
logger = get_logger(__name__)
