import logging

sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
# format: %H:%M:%S file_name:line_number message
sh.setFormatter(
    logging.Formatter(
        "%(asctime)s.%(msecs)03d %(filename)s:%(lineno)d %(message)s", "%H:%M:%S"
    )
)
logger = logging.getLogger("nagasaki")
logger.addHandler(sh)
logger.setLevel(logging.INFO)
