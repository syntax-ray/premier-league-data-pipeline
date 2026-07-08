import logging
import os
from consts import LOGGING_DIR
from datetime import datetime

_LOG_FILE = None

def create_log_directory():
    os.makedirs(LOGGING_DIR, exist_ok=True)

def create_log_filename():
    current_day = datetime.now()  
    file_name = f'{current_day.strftime("%Y-%m-%d_%H:%M:%S")}.log'
    return os.path.join(LOGGING_DIR, file_name)

def _configure_logfile():
    global _LOG_FILE
    if not _LOG_FILE:
        _LOG_FILE = create_log_filename()
    else:
        return
        

def get_logger(name, level=logging.INFO):
    """
    Return a configured logger.
    """
    create_log_directory()
    _configure_logfile()
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger
    
    formatter = logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")

    # file handler
    file_handler = logging.FileHandler(_LOG_FILE)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    # stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


    return logger
    
