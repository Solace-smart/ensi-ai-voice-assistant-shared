import datetime
import logging
import os
import pathlib
from typing import Dict, Optional

_loggers: Dict[str, logging.Logger] = {}

def get_next_log_directory(base_dir: pathlib.Path) -> pathlib.Path:
    """Find or create the next available log directory."""
    # Create base directory and agent_runs subdirectory if they don't exist
    base_dir.mkdir(exist_ok=True)
    agent_runs_dir = base_dir / "agent_runs"
    agent_runs_dir.mkdir(exist_ok=True)

    # List existing directories
    existing_dirs = [d for d in agent_runs_dir.iterdir() if d.is_dir() and d.name.isdigit()]

    if not existing_dirs:
        # No directories yet, create first one
        new_dir = agent_runs_dir / "001"
        new_dir.mkdir(exist_ok=True)
        return new_dir

    # Find the latest directory
    latest_dir = max(existing_dirs, key=lambda d: int(d.name))
    latest_num = int(latest_dir.name)

    # Count files in the latest directory
    file_count = len([f for f in latest_dir.iterdir() if f.is_file()])

    if file_count < 30:
        # Current directory has space
        return latest_dir
    else:
        # Create new directory with incremented number
        new_dir = agent_runs_dir / f"{latest_num + 1:03d}"
        new_dir.mkdir(exist_ok=True)
        return new_dir

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
        # If log_file is in a "logs" directory, organize into numbered subdirectories
        parent_dir = log_file.parent
        if parent_dir.name.lower() == "logs":
            # Get the appropriate numbered directory
            log_dir = get_next_log_directory(parent_dir)
            # Update log_file path to be in the numbered directory
            log_file = log_dir / log_file.name

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    _loggers[name] = logger
    return logger
