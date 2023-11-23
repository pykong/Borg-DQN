import sys
from typing import Final

from loguru import logger

from .monitor import monitor


LOG_LEVEL: Final[str] = "DEBUG"

# configure logger
logger.remove(0)
logger.add(sys.stdout, level=LOG_LEVEL)
logger.add("/usr/share/logs/monitor.log",
    level=LOG_LEVEL,
    colorize=False,
    backtrace=True,
    diagnose=True,
)


if __name__ == "__main__":
    monitor()
