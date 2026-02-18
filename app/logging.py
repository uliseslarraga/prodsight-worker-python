import logging
from pythonjsonlogger import jsonlogger

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    fmt = "%(asctime)s %(levelname)s %(name)s %(message)s"
    formatter = jsonlogger.JsonFormatter(fmt)
    handler.setFormatter(formatter)
    logger.handlers.clear()
    logger.addHandler(handler)
