import sys
from loguru import logger

logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="{time:HH:mm:ss.SSS} <green>{name}</green>:{line} <level>{message}</level>",
    filter={"nagasaki.clients": "INFO"},
)
logger.add(
    sys.stdout,
    colorize=True,
    format="{time:HH:mm:ss.SSS} {name}:{line} <level>{message}</level>",
    filter={"": "INFO", "nagasaki.clients": False},
)
