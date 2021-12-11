import logging
from datetime import datetime


def log(message: str = "", level: str = "error"):
    loggers = {
        "error": logging.error,
        "warn": logging.warning,
        "info": logging.info,
        "debug": logging.debug,
        "critical": logging.critical,
    }
    dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    loggers["info"]("[%s][%s]: %s" % (dt, "INFO", "LOGGGING"))
    loggers[level]("[%s][%s]: %s" % (dt, str(level).upper(), str(message)))
    loggers["info"]("[%s][%s]: %s" % (dt, "INFO", "LOGGGING"))
