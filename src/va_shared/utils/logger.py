import datetime
import logging
import pathlib
from typing import Dict, Optional

_loggers: Dict[str, logging.Logger] = {}

def get_logger(name: str, log_file: Optional[pathlib.Path] = None) -> logging.Logger:
    """Get or create a logger with the given name."""
    logger = _loggers.get(name)

    if logger:
        # Remove any existing file handlers
        for handler in logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                logger.removeHandler(handler)
    else:
        logger = logging.getLogger(name)
        # Don't propagate to root logger (prevents double logging)
        logger.propagate = False

        # Add console handler if not present
        if not any(isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler) for h in logger.handlers):
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

    # Add new file handler if provided
    if log_file:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    _loggers[name] = logger
    return logger
