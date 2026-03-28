import logging
import logging.handlers
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "trading_bot.log"


class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG":    "\033[36m",
        "INFO":     "\033[32m",
        "WARNING":  "\033[33m",
        "ERROR":    "\033[31m",
        "CRITICAL": "\033[35m",
    }
    RESET = "\033[0m"
    BOLD  = "\033[1m"

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{self.BOLD}{record.levelname:<8}{self.RESET}"
        return super().format(record)


def setup_logging(level: str = "INFO"):
    logger = logging.getLogger("trading_bot")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if logger.handlers:
        logger.handlers.clear()

    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(
        fmt="[%(asctime)s] %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColorFormatter(
        fmt="[%(asctime)s] %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    ))
    console_handler.setLevel(logging.DEBUG)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


def get_logger(name: str):
    return logging.getLogger(f"trading_bot.{name}")