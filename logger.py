import logging

from rich.logging import RichHandler

logger = logging.getLogger("anyinference")
logger.setLevel(logging.INFO)
rich_handler = RichHandler()
formatter = logging.Formatter(fmt="%(message)s", datefmt="[%X]")
rich_handler.setFormatter(formatter)
logger.addHandler(rich_handler)
