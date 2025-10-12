import logging
import logging.handlers
import sys
from pathlib import Path

from core.config import config


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log levels."""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'             # Reset color
    
    def format(self, record):
        # Get the original formatted message
        message = super().format(record)
        
        # Add color to the level name
        if record.levelname in self.COLORS:
            colored_level = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
            # Replace the level name in the message with the colored version
            message = message.replace(record.levelname, colored_level, 1)
        
        return message


def setup_logging() -> None:
    """
    Configure logging for the application based on environment settings.
    
    - Development: INFO level to console
    - Production: WARNING level to file and console
    - Debug mode: DEBUG level to console
    """
    
    # Get log level from config
    log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
    
    # If DEBUG is enabled, use DEBUG level
    if config.DEBUG:
        log_level = logging.DEBUG
    
    # Create formatters
    colored_formatter = ColoredFormatter(config.LOG_FORMAT)
    plain_formatter = logging.Formatter(config.LOG_FORMAT)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Console handler (always present) - use colored formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(colored_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if LOG_FILE is configured)
    if config.LOG_FILE:
        log_file_path = Path(config.LOG_FILE)
        
        # Create logs directory if it doesn't exist
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Use RotatingFileHandler for production
        file_handler = logging.handlers.RotatingFileHandler(
            log_file_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(plain_formatter)  # No colors in log files
        root_logger.addHandler(file_handler)
    
    # Configure specific loggers
    _configure_third_party_loggers()

    # Log the logging configuration
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured - Level: {logging.getLevelName(log_level)}")
    if config.LOG_FILE:
        logger.info(f"Log file: {config.LOG_FILE}")


def _configure_third_party_loggers() -> None:
    """Configure logging levels for third-party libraries."""
    
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.INFO)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    
    # In debug mode, show more detail from our application
    if config.DEBUG:
        logging.getLogger("app").setLevel(logging.DEBUG)
        logging.getLogger("core").setLevel(logging.DEBUG)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
