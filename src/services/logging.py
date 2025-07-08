import logging, os

LOGLEVEL = os.environ.get("WATCHDOG_LOGLEVEL", "INFO").upper()

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(LOGLEVEL)
    logger.propagate = False  # Prevent duplicate logs in Flask

    return logger
