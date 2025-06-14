import logging
import time
from pathlib import Path


def set_logger_config(log_file_path: Path) -> None:
    fmt = "%(asctime)s %(name)s %(levelname)s: %(message)s"
    logging_formatter = logging.Formatter(fmt)
    logging_formatter.converter = time.gmtime
    level = logging.INFO

    logger = logging.getLogger()
    logger.setLevel(level)

    if len(logger.handlers):
        logger.handlers.clear()
        logger.root.handlers.clear()

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(logging_formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(level)
    file_handler.setFormatter(logging_formatter)
    logger.addHandler(file_handler)

    # turn off logs for botocore
    logging.getLogger("botocore").setLevel(logging.CRITICAL)
