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

Integration with MLPerf Logging

To also produce output that conforms to MLPerf, cloudmesh.StopWatch
provides utilities to enable and annotate mlperf_logging messages.  To
enable, you must first install mlperf-logging, which can be installed
via pypi, or you can install the latest by using one of the below
commands:

::
    git clone https://github.com/mlperf/logging.git mlperf-logging
    cd mlperf-logging
    pip install -e .

::
    pip install git+https://github.com/mlperf/logging.git

Now you can just use the StopWatch as before.

Once installed, you must elect to activate the logger, calling
StopWatch.activate_mllog.  This will reconfigure the logic of
StopWatch so start, stop, and event method are also logged in the
mlperf log output.  Note that when this is enabled, you are now able
to use the keywords in the signature prefixed with mllog_.

For example, to trigger an event in StopWatch and mlperf_logging, you
can do the following

::
    StopWatch.activate_mllog()
    StopWatch.event("Name Of Event")

The above will run the stopwatch timer as per normal, but also create
a POINT_IN_TIME log entry in the mlperf log written to
`./cloudmesh_mllog.log`.  You can also pass values in to this event as
you would with StopWatch events, so that additional details can be
captured.

While this allows for transparent timers to function, you may need to
use a mllog key that is different from what you are tracking in
StopWatch.  In this case, use the mllog_key keyword, which overrides
the default `name` attribute as the key used in mllog.

Note that if the key's string matches a property in the
mlperf_logging.mllog.constants module, it will dereference the
property.

For example,

::
    StopWatch.activate_mllog() # this only needs to be run once
    StopWatch.event("CloudmeshTimer", mllog_key="EVAL_INIT", values="Example")

This will create a stopwatch timer with the name CloudmeshTimer, and
record an mllog event, which will look up if there is a property named
EVAL_START in mlperf_logging.mllog.constants, which it will find and
dereferences to the string `eval_start`, and then records the string
"Example" in the event.

In the case where you are logging blocks of time using start and end,
these methods also have the mllog_key attribute, allowing the key for
fenced code to be overridden.

Finally, there are times when the code will need a StopWatch timer but
not an mllog entry, or vice versa.  The `suppress_*` methods in the
event, start, and stop provide mechanisms to prevent either framework
from executing when set to true.  By default, only the StopWatch API
is enabled, and if you call activate_mllog, both frameworks will be on
by default.

So if you wish to create a log entry that does not create a stopwatch
event, you can call

::
    StopWatch.event("MyLoggingEvent", values={'custom': 123}, suppress_stopwatch=True)

And this will only create a mllog entry, bypassing all StopWatch logic.

Finally, there is a utility method that generates a series of mllog
events that are required for generating benchmark submissions:
organization_mllog.  This method takes in a YAML configuration file
and extracts fields that match up to the standard logging events.

This method is useful when creating experiments with tools such as
cloudmesh-sbatch.
"""
import datetime
import os
import pathlib
import pprint
import sys
import time
from typing import Union

import yaml
from cloudmesh.common.StopWatch import progress
from cloudmesh.common.StopWatch import progress as common_progress
from cloudmesh.common.Tabulate import Printer
from cloudmesh.common.console import Console
from cloudmesh.common.systeminfo import systeminfo as cm_systeminfo
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile


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


def import_mllog():
    try:
        from mlperf_logging import mllog
    except:  # noqa: E722
        Console.error("You need to install mllogging to use it")
        sys.exit()
    return mllog


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
    mllogging = False
    mllogger = None

    @classmethod
    def activate_mllog(cls, filename="cloudmesh_mllog.log", config=None, stack_offset=2):
        # global mllog

        if not os.path.exists(filename):
            writefile(filename, "")
        cls._mllog_import = import_mllog()


        if config is None:
            cms_mllog = dict(
                default_namespace="cloudmesh",
                default_stack_offset=stack_offset,
                default_clear_line=False
            )
        else:
            cms_mllog = config

        cls.mllogging = True
        cls.mllogger = cls._mllog_import.get_mllogger()
        if os.path.exists(filename):
            cls._mllog_import.config(filename=filename)
        cls._mllog_import.config(**cms_mllog
                                 # useful when refering to linenumbers in separate code
                                 # root_dir=os.path.normpath(
                                 #    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", ".."))
                                 )

    # @classmethod
    def progress(filename=None,  # +
                 status="ready",  # +
                 progress: Union[int, str, float] = 0,
                 pid=None,  # +
                 time=False,
                 stdout=True,
                 stderr=True,
                 append=None,
                 with_banner=False,
                 **kwargs):
        common_progress(filename=filename,
                     status=status,
                     progress=progress,
                     pid=pid,
                     time=time,
                     stdout=stdout,
                     stderr=stderr,
                     append=append,
                     with_banner=with_banner,
                     kwargs=kwargs)

    # def progress(cls, percent, status="running", pid=None):
    #     if pid is None:
    #         pid = os.getpid()
    #     if "SLURM_JOB_ID" in os.environ:
    #         pid = os.environ["SLURM_JOB_ID"] #TODO - may need to be updated (monitor of long running jobs)
    #     print(f"# cloudmesh status={status} progress={percent} pid={pid}")
    #
    # @classmethod
    # def progress(cls, percent, status="running", pid=None, variable=None):
    #     """Prints progress of an event, recording against a pid and providing additional variable.
    #
    #     :percent: 0-100 value
    #     :status: Message to associate to the recording, default - running
    #     :pid: The associated Process ID for this event.
    #     :variable: Any valid python type with a __str__ method.
    #
    #     :returns: The progress message as a string
    #     """
    #     if pid is None:
    #         pid = os.getpid()
    #     if "SLURM_JOB_ID" in os.environ:
    #         # TODO - may need to be updated (monitor of long running jobs)
    #         pid = os.environ["SLURM_JOB_ID"]
    #     msg = f"# cloudmesh status={status} progress={percent} pid={pid}"
    #     if variable is not None:
    #         msg = msg + f" variable={variable}"
    #     print(msg)
    #     return msg
    #     try:
    #         config = yaml.safe_load(readfile(configfile).strip())
    #     except:  # noqa: E722
    #         config = {
    #             "benchmark": {}
    #         }
    #     config["benchmark"].update(argv)

    # @classmethod
    # def organization_mllog(cls, configfile = None, prefix_: str = 'benchmark', flatdict_: bool = False, **argv):
    #     try:
    #         from mlperf_logging import mllog
    #     except Exception:  # noqa: E722
    #         Console.error("You need to install mllogging to use it")
    #         sys.exit()
    #
    #     try:
    #         with open(pathlib.Path(configfile), 'r') as stream:
    #             _config = yaml.safe_load(stream)
    #     except Exception as e:  # noqa: E722
    #         _config = {
    #             "benchmark": {}
    #         }
    #     prefix = prefix_
    #     if flatdict_:
    #         for k,v in argv.items():
    #             _config[f"{prefix}.{k}"] = v
    #     else:
    #         _config[prefix].update(argv)
    #
    #     for key, attribute in [
    #         (mllog.constants.SUBMISSION_BENCHMARK, 'name'),
    #         (mllog.constants.SUBMISSION_POC_NAME, 'user'),
    #         (mllog.constants.SUBMISSION_POC_EMAIL, 'e-mail'),
    #         (mllog.constants.SUBMISSION_ORG, 'organisation'),
    #         (mllog.constants.SUBMISSION_DIVISION, 'division'),
    #         (mllog.constants.SUBMISSION_STATUS, 'status'),
    #         (mllog.constants.SUBMISSION_PLATFORM, 'platform')
    #         ]:
    #         try:
    #             if flatdict_:
    #                 cls.mllogger.event(key, value=_config[f"{prefix}.{attribute}"])
    #             else:
    #                 cls.mllogger.event(key, value=_config["benchmark"][attribute])
    #         except AttributeError as e:
    #             print(f"Missing/invalid standard property {key}")

    @classmethod
    def organization_mllog(cls, configfile=None, **argv):
        try:
            from mlperf_logging import mllog
        except Exception:  # noqa: E722
            Console.error("You need to install mllogging to use it")
            sys.exit()

        try:
            with open(pathlib.Path(configfile), 'r') as stream:
                data = yaml.safe_load(stream)
        except Exception as e:  # noqa: E722
            data = {
                "benchmark": {}
            }
            data.update(argv)
        except Exception as e:
            Console.error(e, traceflag=True)

        for key, attribute in [
            (mllog.constants.SUBMISSION_BENCHMARK, 'name'),
            (mllog.constants.SUBMISSION_POC_NAME, 'user'),
            (mllog.constants.SUBMISSION_POC_EMAIL, 'e-mail'),
            (mllog.constants.SUBMISSION_ORG, 'organisation'),
            (mllog.constants.SUBMISSION_DIVISION, 'division'),
            # (mllog.constants.SUBMISSION_STATUS, 'status'),
            (mllog.constants.SUBMISSION_PLATFORM, 'platform')
        ]:
            try:
                value = data["benchmark"][attribute]
                cls.event(key, mllog_key=key, value=value, stack_offset=3, suppress_stopwatch=True)
            except Exception as e:
                Console.error(e, traceflag=True)

    @classmethod
    def organization_submission(cls, configfile=None, **argv):
        """
        Args:
            configfile
            **argv

        Returns:

        submission:
          benchmark: earthquake
          submitter: Gregor von Laszewski
          email: laszewski@gmail.com
          org: University of Virginia
          division: closed or open
          platform: rivanna
          status: success or aborted (is not going to be written
            until the very end)
          (must not be written when we write the organization submission)
          if poc exists, use it;
          else if submitter exists, use it;
          else error
          ? point_of_contact_name:
          ? point_of_contact_email:
          ? version: mlcommons-earthquake-v1.0
          ? github_commit_version: TBD
          # value = d['submission']['version']
          # event('submission_version',value=value)
          # value = d['submission']['github_commit_version']
          # event('github_commit_version',value=value)

        """
        try:
            from mlperf_logging import mllog
        except Exception:  # noqa: E722
            Console.error("You need to install mllogging to use it")
            sys.exit()

        try:
            with open(pathlib.Path(configfile), 'r') as stream:
                data = yaml.safe_load(stream)
        except Exception as e:  # noqa: E722
            data = {
                "benchmark": {}
            }
            data.update(argv)
        except Exception as e:
            Console.error(e, traceflag=True)
        # value = data['submission']['version']
        # event('submission_version',value=value)
        # value = data['submission']['github_commit_version']
        # event('github_commit_version',value=value)
        for key, attribute in [
            (mllog.constants.SUBMISSION_BENCHMARK, 'name'),
            (mllog.constants.SUBMISSION_POC_NAME, 'submitter'),
            (mllog.constants.SUBMISSION_POC_EMAIL, 'email'),
            (mllog.constants.SUBMISSION_ORG, 'org'),
            (mllog.constants.SUBMISSION_DIVISION, 'division'),
            (mllog.constants.SUBMISSION_PLATFORM, 'platform'),
            ("submission_version", 'version'),
            ("github_commit_version", 'github_commit_version')
        ]:
            try:
                value = data["submission"][attribute]
                cls.event(key, mllog_key=key, value=value, stack_offset=3, suppress_stopwatch=True)
            except Exception as e:
                Console.error(e, traceflag=True)

    @classmethod
    def status_submission(cls, success=True):
        try:
            from mlperf_logging import mllog
        except Exception:  # noqa: E722
            Console.error("You need to install mllogging to use it")
            sys.exit()

        key = mllog.constants.SUBMISSION_STATUS
        if success:
            value = 'success'
        else:
            value = 'aborted'
        cls.event(key,
                  mllog_key=key,
                  value=value,
                  stack_offset=3,
                  suppress_stopwatch=True)

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
    def event(cls,
              key=None,
              msg=None,
              values=None, value=None,
              mllog_key=None,
              suppress_stopwatch=False,
              suppress_mllog=False,
              stack_offset=2,
              executioncounter=True,
              metadata=None):
        """Adds an event with a given name, where start and stop is the same time.

        Args:
            name (string): the name of the timer
            msg (string): a message to attach to this event
            values (object): data that is associated with the event that
                is converted to a string
            mllog_key (string): Specifies the key to be used in
                mlperf_logging. If none, it will use the `name` value.
            suppress_stopwatch (bool): suppresses executing any
                stopwatch code. Useful when only logging an mllog event.
            suppress_mllog (bool): suppresses executing any mllog code.
                Useful when only interacting with stopwatch timers.

        Returns:
            None: None
        """
        name = key
        values = values or value
        if not suppress_stopwatch:
            StopWatch.start(name, suppress_mllog=True)
            StopWatch.stop(name, suppress_mllog=True)
            StopWatch.timer_end[name] = StopWatch.timer_start[name]
            if values:
                StopWatch.timer_values[name] = values

            if msg is not None:
                StopWatch.message(name, str(msg))
        if cls.mllogging and not suppress_mllog:
            if mllog_key is None:
                key_name = cls._mllog_lookup("POINT_IN_TIME")
            else:
                key_name = cls._mllog_lookup(mllog_key)
            if metadata is None:
                if values is not None:
                    cls.mllogger.event(key=name, value=str(values), stack_offset=stack_offset)
                else:
                    cls.mllogger.event(key=name, stack_offset=stack_offset)
            else:
                if values is not None:
                    cls.mllogger.event(key=name, value=str(values), stack_offset=stack_offset, metadata=metadata)
                else:
                    cls.mllogger.event(key=name, stack_offset=stack_offset, metadata=metadata)

    @classmethod
    def log_event(cls, **kwargs):
        """Logs an event using the passed keywords as parameters to be logged,
           prefiltered by mlperf_logging's standard api.

        Args:
            **kwargs (dict): an unpacked dictionary of key=value entries
                to be leveraged when logging an event to both the
                cloudmesh stopwatch and mllog.  If the keyword matches
                mlperf_logging's constants, the value will be replaced
                with the standardized string
        """
        for key, value in kwargs.items():
            mlkey = cls._mllog_lookup(key)
            cls.event(mlkey, msg=mlkey, values=value, stack_offset=3)

    @classmethod
    def _mllog_lookup(cls, key: str) -> str:
        """Performs a dynamic lookup for the string representation of a
           mlperf constant.  If the value isn't found, it will return a string
           of the pattern mllog-event-{key}

        Args:
            key (string): The name of the constant to look up

        Returns:
            string: The decoded value of the constant.
        """
        try:
            from mlperf_logging.mllog import constants as mlconst
        except ImportError as e:
            Console.error("You need to install mlperf_logging to use it")
            raise e
        try:
            key_str = getattr(mlconst, key)
        except AttributeError as e:
            key_str = f"mllog-event-{key}"
        return key_str

    @classmethod
    def start(cls,
              key=None,
              values=None, value=None,
              mllog_key=None,
              suppress_stopwatch=False,
              suppress_mllog=False,
              metadata=None):
        """starts a timer with the given name.

        Args:
            name (string): the name of the timer
            values (object): any python object with a __str__ method to
                record with the event.
            mllog_key (string): Specifies the string name of an mllog
                constant to associate to this timer start.  If no value
                is passed and mllogging is enabled, then `name` is used.
            suppress_stopwatch (bool): When true, prevents all
                traditional stopwatch logic from running.  This is
                useful when attempting to interact with mllog-only.
            suppress_mllog: When true, prevents all mllog events from
                executing.  Useful when working with stopwatch timers-
                only.

        Returns:
            None: None
        """
        name = key
        values = values or value

        if not suppress_stopwatch:
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

        if cls.mllogging and not suppress_mllog:
            if mllog_key is None:
                key = name
            else:
                key = cls._mllog_lookup(mllog_key)
            if values is not None:
                if isinstance(values, dict):
                    values['name'] = name
                elif isinstance(values, list):
                    values += list(name)
                else:
                    values = f"Name: {name}, {values}"

                cls.mllogger.start(key=key, value=str(values), metadata=metadata)
            else:
                cls.mllogger.start(key=key, value=name, metadata=metadata)

    @classmethod
    def stop(cls,
             key=None,
             state=True,
             values=None,
             value=None,
             mllog_key=None,
             suppress_stopwatch=False,
             suppress_mllog=False,
             metadata=None):
        """stops the timer with a given name.

        Args:
            name (string): the name of the timer
            state (bool): When true, updates the status of the timer.
            mllog_key (string): Specifies the string name of an mllog
                constant to associate to this timer start.  If no value
                is passed and mllogging is enabled, then `name` is used.
            suppress_stopwatch (bool): When true, prevents all
                traditional stopwatch logic from running.  This is
                useful when attempting to interact with mllog-only.
            suppress_mllog: When true, prevents all mllog events from
                executing.  Useful when working with stopwatch timers-
                only.

        Returns:
            None: None
        """

        name=key
        values = values or value

        if not suppress_stopwatch:
            cls.timer_end[name] = time.time()
            # if cumulate:
            #    cls.timer_end[name] = cls.timer_end[name] + cls.timer_last[name]
            cls.timer_sum[name] = cls.timer_sum[name] + cls.timer_end[name] - cls.timer_start[name]
            cls.timer_status[name] = state
            if values:
                StopWatch.timer_values[name] = values

        if cls.mllogging and not suppress_mllog:
            if mllog_key is None:
                key = name
            else:
                key = cls._mllog_lookup(mllog_key)
            if values is not None:
                if isinstance(values, dict):
                    values['name'] = name
                elif isinstance(values, list):
                    values += list(name)
                else:
                    values = f"Name: {name}, {values}"

                cls.mllogger.end(key=key, value=str(values), metadata=metadata)
            else:
                cls.mllogger.end(key=key, value=name, metadata=metadata)

        if cls.debug and not suppress_stopwatch:
            print("Timer", name, "stopped ...")

    @classmethod
    def get_status(cls, key=None):
        """sets the status of the timer with a given name.

        Args:
            name (string): the name of the timer
        """
        name = key
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
    def output(cls, key=None):
        """prints a timer. The first argument is the label if it exists, the last is the timer

        Args:
            args: label, name

        Returns:

        """
        name=key
        print(name, str("{0:.2f}".format(cls.get(name))), "s")

    @classmethod
    def __str__(cls):
        """returns the string representation of the StopWatch

        Returns:
            str: string of the StopWatch
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
            data_platform,
            order=["Machine Attribute", "Value"],
            output="table"
        )

    @classmethod
    def get_sysinfo(cls,
                    node=None,
                    user=None):
        data_platform = cm_systeminfo(node=node, user=user)
        return data_platform

    @classmethod
    def get_benchmark(cls,
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
            print(Printer.attribute(
                data_platform,
                output="table"
            ))

        benchmark_data = {
            'sysinfo': data_platform,
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
                    'start': time.strftime("%Y-%m-%d %H:%M:%S",
                                           time.gmtime(
                                               StopWatch.timer_start[timer])),
                    'stop': time.strftime("%Y-%m-%d %H:%M:%S",
                                          time.gmtime(
                                              StopWatch.timer_end[timer])),
                    'time': StopWatch.get(timer, digits=3),
                    'sum': StopWatch.sum(timer, digits=3),
                    'status': StopWatch.get_status(timer),
                    'msg': StopWatch.get_message(timer),
                    'timer': timer,
                    'tag': tag or ''
                }
                total_time = total_time + StopWatch.get(timer)

            # print(Printer.attribute(data_timers, header=["Command", "Time/s"]))

            if 'benchmark_start_stop' in data_timers:
                del data_timers['benchmark_start_stop']

            for key in data_timers:
                if key != 'benchmark_start_stop' and data_timers[key]['status'] is None:
                    data_timers[key]['status'] = "failed"
                elif data_timers[key]['status'] is not None and data_timers[key]['status']:
                    data_timers[key]['status'] = "ok"

            if total:
                print("Total:", total_time)

            benchmark_data["benchmark"] = data_timers

        else:
            print("ERROR: No timers found")

        return benchmark_data

    @classmethod
    def benchmark(cls,
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
                  filename=None):
        """prints out all timers in a convenient benchmark table

        Args:
            sysinfo (bool): controls if system info should be printed.
            csv (bool): controls if the data should be printed also as
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
                data_platform,
                order=["Machine Attribute", "Value"],
                output="table"
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
                    try:
                        total_time = total_time + StopWatch.get(timer)
                    except:  # noqa: E722
                        pass
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

                    if version is not None:
                        data_timers[timer]["platform.version"] = version

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
                else:
                    order = attributes
                    header = attributes
                content = content + "\n"
                content = content + Printer.write(
                    data_timers,
                    order=order,
                    header=header,
                    output="table"

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
                            data_timers,
                            order=order,
                            header=header,
                            output="csv"
                        )
                    else:

                        content = content + pprint.pformat(data_timers, indent=4)
                        content = content + "\n"

                        content = content + Printer.write(
                            data_timers,
                            order=order[1:],
                            output="csv"
                        )
                        content = content + "\n"

            else:
                content = content + "ERROR: No timers found\n"

        print(content)
        if filename:
            writefile(filename, content)

    def load(filename,
             label=["name"], label_split_char=" ",
             attributes=['timer',
                         'status',
                         'time',
                         'sum',
                         'start',
                         'tag',
                         'msg',
                         'uname.node',
                         'user',
                         'uname.system',
                         'platform.version']):
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

        return {"headers": headers,
                "data": data}

    @classmethod
    def deactivate_mllog(cls):
        """Disables the mllog capabilities and closes all registered handlers."""
        handlers = cls.mllogger.logger.handlers.copy()
        for handler in handlers:
            try:
                handler.acquire()
                handler.flush()
                handler.close()
            except (OSError, ValueError):
                pass
            finally:
                handler.release()
            cls.mllogger.logger.removeHandler(handler)
        cls.mllogging = False


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
            print(f"# {self.name}, {entry}, {self.start}, {self.stop}, {self.data}", file=self.log)
        else:
            print(f"# {self.name}, {entry}, {self.start}, {self.stop}", file=self.log)
        if self.is_file:
            self.log.close()
