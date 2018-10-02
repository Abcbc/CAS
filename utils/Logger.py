import os
from logging import *

import sys

log_file = ""
format = Formatter('%(asctime)s:%(module)s -> %(levelname)s:%(message)s')
cmd_level = DEBUG
file_level = DEBUG
log_dir = "".join([os.getcwd(), "/logs/"])


ae_logger = []


def get_logger(name=None, filepath=None):
    """

    :param name:
    :param filepath:
    :return:
    """
    global log_file
    if name == "__main__":
        print(filepath)
        log_file = filepath.rsplit("/")[-1].replace(".py", ".log")
    elif name == "__mp_main__":
        log_file= "mp_dump.log"
    log_name = __name__
    if name is not None:
        log_name = "".join([name,log_name])
    logger = Logger(log_name)

    cmd_handler = StreamHandler(sys.stdout)
    cmd_handler.setFormatter(format)
    cmd_handler.setLevel(cmd_level)

    file_handler = FileHandler("".join([log_dir, log_file]))
    file_handler.setFormatter(format)
    file_handler.setLevel(file_level)

    logger.addHandler(cmd_handler)
    logger.addHandler(file_handler)

    return logger

def change_logfile(filename):
    """

    :param filename:
    """
    global log_file
    log_file = "".join([filename,".log"])