from utils.Logger import *
log = get_logger(__name__)

class Test:
    def __init__(self):
        print("Test Class")
        log.debug("Test Class")
