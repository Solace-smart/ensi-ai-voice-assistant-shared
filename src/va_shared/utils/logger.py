import logging
from typing import Dict

_loggers: Dict[str, logging.Logger] = {}

def get_logger(name: str) -> logging.Logger:
    """Get or create a logger with the given name."""
    if name in _loggers:
        return _loggers[name]
    
    logger = logging.getLogger(name)
    
    # Only add handlers if they don't exist
    if not logger.handlers:
        # Remove any existing handlers to prevent duplication
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Don't propagate to root logger (prevents double logging)
        logger.propagate = False
        
        # Add our custom formatter only if we're not in Home Assistant
        if not any(handler for handler in logger.handlers if isinstance(handler, logging.StreamHandler)):
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%y-%m-%d %H:%M:%S'
            )
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            logger.addHandler(handler)
    
    _loggers[name] = logger
    return logger
