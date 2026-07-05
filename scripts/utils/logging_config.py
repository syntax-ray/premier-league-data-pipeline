import logging

from consts import LOGGING_FILE

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    filename=LOGGING_FILE,
)


def get_logger(name):
    """
    Return a configured logger.
    """
    return logging.getLogger(name)