#
# TODO: THIS REQUIRES CMD5 OR VARIABLES TO BE HERE
#
from cloudmesh.variables import Variables
from cloudmesh.common.util import banner
from pprint import pformat
from pprint import pprint
import inspect


# noinspection PyPep8Naming
def VERBOSE(msg, label=None, color="BLUE", verbose=9):
    if label is None:
        label = inspect.stack()[1][4][0].strip().replace("VERBOSE(", "")
        label = label.split(",")[0][:-1]

    _verbose = int(Variables()["verbose"] or 0)
    if _verbose >= verbose:
        banner(pformat(msg), label=label, color=color)
