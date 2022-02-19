import logging

sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
logger = logging.getLogger("nagasaki")
logger.addHandler(sh)
logger.setLevel(logging.INFO)
