import logging

from colorama import Fore, Style

from entities.config import get_instance as get_config


class CustomFormatter(logging.Formatter):

    format = "[{asctime}] [{levelname:<8}] {name}: {message} ({filename}:{lineno})"
    dt_fmt = "%Y-%m-%d %H:%M:%S"

    FORMATS = {
        logging.DEBUG: Fore.CYAN + format + Style.RESET_ALL,
        logging.INFO: Fore.BLUE + format + Style.RESET_ALL,
        logging.WARNING: Fore.YELLOW + format + Style.RESET_ALL,
        logging.ERROR: Fore.RED + format + Style.RESET_ALL,
        logging.CRITICAL: Fore.LIGHTRED_EX + format + Style.RESET_ALL,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, self.dt_fmt, style="{")
        return formatter.format(record)


def get_logger(name, lvl=get_config().loglevel):
    logger = logging.getLogger(name)
    logger.setLevel(lvl)

    ch = logging.StreamHandler()
    ch.setLevel(lvl)

    ch.setFormatter(CustomFormatter())

    logger.addHandler(ch)

    return logger
