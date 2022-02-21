"""
Class for starting and stopping named timers.

"""
import os
import time
from pprint import pprint

from cloudmesh.common.Tabulate import Printer
from cloudmesh.common.systeminfo import systeminfo as cm_systeminfo

def rename(newname):
    """
    decorator to rename a function
    :param newname: function name
    :type newname: str
    :return: renamed function
    :rtype: object
    """
    def decorator(f):
        f.__name__ = newname
        return f
    return decorator

def benchmark(func):
    """
    decorator to benchmark a function
    :param func: function
    :type func: object
    :return: function with benchmarks based on the name of the function
    :rtype: object
    """
    @rename(func.__name__)
    def wrapper(*args, **kwargs):
        StopWatch.start(func.__name__)
        func(*args, **kwargs)
        StopWatch.stop(func.__name__)
    return wrapper

class StopWatch(object):
    """
    A class to measure times between events.
    """
    debug = False
    verbose = True
    # Timer start dict
    timer_start = {}
    # Timer end dict
    timer_end = {}
    # Timer diff
    timer_elapsed = {}
    # records a status
    timer_status = {}
    # records a dt
    timer_sum = {}
    # msg
    timer_msg = {}

    @classmethod
    def keys(cls):
        """returns the names of the timers"""
        return list(cls.timer_end.keys())

    @classmethod
    def status(cls, name, value):
        """
        starts a timer with the given name.

        :param name: the name of the timer
        :type name: string
        :param value: value of the nameed of a status
        :type value: bool

        """
        if cls.debug:
            print("Timer", name, "status", value)
        cls.timer_status[name] = value

    @classmethod
    def get_message(cls, name):
        """
        starts a timer with the given name.

        :param name: the name of the timer
        :type name: string

        """
        return cls.timer_msg[name]

    @classmethod
    def message(cls, name, value):
        """
        starts a timer with the given name.

        :param name: the name of the timer
        :type name: string
        :param value: the value of the message
        :type value: bool

        """
        cls.timer_msg[name] = value


    @classmethod
    def start(cls, name):
        """
        starts a timer with the given name.

        :param name: the name of the timer
        :type name: string
        """
        if cls.debug:
            print("Timer", name, "started ...")
        if name not in cls.timer_sum:
            cls.timer_sum[name] = 0.0
        cls.timer_start[name] = time.time()
        cls.timer_end[name] = None
        cls.timer_status[name] = None
        cls.timer_msg[name] = None

    @classmethod
    def stop(cls, name, state=True):
        """
        stops the timer with a given name.

        :param name: the name of the timer
        :type name: string
        """
        cls.timer_end[name] = time.time()
        # if cumulate:
        #    cls.timer_end[name] = cls.timer_end[name] + cls.timer_last[name]
        cls.timer_sum[name] = cls.timer_sum[name] + cls.timer_end[name] - cls.timer_start[name]
        cls.timer_status[name] = state

        if cls.debug:
            print("Timer", name, "stopped ...")

    @classmethod
    def get_status(cls, name):
        """
        sets the status of the timer with a given name.

        :param name: the name of the timer
        :type name: string
        """
        return cls.timer_status[name]

    # noinspection PyPep8
    @classmethod
    def get(cls, name, digits=4):
        """
        returns the time of the timer.

        :param name: the name of the timer
        :type name: string
        :rtype: the elapsed time
        """
        if name in cls.timer_end:
            try:
                diff = cls.timer_end[name] - cls.timer_start[name]
                if round is not None:
                    cls.timer_elapsed[name] = round(diff, digits)
                else:
                    cls.timer_elapsed[name] = diff
                return cls.timer_elapsed[name]
            except:  # noqa: E722
                return None
        else:
            return "undefined"

    @classmethod
    def sum(cls, name, digits=4):
        """
        returns the sum of the timer if used multiple times

        :param name: the name of the timer
        :type name: string
        :rtype: the elapsed time
        """
        if name in cls.timer_end:
            try:
                diff = cls.timer_sum[name]
                if round is not None:
                    return round(diff, digits)
                else:
                    return diff
            except:  # noqa: E722
                return None
        else:
            return "undefined"

    @classmethod
    def clear(cls):
        """
        clear start and end timer_start
        """
        cls.timer_start.clear()
        cls.timer_end.clear()
        cls.timer_sum.clear()
        cls.timer_status.clear()
        cls.timer_elapsed.clear()
        cls.timer_msg.clear()

    @classmethod
    def print(cls, *args):
        """
        prints a timer. The first argument is the label if it exists, the last is the timer
        :param args: label, name
        :return:
        """
        if cls.verbose:
            if len(args) == 2:
                print(args[0], str("{0:.2f}".format(cls.get(args[1]))), "s")
            else:
                raise Exception("StopWatch: wrong number of arguments")

    @classmethod
    def __str__(cls):
        """
        returns the string representation of the StopWatch
        :return: string of the StopWatch
        :rtype: str
        """
        s = ""
        for t in cls.timer_end:
            data = {"label": t,
                    "start": str(cls.timer_start[t]),
                    "end": str(cls.timer_end[t]),
                    "status": str(cls.timer_status[t]),
                    "elapsed": str(cls.get(t)),
                    "newline": os.linesep}
            s += "{label} {start} {end} {elapsed} {status} {newline}".format(
                **data)
        return s

    @classmethod
    def systeminfo(cls, data=None):
        """
        Print information about the system

        :param data: additional data to be integrated
        :type data: dict
        :return: a table with data
        :rtype: str
        """
        data_platform = cm_systeminfo()
        if data is not None:
            data_platform.update(data)
        return Printer.attribute(
            data_platform,
            order=["Machine Attribute", "Value"],
            output="table"
        )

    @classmethod
    def benchmark(cls,
                  sysinfo=True,
                  csv=True,
                  prefix="# csv",
                  tag=None,
                  sum=True,
                  node=None,
                  user=None,
                  attributes=None,
                  total=False):
        """
        prints out all timers in a convenient benchmark table

        :param sysinfo: controls if system info shoul be printed.
        :type sysinfo: bool
        :param csv: contols if the data should be printed also as csv strings
        :type csv: bool
        :param prefix: The prefix used for the csv string
        :type prefix: str
        :param tag: overwrites the tag
        :type tag: str
        :param sum: prints the sums (not used)
        :type sum: bool
        :param node: overwrites the name of the node
        :type node: str
        :param user: overwrites the name of the user
        :type user: str
        :param attributes: list of additional attributes to print
        :type attributes: list
        :return: prints the information
        :rtype: stdout
        """

        #
        # PRINT PLATFORM
        #

        print()
        data_platform = cm_systeminfo()
        if sysinfo:
            if node is not None:
                data_platform["uname.node"] = node
            if user is not None:
                data_platform["user"] = user

            print(Printer.attribute(
                data_platform,
                order=["Machine Attribute", "Value"],
                output="table"
            ))

        #
        # PRINT TIMERS
        #
        timers = StopWatch.keys()
        total_time = 0.0
        if len(timers) > 0:

            data_timers = {}
            for timer in timers:
                data_timers[timer] = {
                    'start': time.strftime("%Y-%m-%d %H:%M:%S",
                                           time.gmtime(
                                               StopWatch.timer_start[timer])),
                    'time': StopWatch.get(timer, digits=3),
                    'sum': StopWatch.sum(timer, digits=3),
                    'status': StopWatch.get_status(timer),
                    'msg': StopWatch.get_message(timer),
                    'timer': timer,
                    'tag': tag or ''
                }
                total_time = total_time + StopWatch.get(timer)

                for attribute in ["uname.node",
                                  "user",
                                  "uname.system",
                                  "uname.machine",
                                  "platform.version",
                                  "sys.platform"]:
                    if attribute == "user" and user is not None:
                        data_timers[timer][attribute] = user
                    elif attribute == "uname.node" and node is not None:
                        data_timers[timer][attribute] = node
                    else:
                        data_timers[timer][attribute] = data_platform[attribute]


            # print(Printer.attribute(data_timers, header=["Command", "Time/s"]))

            if 'benchmark_start_stop' in data_timers:
                del data_timers['benchmark_start_stop']

            for key in data_timers:
                if key != 'benchmark_start_stop' and data_timers[key]['status'] is None:
                    data_timers[key]['status'] = "failed"
                elif data_timers[key]['status'] is not None and data_timers[key]['status']:
                    data_timers[key]['status'] = "ok"

            if attributes is None:
                order = [
                    "timer",
                    "status",
                    "time",
                    "sum",
                    "start",
                    "tag",
                    "msg",
                    "uname.node",
                    "user",
                    "uname.system",
                    "platform.version"
                ]

                header = [
                    "Name",
                    "Status",
                    "Time",
                    "Sum",
                    "Start",
                    "tag",
                    "msg",
                    "Node",
                    "User",
                    "OS",
                    "Version"
                ]
            elif attributes == "short":
                order = [
                    "timer",
                    "status",
                    "time"
                ]

                header = [
                    "Name",
                    "Status",
                    "Time"
                ]
            print()
            print(Printer.write(
                data_timers,
                order=order,
                header=header,
                output="table"

            ))
            if total:
                print("Total:", total_time)
            print()

            if csv:
                if prefix is not None:
                    for entry in data_timers:
                        data_timers[entry]["# csv"] = prefix

                    order = ["# csv"] + order

                    print(Printer.write(
                        data_timers,
                        order=order,
                        header=header,
                        output="csv"
                    ))
                else:

                    pprint(data_timers)

                    print(Printer.write(
                        data_timers,
                        order=order[1:],
                        output="csv"
                    ))

        else:

            print("ERROR: No timers found")
