"""
Logging module

"""

import logging
import sys

import app_config


FORMATTER = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def get_console_handler():
    """
    Console Handler
    """
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_logger(logger_name):
    """
    Initiating logger with custom formatter and handler
    """
    logger = logging.getLogger(logger_name)

    logger.setLevel(app_config.LOG_LEVEL)
    logger.addHandler(get_console_handler())

    # with this pattern, it's rarely necessary to propagate
    # the error up to parent
    logger.propagate = False

    return logger
