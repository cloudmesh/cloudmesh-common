from cloudmesh.common.variables import Variables
from cloudmesh.common.util import banner
from pprint import pformat
import inspect


# noinspection PyPep8Naming
def VERBOSE(msg, label=None, color="BLUE", verbose=9):
    """
    Prints a data structure in verbose mode

    :param msg: the msg to be printed, can be a datastructure suc as a dict
    :param label: the  label to be used, defaults to the name of the msg variable
    :param color: the color
    :param verbose: indicates when to print it. If verbose in cloudmesh is higher than the speified value it is printed
    :return:
    """
    if label is None:
        label = inspect.stack()[1][4][0].strip().replace("VERBOSE(", "")
        label = label.split(",")[0][:-1]

    _verbose = int(Variables()["verbose"] or 0)
    if _verbose >= verbose:
        banner(pformat(msg), label=label, color=color)
