"""
Logging utility - Single responsibility: Configure logging
"""
import logging
from pathlib import Path


def setup_logger(name, log_file, level='INFO'):
    """
    Configure and return a logger instance
    
    Args:
        name: Logger name
        log_file: Path to log file
        level: Logging level
        
    Returns:
        logging.Logger: Configured logger
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))
    
    # File handler
    log_file = Path(log_file)
    log_file.parent.mkdir(exist_ok=True)
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name='powerbi_automation'):
    """
    Get or create logger instance
    
    Args:
        name: Logger name
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)

