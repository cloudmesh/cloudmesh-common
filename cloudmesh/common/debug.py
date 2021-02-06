from cloudmesh.common.variables import Variables
from cloudmesh.common.util import banner
from pprint import pformat
import inspect
import os
import threading
import sys
import traceback

verbose_lock = threading.Lock()


def TRACE():
    """
    prints the current trace stack
    """
    traceback.print_stack()


def tracefunc(frame, event, arg, indent=[0]):
    if event == "call":
        indent[0] += 2
        print("-" * indent[0] + "> call function", frame.f_code.co_name)
    elif event == "return":
        print("<" + "-" * indent[0], "exit function", frame.f_code.co_name)
        indent[0] -= 2
    return tracefunc


# sys.settrace(tracefunc)


# noinspection PyPep8Naming
def VERBOSE(msg, label=None, color="BLUE", verbose=9, location=True,
            secrets=["OS_PASSWORD",
                     "OS_USERNAME",
                     "client_secret",
                     "client_id",
                     "project_id",
                     "AZURE_TENANT_ID",
                     "AZURE_SUBSCRIPTION_ID",
                     "AZURE_APPLICATION_ID",
                     "AZURE_SECRET_KEY: TBD",
                     "EC2_ACCESS_ID: TBD",
                     "EC2_SECRET_KEY",
                     "MONGO_PASSWORD"]
            ):
    """
    Prints a data structure in verbose mode

    :param msg: the msg to be printed, can be a data structure such as a dict
    :param label: the  label to be used, defaults to the name of the msg variable
    :param color: the color
    :param verbose: indicates when to print it. If verbose in cloudmesh is
                    higher than the specified value it is printed
    :return:
    """

    _verbose = int(Variables()["verbose"] or 0)
    if _verbose >= verbose:

        verbose_lock.acquire()

        if label is None:
            label = inspect.stack()[1][4][0].strip().replace("VERBOSE(", "")
            label = label.split(",")[0][:-1]

        if location:
            cwd = os.getcwd()
            frame = inspect.stack()[1]
            module = inspect.getmodule(frame[0])
            filename = module.__file__.replace(cwd, ".")
            lineno = str(inspect.stack()[1][2]) + ":" + str(inspect.stack()[1][3])
            # print("# FILENAME:", filename, sep="")

        hline = "\n" + 70 * "-" + "\n"

        if type(msg) == dict and secrets is not None:
            tmp = dict(msg)
            for key in secrets:
                if key in tmp:
                    tmp[key] = "********"
            banner(lineno + " " + filename + hline + pformat(tmp),
                   label=label,
                   color=color)
        else:
            banner(lineno + " " + filename + hline + pformat(msg),
                   label=label,
                   color=color)

        verbose_lock.release()
