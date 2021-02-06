"""
Class for starting and stopping named timers.

"""
import multiprocessing
import os
import time
from pprint import pprint

from cloudmesh.common.Tabulate import Printer
from cloudmesh.common.systeminfo import systeminfo


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
        :param status: the name of a status
        :type status: bool

        """
        if cls.debug:
            print("Timer", name, "status", value)
        cls.timer_status[name] = value

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

    @classmethod
    def stop(cls, name):
        """
        stops the timer with a given name.

        :param name: the name of the timer
        :type name: string
        """
        cls.timer_end[name] = time.time()
        # if cumulate:
        #    cls.timer_end[name] = cls.timer_end[name] + cls.timer_last[name]
        cls.timer_sum[name] = cls.timer_sum[name] + cls.timer_end[name] - cls.timer_start[name]

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
    def benchmark(cls,
                  sysinfo=True,
                  csv=True,
                  prefix="# csv",
                  tag=None,
                  sum=True):
        """
        prints out all timers in a convenient benchmark table
        :return:
        :rtype:
        """

        #
        # PRINT PLATFORM
        #

        print()
        data_platform = systeminfo()

        data_platform['cpu_count'] = multiprocessing.cpu_count()

        if sysinfo:
            print(Printer.attribute(
                data_platform,
                order=["Machine Attribute", "Value"],
                output="table"
            ))

        #
        # PRINT TIMERS
        #
        timers = StopWatch.keys()

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
                    'timer': timer,
                    'tag': tag or ''
                }

                for attribute in ["uname.node",
                                  "user",
                                  "uname.system",
                                  "uname.machine",
                                  "platform.version",
                                  "sys.platform"]:
                    data_timers[timer][attribute] = data_platform[attribute]

            # print(Printer.attribute(data_timers, header=["Command", "Time/s"]))

            if 'benchmark_start_stop' in data_timers:
                del data_timers['benchmark_start_stop']

            for key in data_timers:
                if key != 'benchmark_start_stop' and data_timers[key]['status'] is None:
                    data_timers[key]['status'] = "failed"
                elif data_timers[key]['status'] is not None and data_timers[key]['status']:
                    data_timers[key]['status'] = "ok"

            order = [
                "timer",
                "status",
                "time",
                "sum",
                "start",
                "tag",
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
                "Node",
                "User",
                "OS",
                "Version"
            ]

            print()
            print(Printer.write(
                data_timers,
                order=order,
                header=header,
                output="table"

            ))
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
