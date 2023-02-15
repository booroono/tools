import logging
import logging.handlers
import os
import time

fileMaxByte = 1024 * 1024 * 10  # 10MB
fileName = 'log/log.log'
consolLevel = logging.DEBUG
fileLevel = logging.DEBUG


def get_logger(name="My Logger"):
    # 1 logger instance를 만든다.
    logger = logging.getLogger(name)

    if len(logger.handlers) > 0:
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - [%(levelname)s|%(filename)s|%(funcName)s:%(threadName)s:%(lineno)s] > %(message)s")

    if not os.path.isdir('log'):
        os.mkdir('log')
    localtime = time.localtime()
    filename = f"log/{localtime.tm_year}{localtime.tm_mon:02d}{localtime.tm_mday:02d}_log.log"

    console = logging.StreamHandler()
    file_handler = logging.handlers.RotatingFileHandler(filename, maxBytes=fileMaxByte, backupCount=10)

    console.setLevel(consolLevel)
    file_handler.setLevel(fileLevel)

    console.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console)
    logger.addHandler(file_handler)

    return logger

logger = get_logger("My Logger")