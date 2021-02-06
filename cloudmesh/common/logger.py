"""
simple logging convenience framework
"""
import logging
import os

from cloudmesh.common.location import Location
from cloudmesh.common.util import grep


# noinspection PyUnusedLocal,PyPep8Naming
def LOGGER(filename):
    """creates a logger with the given name.

    You can use it as follows::

       log = cloudmesh.common.LOGGER(__file__)
       log.error("this is an error")
       log.info("this is an info")
       log.warning("this is a warning")

    """
    pwd = os.getcwd()
    name = filename.replace(pwd, "$PWD")
    try:
        (first, name) = name.split("site-packages")
        name += "... site"
    except:
        pass

    loglevel = logging.CRITICAL
    try:
        location = Location()

        level = grep("loglevel:", location.file("cloudmesh_debug.yaml")) \
            .strip().split(":")[1].strip().lower()

        if level.upper() == "DEBUG":
            loglevel = logging.DEBUG
        elif level.upper() == "INFO":
            loglevel = logging.INFO
        elif level.upper() == "WARNING":
            loglevel = logging.WARNING
        elif level.upper() == "ERROR":
            loglevel = logging.ERROR
        else:
            level = logging.CRITICAL
    except:
        # print "LOGLEVEL NOT FOUND"
        loglevel = logging.DEBUG

    log = logging.getLogger(name)
    log.setLevel(loglevel)

    formatter = logging.Formatter(
        'CM {0:>50}:%(lineno)s: %(levelname)6s - %(message)s'.format(name))

    # formatter = logging.Formatter(
    #    'CM {0:>50}: %(levelname)6s - %(module)s:%(lineno)s %funcName)s: %(message)s'.format(name))
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log


# noinspection PyPep8Naming
def LOGGING_ON(log):
    """
    Switches logging on
    :param log: the logger for which we switch logging on
    """
    try:
        log.setLevel(logging.DEBUG)
        return True
    except:
        return False


# noinspection PyPep8Naming
def LOGGING_OFF(log):
    """
    Switches logging off
    :param log: the logger for which we switch logging off
    """
    try:
        log.setLevel(logging.CRITICAL)
        return True
    except:
        return False
