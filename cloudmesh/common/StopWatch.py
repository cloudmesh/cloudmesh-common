"""
Class for starting and stopping named timers.

"""
import multiprocessing
import os
import time

import humanize
import psutil
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
    # records a status
    timer_status = {}

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
        if cls.debug:
            print("Timer", name, "stopped ...")

    @classmethod
    def get_status(cls, name):
        """
        stops the timer with a given name.

        :param name: the name of the timer
        :type name: string
        """
        return cls.timer_status[name]


    @classmethod
    def get(cls, name, digits=None):
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
            except:
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
            s += "{label} {start} {end} {elapsed} {status} {newline}".format(**data)
        return s

    @classmethod
    def benchmark(cls,
                  sysinfo=True,
                  csv=True,
                  prefix="#csv",
                  tag=None):
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
        mem = psutil.virtual_memory()
        try:
            data_platform['mem_total'] = humanize.naturalsize(mem.total, \
                                                              binary=True)
        except:
            pass
        try:
            data_platform['mem_available'] = humanize.naturalsize(
                mem.available, binary=True)
        except:
            pass
        try:
            data_platform['mem_percent'] = str(mem.percent) + "%"
        except:
            pass
        try:
            data_platform['mem_used'] = humanize.naturalsize(mem.used,
                                                             binary=True)
        except:
            pass
        try:
            data_platform['mem_free'] = humanize.naturalsize(mem.free,
                                                             binary=True)
        except:
            pass
        try:
            data_platform['mem_active'] = humanize.naturalsize(mem.active,
                                                               binary=True)
        except:
            pass
        try:
            data_platform['mem_inactive'] = humanize.naturalsize(mem.inactive,
                                                                 binary=True)
        except:
            pass
        try:
            data_platform['mem_wired'] = humanize.naturalsize(mem.wired,
                                                              binary=True)
        except:
            pass
        # svmem(total=17179869184, available=6552825856, percent=61.9,

        if sysinfo:
            print(Printer.attribute(data_platform,
                                    ["Machine Attribute", "Value"]))

        #
        # PRINT TIMERS
        #
        timers = StopWatch.keys()

        if len(timers) > 0:

            data_timers = {}
            for timer in timers:
                data_timers[timer] = {
                    'start': time.strftime("%Y-%m-%d %H:%M:%S",
                                           time.gmtime(StopWatch.timer_start[timer])),
                    'time': StopWatch.get(timer, digits=3),
                    'status': StopWatch.get_status(timer),
                    'timer': timer,
                    'tag': tag or ''
                }
                for attribute in ["node",
                                  "user",
                                  "system",
                                  "machine",
                                  "mac_version",
                                  "win_version"]:
                    data_timers[timer][attribute] = data_platform[attribute]

            # print(Printer.attribute(data_timers, header=["Command", "Time/s"]))

            if 'benchmark_start_stop' in data_timers:
                del data_timers['benchmark_start_stop']

            for key in data_timers:
                if key != 'benchmark_start_stop' and data_timers[key]['status'] == None:
                    data_timers[key]['status'] = "failed"
                elif data_timers[key]['status'] != None and data_timers[key]['status'] == True:
                    data_timers[key]['status'] = "ok"


            print(Printer.write(
                data_timers,
                order=["timer",
                       "status",
                       "time",
                       "start",
                       "tag",
                       "node",
                       "user",
                       "system",
                       "mac_version",
                       "win_version"],
                max_width=128)
            )

            print()
            if csv:
                order = ["csv",
                         "status"
                         "timer",
                         "time",
                         "start"
                         "tag",
                         "node",
                         "user",
                         "system",
                         "mac_version",
                         "win_version"]

                if prefix is not None:
                    for entry in data_timers:
                        data_timers[entry]["csv"] = "#csv"
                    print(Printer.write(
                        data_timers,
                        order=order,
                        output="csv"
                    ))
                else:
                    print(Printer.write(
                        data_timers,
                        order=order[1:],
                        output="csv"
                    ))

        else:

            print("ERROR: No timers found")

