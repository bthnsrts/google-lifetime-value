import logging
import pathlib
from datetime import datetime

def setup_logger(name='preprocess'):

    # Create a log directory 
    log_dir = pathlib.Path('').resolve() / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y.%m.%d_%H:%M:%S")
    log_filename = log_dir / f"{name}_{timestamp}.log"

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)    

    # Remove existing handlers if any
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Create file handler
    file_handler = logging.FileHandler(log_filename)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    
    # Create formatter and add to handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)   

    logger.info(f"Logging initialized. Log file: {log_filename}")
    
    return logger