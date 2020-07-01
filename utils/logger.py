import logging

from config import LOG_FILE, LOGGING_LEVEL, LOGGER_MODE

logging_level = LOGGING_LEVEL['DEBUG']
logger_mode = LOGGER_MODE['ALL']
is_save_log = False

logger = logging.getLogger(__name__)
logger.setLevel(logging_level)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging_level)
console_handler.setFormatter(logging.Formatter(logger_mode))
logger.addHandler(console_handler)

if is_save_log:
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging_level)
    file_handler.setFormatter(logging.Formatter(logger_mode))
    logger.addHandler(file_handler)