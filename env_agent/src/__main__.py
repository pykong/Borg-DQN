import sys

from loguru import logger

from .config import create_config
from .loop import loop

if __name__ == "__main__":
    config = create_config()

    # configure logger
    logger.remove(0)
    logger.add(sys.stdout, level=config.log_level)

    loop(config)
