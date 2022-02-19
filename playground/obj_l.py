import logging

l = logging.getLogger("cipa")
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
l.setLevel(logging.DEBUG)
l.addHandler(ch)
l.critical("cipa_critical")
l.error("cipa_error")
l.warning("cipa_warning")
l.info("cipa_info")
l.debug("cipa_debug")
