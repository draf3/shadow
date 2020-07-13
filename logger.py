import os, logging
import config


logger = logging.getLogger(__name__)
logger.setLevel(config.logging_level)

console_handler = logging.StreamHandler()
console_handler.setLevel(config.logging_level)
console_handler.setFormatter(logging.Formatter(config.logger_mode))
logger.addHandler(console_handler)

if config.is_save_log:
    if not os.path.exists(config.LOG_DIR):
        os.makedirs(config.LOG_FILE)

    file_handler = logging.FileHandler(config.LOG_FILE)
    file_handler.setLevel(config.logging_level)
    file_handler.setFormatter(logging.Formatter(config.logger_mode))
    logger.addHandler(file_handler)