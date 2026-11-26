"""
Simple logger for the Raspberry Pi Agent
"""

import logging
import sys

def setup_logger(name: str = "ad_agent", level: str = "INFO") -> logging.Logger:
                                             
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    logger.setLevel(numeric_level)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
