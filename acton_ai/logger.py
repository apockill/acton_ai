import logging

logger = logging.getLogger("acton")
logging.getLogger("pymycobot.myarm_api").setLevel(logging.ERROR)
logging.basicConfig()
