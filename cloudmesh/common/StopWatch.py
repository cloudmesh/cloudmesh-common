"""
Class for starting and stopping named timers.

This class is based on a similar java class in cyberaide, and java cog kit.

"""
from __future__ import print_function

import os
import time
from cloudmesh.common.Printer import Printer
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

    @classmethod
    def keys(cls):
        """returns the names of the timers"""
        return list(cls.timer_end.keys())

    @classmethod
    def start(cls, name):
        """
        starts a timer with the given name.

        :param name: the name of the timer
        :type name: string
        """
        if cls.debug:
            print("Timer", name, "started ...")
        cls.timer_start[name] = time.time()

    @classmethod
    def stop(cls, name):
        """
        stops the timer with a given name.

        :param name: the name of the timer
        :type name: string
        """
        cls.timer_end[name] = time.time()
        if cls.debug:
            print("Timer", name, "stopped ...")

    @classmethod
    def get(cls, name):
        """
        returns the time of the timer.

        :param name: the name of the timer
        :type name: string
        :rtype: the elapsed time
        """
        if name in cls.timer_end:
            cls.timer_elapsed[name] = cls.timer_end[name] - \
                                      cls.timer_start[name]
            return cls.timer_elapsed[name]
        else:
            return "undefined"

    @classmethod
    def clear(cls):
        """
        clear start and end timer_start
        """
        cls.timer_start.clear()
        cls.timer_end.clear()

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
                    "elapsed": str(cls.get(t)),
                    "newline": os.linesep}
            s += "{label} {start} {end} {elapsed} {newline}".format(**data)
        return s

    def benchmark(self, sysinfo=True):
        """
        prints out all timers in a convenient benchmark tabble
        :return:
        :rtype:
        """

        #
        # PRINT PLATFORM
        #
        if sysinfo:
            data_platform = systeminfo()
            print(Printer.attribute(data_platform,
                                    ["Machine Arribute", "Time/s"]))

        #
        # PRINT TIMERS
        #
        timers = StopWatch.keys()

        data_timers = {}
        for timer in timers:
            data_timers[timer] = {
                'time': round(StopWatch.get(timer), 2),
                'timer': timer
            }
            for attribute in ["node", "system", "machine", "mac_version",
                              "win_version"]:
                data_timers[timer][attribute] = data_platform[attribute]
        # print(Printer.attribute(data_timers, header=["Command", "Time/s"]))
        print(Printer.write(
            data_timers,
            order=["timer", "time", "node", "system", "mac_version",
                   "win_version"]
        ))

        print()
        print(Printer.write(
            data_timers,
            order=["timer", "time", "node", "system", "mac_version",
                   "win_version"],
            output="csv"
        ))
