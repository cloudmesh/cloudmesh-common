"""Class for starting and stopping named timers.

Here is a simple example. the user and node parameters can be omitted,
but they help in case you like to change the system retrieved values.

from pprint import pprint
from cloudmesh.common.StopWatch import StopWatch

import time

user="gregor"
node="5950x"

for t in ["a", "b"]:
    StopWatch.start(t)
    time.sleep(0.1)
    StopWatch.stop(t)

pprint(StopWatch.get_benchmark(user=user, node=node))

StopWatch.benchmark(user=user, node=node)

## Context Block

StopWatch also comes with a context block allowing to use the
convenient `with` statement. However, this is only recommended when the
block is small as it is easy to lose the indentation in larger
code. You can also certainly split the code up into functions so it is
easier manageable.

Here is a simple example of how to use the `with` statement, showing
that is can be used for streams and files.  The mode determines if the
file will be recreated, or if it will be expanded on. In addition,
there is the ability to write metadata into the record with a `dict`
that can optionally be passed along.

In order not to overwrite the value of an event, you must give it a
unique name.

    from cloudmesh.common.StopWatch import StopWatchBlock
    from cloudmesh.common.StopWatch import StopWatch
    from cloudmesh.common.util import readfile

    import time

    data = {"step": "value"}

    StopWatch.event("event-start")
    d = {"key": "value"}
    StopWatch.event("event-with-value", d)

    with StopWatchBlock("total"):
        time.sleep(1.0)

    with StopWatchBlock("dict", data=data):
        time.sleep(1.0)
        data["step"] = 1

    with StopWatchBlock("file", data=data, log="a.log", mode="w"):
        time.sleep(1.0)
        data["step"] = 2

    with StopWatchBlock("append", data=data, log="a.log", mode="a"):
        time.sleep(1.0)
        data["step"] = 3

    content = readfile ("a.log")
    print (79*"=")
    print (content.strip())
    print (79*"=")

    StopWatch.event("event-stop")

    StopWatch.benchmark(sysinfo=False,
                        tag="myexperiment",
                        user="gregor",
                        node="computer",
                        attributes=["timer", "status", "time", "start", "tag", "msg"]

    # for more examples, see our pytest:
    # * <https://github.com/cloudmesh/cloudmesh-common/blob/main/tests/test_stopwatch.py>
    #
    # there we demonstrate how to timers in a loop as individual timers and as sum.
    # We also showcase how to add a message to timers
    )

"""

import datetime
import os
import pprint
import sys
import time
from typing import Union

from cloudmesh.common.DateTime import DateTime
from cloudmesh.common.Tabulate import Printer
from cloudmesh.common.systeminfo import systeminfo as cm_systeminfo
from cloudmesh.common.util import appendfile
from cloudmesh.common.util import banner
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile


def progress(
    filename=None,  # +
    status="ready",  # +
    progress: Union[int, str, float] = 0,  # +
    pid=None,  # +
    time=False,
    stdout=True,
    stderr=True,
    append=None,
    with_banner=False,
    # variable we do not have, but should be in kwrags
    **kwargs,
):
    """Creates a printed line of the form

        "# cloudmesh status=ready progress=0 pid=$$ time='2022-08-05 16:29:40.228901'"

    If the pid is omitted it will give the current process pid
    If PID contains the string SLURM it will give the SLURM_TASK_ID
    Otherwise it will take the value passed along in pid

    Args:
        status (str): String representation of the status
        progress (int | str): Progress in value from 0 to 100
        pid (int): Process ID. If not specified, it used the underlaying
            PID from the OS, or the task id from SLURM or LSF if
            submitted through a queueing system.
        time (str): current time
        stdout (bool): if TRue Prints the progress, if False does not
            pring, defaut is print
        filename (str): where to write the progress as a file
        **kwargs (dict): additional arguments as key=value

    Returns:
        str: progress string
    """
    if type(progress) in ["int", "float"]:
        progress = str(progress)
    if pid is None:
        if "SLURM_JOB_ID" in os.environ:
            pid = os.environ["SLURM_JOB_ID"]
        elif "LSB_JOBID" in os.environ:
            pid = os.environ["LSB_JOBID"]
        else:
            pid = os.getpid()
    variables = ""
    msg = f"# cloudmesh status={status} progress={progress} pid={pid}\n"
    if time:
        t = str(DateTime.now())
        msg = msg + f" time='{t}'"
    if kwargs:
        for name, value in kwargs.items():
            variables = variables + f" {name}={value}"
        msg = msg + variables
    if append is not None:
        msg = msg + " " + append
    if stdout:
        if with_banner:
            banner(msg)
        print(msg, file=sys.stdout)
    if stderr:
        print(msg, file=sys.stderr)
    if filename is not None:
        appendfile(filename, msg)
    return msg


def rename(newname):
    """decorator to rename a function

    Args:
        newname (str): function name

    Returns:
        object: renamed function
    """

    def decorator(f):
        f.__name__ = newname
        return f

    return decorator


def benchmark(func):
    """decorator to benchmark a function

    Args:
        func (object): function

    Returns:
        object: function with benchmarks based on the name of the
        function
    """

    @rename(func.__name__)
    def wrapper(*args, **kwargs):
        StopWatch.start(func.__name__)
        func(*args, **kwargs)
        StopWatch.stop(func.__name__)

    return wrapper


class StopWatch(object):
    """A class to measure times between events."""

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
    # mllogger
    timer_values = {}

    # @classmethod
    # def progress(cls, percent, status="running", pid=None):
    #     if pid is None:
    #         pid = os.getpid()
    #     if "SLURM_JOB_ID" in os.environ:
    #         pid = os.environ["SLURM_JOB_ID"] #TODO - may need to be updated (monitor of long running jobs)
    #     print(f"# cloudmesh status={status} progress={percent} pid={pid}")

    # @classmethod
    # def progress(cls,
    #              percent: Union[int, str],
    #              status="running",
    #              pid=None,
    #              variable=None,
    #              filename=None):
    #     """Prints progress of an event, recording against a pid and providing additional variable.
    #
    #     :param percent: 0-100 value
    #     :type percent: int | str
    #     :param status: Message to associate to the recording, default - running
    #     :param pid: The associated Process ID for this event.
    #     :param variable: Any valid python type with a __str__ method.
    #
    #     :return: The progress message as a string
    #     """
    #     if type(percent) == 'int':
    #         percent = str(percent)
    #     if pid is None:
    #         pid = os.getpid()
    #     if "SLURM_JOB_ID" in os.environ:
    #         # TODO - may need to be updated (monitor of long running jobs)
    #         pid = os.environ["SLURM_JOB_ID"]
    #     msg = f"# cloudmesh status={status} progress={percent} pid={pid}"
    #     if variable is not None:
    #         msg = msg + f" variable={variable}"
    #     print(msg)
    #     if filename is not None:
    #         appendfile(filename, msg)
    #     return msg
    #
    #     try:
    #         config = yaml.safe_load(readfile(configfile).strip())
    #     except:  # noqa: E722
    #         config = {
    #             "benchmark": {}
    #         }
    #     config["benchmark"].update(argv)

    @classmethod
    def keys(cls):
        """returns the names of the timers"""
        return list(cls.timer_end.keys())

    @classmethod
    def status(cls, name, value):
        """starts a timer with the given name.

        Args:
            name (string): the name of the timer
            value (bool): value of the nameed of a status
        """
        if cls.debug:
            print("Timer", name, "status", value)
        cls.timer_status[name] = value

    @classmethod
    def get_message(cls, name):
        """starts a timer with the given name.

        Args:
            name (string): the name of the timer
        """
        return cls.timer_msg[name]

    @classmethod
    def message(cls, name, value):
        """starts a timer with the given name.

        Args:
            name (string): the name of the timer
            value (bool): the value of the message
        """
        cls.timer_msg[name] = value

    @classmethod
    def event(cls, name, msg=None, values=None, value=None, stack_offset=2):
        """Adds an event with a given name, where start and stop is the same time.

        Args:
            name (string): the name of the timer
            msg (string): a message to attach to this event
            values (object): data that is associated with the event that
                is converted to a string

        Returns:
            None: None
        """
        values = values or value

        StopWatch.start(name)
        StopWatch.stop(name)
        StopWatch.timer_end[name] = StopWatch.timer_start[name]
        if values:
            StopWatch.timer_values[name] = values

        if msg is not None:
            StopWatch.message(name, str(msg))

        if cls.debug:
            print("Timer", name, "event ...")

    @classmethod
    def start(cls, name, values=None, value=None):
        """starts a timer with the given name.

        Args:
            name (string): the name of the timer
            values (object): any python object with a __str__ method to
                record with the event.

        Returns:
            None: None
        """
        values = values or value

        if cls.debug:
            print("Timer", name, "started ...")
        if name not in cls.timer_sum:
            cls.timer_sum[name] = 0.0
        cls.timer_start[name] = time.time()
        cls.timer_end[name] = None
        cls.timer_status[name] = None
        cls.timer_msg[name] = None
        if values:
            StopWatch.timer_values[name] = values

        if cls.debug:
            print("Timer", name, "start ...")

    @classmethod
    def stop(cls, name, state=True, values=None, value=None):
        """stops the timer with a given name.

        Args:
            name (string): the name of the timer
            state (bool): When true, updates the status of the timer.

        Returns:
            None: None
        """
        values = values or value

        cls.timer_end[name] = time.time()
        # if cumulate:
        #    cls.timer_end[name] = cls.timer_end[name] + cls.timer_last[name]
        cls.timer_sum[name] = (
            cls.timer_sum[name] + cls.timer_end[name] - cls.timer_start[name]
        )
        cls.timer_status[name] = state
        if values:
            StopWatch.timer_values[name] = values

        if cls.debug:
            print("Timer", name, "stopped ...")

    @classmethod
    def get_status(cls, name):
        """sets the status of the timer with a given name.

        Args:
            name (string): the name of the timer
        """
        return cls.timer_status[name]

    # noinspection PyPep8
    @classmethod
    def get(cls, name, digits=4):
        """returns the time of the timer.

        Args:
            name (string): the name of the timer

        Returns:
            the elapsed time
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
        """returns the sum of the timer if used multiple times

        Args:
            name (string): the name of the timer

        Returns:
            the elapsed time
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
        """clear start and end timer_start"""
        cls.timer_start.clear()
        cls.timer_end.clear()
        cls.timer_sum.clear()
        cls.timer_status.clear()
        cls.timer_elapsed.clear()
        cls.timer_msg.clear()

    @classmethod
    def print(cls, *args):
        """prints a timer. The first argument is the label if it exists, the last is the timer

        Args:
            *args: label, name

        Returns:

        """
        if cls.verbose:
            if len(args) == 2:
                print(args[0], str("{0:.2f}".format(cls.get(args[1]))), "s")
            else:
                raise Exception("StopWatch: wrong number of arguments")

    @classmethod
    def output(cls, name):
        """prints a timer. The first argument is the label if it exists, the last is the timer

        Args:
            args: label, name

        Returns:

        """
        print(name, str("{0:.2f}".format(cls.get(name))), "s")

    @classmethod
    def __str__(cls):
        """returns the string representation of the StopWatch

        Returns:
            str: string of the StopWatch
        """
        s = ""
        for t in cls.timer_end:
            data = {
                "label": t,
                "start": str(cls.timer_start[t]),
                "end": str(cls.timer_end[t]),
                "status": str(cls.timer_status[t]),
                "elapsed": str(cls.get(t)),
                "newline": os.linesep,
            }
            s += "{label} {start} {end} {elapsed} {status} {newline}".format(**data)
        return s

    @classmethod
    def systeminfo(cls, data=None):
        """Print information about the system

        Args:
            data (dict): additional data to be integrated

        Returns:
            str: a table with data
        """
        data_platform = cm_systeminfo()
        if data is not None:
            data_platform.update(data)
        return Printer.attribute(
            data_platform, order=["Machine Attribute", "Value"], output="table"
        )

    @classmethod
    def get_sysinfo(cls, node=None, user=None):
        data_platform = cm_systeminfo(node=node, user=user)
        return data_platform

    @classmethod
    def get_benchmark(
        cls,
        sysinfo=True,
        tag=None,
        node=None,
        user=None,
        total=False,
    ):
        """prints out all timers in a convenient benchmark table

        Args:
            sysinfo (bool): controls if system info shoul be printed.
            csv (bool): contols if the data should be printed also as
                csv strings
            prefix (str): The prefix used for the csv string
            tag (str): overwrites the tag
            sum (bool): prints the sums (not used)
            node (str): overwrites the name of the node
            user (str): overwrites the name of the user
            attributes (list): list of additional attributes to print

        Returns:
            stdout: prints the information
        """

        #
        # PRINT PLATFORM
        #

        data_platform = cm_systeminfo(user=user, node=node)
        if sysinfo:
            print(Printer.attribute(data_platform, output="table"))

        benchmark_data = {
            "sysinfo": data_platform,
        }

        #
        # GET TIMERS
        #
        timers = StopWatch.keys()
        total_time = 0.0
        if len(timers) > 0:
            data_timers = {}
            for timer in timers:
                data_timers[timer] = {
                    "start": time.strftime(
                        "%Y-%m-%d %H:%M:%S", time.gmtime(StopWatch.timer_start[timer])
                    ),
                    "stop": time.strftime(
                        "%Y-%m-%d %H:%M:%S", time.gmtime(StopWatch.timer_end[timer])
                    ),
                    "time": StopWatch.get(timer, digits=3),
                    "sum": StopWatch.sum(timer, digits=3),
                    "status": StopWatch.get_status(timer),
                    "msg": StopWatch.get_message(timer),
                    "timer": timer,
                    "tag": tag or "",
                }
                total_time = total_time + StopWatch.get(timer)

            # print(Printer.attribute(data_timers, header=["Command", "Time/s"]))

            if "benchmark_start_stop" in data_timers:
                del data_timers["benchmark_start_stop"]

            for key in data_timers:
                if key != "benchmark_start_stop" and data_timers[key]["status"] is None:
                    data_timers[key]["status"] = "failed"
                elif (
                    data_timers[key]["status"] is not None
                    and data_timers[key]["status"]
                ):
                    data_timers[key]["status"] = "ok"

            if total:
                print("Total:", total_time)

            benchmark_data["benchmark"] = data_timers

        else:
            print("ERROR: No timers found")

        return benchmark_data

    @classmethod
    def benchmark(
        cls,
        sysinfo=True,
        timers=True,
        csv=True,
        prefix="# csv",
        tag=None,
        sum=True,
        node=None,
        user=None,
        version=None,
        attributes=None,
        total=False,
        filename=None,
    ):
        """prints out all timers in a convenient benchmark table

        Args:
            sysinfo (bool): controls if system info shoul be printed.
            csv (bool): contols if the data should be printed also as
                csv strings
            prefix (str): The prefix used for the csv string
            tag (str): overwrites the tag
            sum (bool): prints the sums (not used)
            node (str): overwrites the name of the node
            user (str): overwrites the name of the user
            attributes (list): list of additional attributes to print

        Returns:
            stdout: prints the information
        """

        #
        # PRINT PLATFORM
        #
        content = "\n"

        data_platform = cm_systeminfo(user=user, node=node)
        if sysinfo:
            content = content + Printer.attribute(
                data_platform, order=["Machine Attribute", "Value"], output="table"
            )
            content = content + "\n"

        if timers:
            #
            # PRINT TIMERS
            #
            timers = StopWatch.keys()
            total_time = 0.0
            if len(timers) > 0:
                data_timers = {}
                for timer in timers:
                    data_timers[timer] = {
                        "start": time.strftime(
                            "%Y-%m-%d %H:%M:%S",
                            time.gmtime(StopWatch.timer_start[timer]),
                        ),
                        "time": StopWatch.get(timer, digits=3),
                        "sum": StopWatch.sum(timer, digits=3),
                        "status": StopWatch.get_status(timer),
                        "msg": StopWatch.get_message(timer),
                        "timer": timer,
                        "tag": tag or "",
                    }
                    try:
                        total_time = total_time + StopWatch.get(timer)
                    except:  # noqa: E722
                        pass
                    for attribute in [
                        "uname.node",
                        "user",
                        "uname.system",
                        "uname.machine",
                        "platform.version",
                        "sys.platform",
                    ]:
                        if attribute == "user" and user is not None:
                            data_timers[timer][attribute] = user
                        elif attribute == "uname.node" and node is not None:
                            data_timers[timer][attribute] = node
                        else:
                            data_timers[timer][attribute] = data_platform[attribute]

                    if version is not None:
                        data_timers[timer]["platform.version"] = version

                # print(Printer.attribute(data_timers, header=["Command", "Time/s"]))

                if "benchmark_start_stop" in data_timers:
                    del data_timers["benchmark_start_stop"]

                for key in data_timers:
                    if (
                        key != "benchmark_start_stop"
                        and data_timers[key]["status"] is None
                    ):
                        data_timers[key]["status"] = "failed"
                    elif (
                        data_timers[key]["status"] is not None
                        and data_timers[key]["status"]
                    ):
                        data_timers[key]["status"] = "ok"

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
                        "platform.version",
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
                        "Version",
                    ]
                elif attributes == "short":
                    order = ["timer", "status", "time"]

                    header = ["Name", "Status", "Time"]
                else:
                    order = attributes
                    header = attributes
                content = content + "\n"
                content = content + Printer.write(
                    data_timers, order=order, header=header, output="table"
                )

                if total:
                    content = content + f"Total: {total_time}"

                content = content + "\n"

                if csv:
                    if prefix is not None:
                        for entry in data_timers:
                            data_timers[entry]["# csv"] = prefix

                        order = ["# csv"] + order

                        content = content + Printer.write(
                            data_timers, order=order, header=header, output="csv"
                        )
                    else:
                        content = content + pprint.pformat(data_timers, indent=4)
                        content = content + "\n"

                        content = content + Printer.write(
                            data_timers, order=order[1:], output="csv"
                        )
                        content = content + "\n"

            else:
                content = content + "ERROR: No timers found\n"

        print(content)
        if filename:
            writefile(filename, content)

    def load(
        filename,
        label=["name"],
        label_split_char=" ",
        attributes=[
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
            "platform.version",
        ],
    ):
        """Loads data written to a file from the #csv lines.
        If the timer name has spaces in it, it must also have a label tag in which each lable is the name when
        splitting up the timer name. The list of attributes is the list specified plus the once generated from the
        timer name by splitting.

        Example:
            data = StopWatch.load(logfile, label=["name", "n"], attributes=["timer", "time", "user", "uname.node"])

        Args:
            label
            attributes

        Returns:

        """
        from cloudmesh.common.Shell import Shell

        data = []
        headers = []
        content = readfile(filename)
        lines = Shell.find_lines_with(content, what="# csv")
        data_attributes = lines[0].split(",")
        index_attributes = []
        for attribute in attributes:
            index_attributes.append(data_attributes.index(attribute))
        print(index_attributes)
        headers = attributes + label
        del lines[0]
        for line in lines:
            entry = line.split(",")
            entry = [entry[i] for i in index_attributes]
            label_tags = entry[0].split(label_split_char)
            entry = entry + label_tags
            data.append(entry)

        return {"headers": headers, "data": data}


class StopWatchBlock:
    def __init__(self, name, data=None, log=sys.stdout, mode="w"):
        self.name = name
        self.data = data
        self.log = log
        self.is_file = False
        self.start = datetime.datetime.now()
        if type(log) == str:
            self.is_file = True
            self.log = open(log, mode)

    def __enter__(self):
        StopWatch.start(self.name)
        return StopWatch.get(self.name)

    def __exit__(self, type, value, traceback):
        self.stop = datetime.datetime.now()
        StopWatch.stop(self.name)
        entry = StopWatch.get(self.name)
        if self.data:
            print(
                f"# {self.name}, {entry}, {self.start}, {self.stop}, {self.data}",
                file=self.log,
            )
        else:
            print(f"# {self.name}, {entry}, {self.start}, {self.stop}", file=self.log)
        if self.is_file:
            self.log.close()
