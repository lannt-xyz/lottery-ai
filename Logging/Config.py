import logging
from logging.handlers import TimedRotatingFileHandler

def configure_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        handler = TimedRotatingFileHandler('/app/logs/app.log', when='midnight', interval=1, backupCount=5)
        handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger
