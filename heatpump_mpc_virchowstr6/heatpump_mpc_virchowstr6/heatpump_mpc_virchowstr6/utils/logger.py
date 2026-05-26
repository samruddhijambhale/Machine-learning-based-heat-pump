"""Simple logging setup"""
import logging
import sys

def setup_logger(name='MPC', level=logging.INFO):
    """Setup logger with console output"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s',
                                     datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
