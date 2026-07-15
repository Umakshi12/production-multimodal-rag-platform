"""Logging utility for the chatbot"""

import logging
import os
from config import LOG_LEVEL, LOG_FILE

# Create logs directory
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def get_logger(name):
    """Get a logger instance"""
    return logging.getLogger(name)
