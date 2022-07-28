###############################################################
# pytest -v --capture=no tests/test_stopwatch_mllog.py
# pytest -v --capture=no tests/test_stopwatch_mllog.py::Test_stopwatch.test_001
# pytest -v  tests/test_stopwatch_mllog.py
###############################################################
import platform
from typing import Dict, Any
import contextlib
import json
import logging
import os
import time
from io import StringIO  # Python 3
import pathlib
import sys
import tempfile
from pprint import pprint

import yaml

from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import readfile

import pytest
from cloudmesh.common.StopWatch import StopWatch

from cloudmesh.common.util import HEADING

# Sample taken from https://github.com/mlcommons/logging/blob/master/mlperf_logging/mllog/constants.py
mllog_constants=dict(
    DEFAULT_LOGGER_NAME = "mllog_default",
    DEFAULT_NAMESPACE = "",
    # Constant values - log event type
    INTERVAL_END = "INTERVAL_END",
    INTERVAL_START = "INTERVAL_START",
    POINT_IN_TIME = "POINT_IN_TIME",
    # Constant values - submission division
    CLOSED = "closed",
    OPEN = "open",
)


def close_logger(log):
    handlers = log.handlers.copy()
    for handler in handlers:
        try:
            handler.acquire()
            handler.flush()
            handler.close()
        except (OSError, ValueError):
            pass
        finally:
            handler.release()
        log.removeHandler(handler)

    #benchmark_constant = [
#
#]

benchmark_config = """
benchmark:
  name: Earthquake
  user: Gregor von Laszewski
  e-mail: laszewski@gmail.com
  organisation:  University of Virginia
  division: BII
  status: success
  platform: rivanna
  badkey: ignored
""".strip()

#
# @contextlib.contextmanager
# def yaml_generator(filename, prefix="general", flat=False):
#     if flat:
#         mllog_sampleyaml = f"""
# name: ignored
# {prefix}.name: Earthquake
# {prefix}.user: Gregor von Laszewski
# {prefix}.e-mail: laszewski@gmail.com
# {prefix}.organisation:  University of Virginia
# {prefix}.division: BII
# {prefix}.status: submission
# {prefix}.platform: rivanna
# {prefix}.badkey: ignored
# followon: ignored
# """
#     else:
#         mllog_sampleyaml="""
# name: ignored
# benchmark:
#   name: Earthquake
#   user: Gregor von Laszewski
#   e-mail: laszewski@gmail.com
#   organisation:  University of Virginia
#   division: BII
#   status: submission
#   platform: rivanna
#   badkey: ignored
# followon: ignored
# """
#     my_tempdir = tempfile.gettempdir()
#     temppath = pathlib.Path(my_tempdir) / filename
#     with open(temppath, 'wb') as f:
#         f.write(mllog_sampleyaml.encode('utf-8'))
#     try:
#         yield temppath
#     finally:
#         os.remove(temppath)
#
#
# def convert_mllog_to_object(log_stream: StringIO):
#     """Utility method to transform the mlperf logging strings into a python object.
#
#     :param log_stream: An io-like object that contains a stream of newline split json strings
#     :type log_stream: StringIO
#
#     :returns: a list of python dictionaries representing the logging events.
#     :rtype: list(dict)
#     """
#     obj = list()
#     text = log_stream.getvalue().replace(":::MLLOG ", "")
#     for x in text.split("\n"):
#         if x != "":
#             try:
#                 obj.append(json.loads(x))
#             except json.JSONDecodeError as e:
#                 pass
#     return obj
#
#
# @contextlib.contextmanager
# def intercept_mllogger(filename=None):
#     """A context function used to capture logging events in mlperf.
#     This method does so by directly registering a stream object to the logging
#     module.
#
#     :yields: a StringIO object that captures the StopWatch mllog events.
#     """
#     StopWatch.activate_mllog(filename=filename)
#     temp_out = StringIO('')
#     stream_handler = logging.StreamHandler(temp_out)
#     StopWatch.mllogger.logger.addHandler(stream_handler)
#     try:
#         yield temp_out
#     finally:
#         StopWatch.mllogger.logger.removeHandler(stream_handler)
#

@pytest.mark.incremental
class Test_Printer:

    def test_check_loading(self):
        Shell.rm("cloudmesh_mllog.log")
        StopWatch.activate_mllog()
        StopWatch.mllogger.event("test", "1", stack_offset=1)
        content = readfile("cloudmesh_mllog.log").splitlines()
        line = Shell.find_lines_with(content, what='"key": "test"')[0]
        print (line)
        if platform.system() == 'Windows':
            assert "cloudmesh-common\\\\tests\\\\test_stopwatch_mllog.py" in line
        else:
            assert "cloudmesh-common/tests/test_stopwatch_mllog.py" in line
        assert '"value": "1"' in line
        assert '"value": "1"' in line
        close_logger(StopWatch.mllogger.logger)

    def test_stopwatch_activate_mllog(self):
        HEADING()
        Shell.rm("cloudmesh_mllog.log")
        # Will not pass when running as an incremental test
        # StopWatch persists across threads.
        # assert not StopWatch.mllogging, "mllog should be disabled by default"
        StopWatch.activate_mllog()
        print(StopWatch.mllogging)
        assert StopWatch.mllogging, "activating mllog should enable the class variable"
        assert os.path.isfile("cloudmesh_mllog.log"), "activating should create a new log file"
        close_logger(StopWatch.mllogger.logger)


    def test_stopwatch_1_mllog(self):
        HEADING()
        Shell.rm("cloudmesh_mllog.log")
        StopWatch.activate_mllog()
        StopWatch.start("stopwatch sleep 1")
        time.sleep(0.1)
        StopWatch.stop("stopwatch sleep 1")
        StopWatch.status("stopwatch sleep 1", True)
        content = readfile("cloudmesh_mllog.log").splitlines()
        print(content)
        _start = content[0]
        _stop = content[1]

        print()
        print (_start)
        print (_stop)

        assert "INTERVAL_START" in _start
        assert "INTERVAL_END" in _stop
        assert "stopwatch sleep 1" in _start
        assert "stopwatch sleep 1" in _stop
        close_logger(StopWatch.mllogger.logger)


    def test_stopwatch_2(self):
        HEADING()
        Shell.rm("cloudmesh_mllog.log")
        StopWatch.activate_mllog()
        StopWatch.start("stopwatch sleep 2")
        time.sleep(0.1)
        StopWatch.stop("stopwatch sleep 2")
        StopWatch.status("stopwatch sleep 2", True)
        content = readfile("cloudmesh_mllog.log").splitlines()
        _start = content[0]
        _stop = content[1]

        print(_start)
        print(_stop)

        assert "INTERVAL_START" in _start
        assert "INTERVAL_END" in _stop
        assert "stopwatch sleep 2" in _start
        assert "stopwatch sleep 2" in _stop
        close_logger(StopWatch.mllogger.logger)

    def test_stopwatch_loop_sum(self):
        HEADING()
        Shell.rm("cloudmesh_mllog.log")
        StopWatch.activate_mllog()
        dt = 0.1
        n = 10
        for i in range(0,n):
            StopWatch.start("stopwatch loop")
            time.sleep(dt)
            StopWatch.stop("stopwatch loop")
            StopWatch.status("stopwatch loop", True)
            t = StopWatch.get("stopwatch loop")
            print (t)
            assert t >= dt

        t = StopWatch.sum("stopwatch loop", digits=4)

        print(t)

        assert t >= n * dt
        close_logger(StopWatch.mllogger.logger)

    def test_stopwatch_loop_individual(self):
        HEADING()
        Shell.rm("cloudmesh_mllog.log")
        StopWatch.activate_mllog()
        dt = 0.1
        n = 10
        for i in range(0,n):
            StopWatch.start(f"stopwatch loop")
            time.sleep(dt)
            StopWatch.stop(f"stopwatch loop")
            StopWatch.message(f"stopwatch loop", i)
            StopWatch.status(f"stopwatch loop", True)
            t = StopWatch.get(f"stopwatch loop")
            print(t)
            assert t >= dt

        t = StopWatch.sum("stopwatch loop", digits=4)

        print (t)

        assert t >= n * dt
        close_logger(StopWatch.mllogger.logger)

    def test_stopwatch_dict_event(self):
        HEADING()
        Shell.rm("cloudmesh_mllog.log")
        StopWatch.activate_mllog()
        data = {"a": 1}
        StopWatch.event("stopwtch dict event", values=data)
        content = readfile("cloudmesh_mllog.log").splitlines()[-1]

        print (content)
        assert '"a": 1' in content
        assert '"key": "POINT_IN_TIME"' in content
        assert '"name": "stopwtch dict event"' in content
        close_logger(StopWatch.mllogger.logger)

    def test_stopwatch_organization(self):
        HEADING()
        StopWatch.activate_mllog()
        data = yaml.safe_load(benchmark_config)
        StopWatch.organization_mllog(data)

        content = readfile("cloudmesh_mllog.log").splitlines()
        print ("---")
        pprint (content)

        content = readfile("cloudmesh_mllog.log")
        assert '"namespace": "cloudmesh"' in content
        assert '"event_type": "POINT_IN_TIME", "key": "submission_poc_name"' in content
        assert '"value": "Gregor von Laszewski"' in content
        assert '"event_type": "POINT_IN_TIME", "key": "submission_poc_email"' in content
        assert '"value": "laszewski@gmail.com"' in content
        assert '"event_type": "POINT_IN_TIME", "key": "submission_org"' in content
        assert '"value": "University of Virginia"' in content
        assert '"event_type": "POINT_IN_TIME", "key": "submission_division"' in content
        assert '"value": "BII"' in content
        assert '"event_type": "POINT_IN_TIME", "key": "submission_status"' in content
        assert '"value": "success"' in content
        assert '"event_type": "POINT_IN_TIME", "key": "submission_platform"' in content
        assert '"value": "rivanna"' in content
        close_logger(StopWatch.mllogger.logger)

    # def test_stopwatch_organization_2(self):
    #     HEADING()
    #     data = yaml.safe_load(benchmark_config)
    #     StopWatch.organization_mllog(data)
    #
    #     content = readfile("cloudmesh_mllog.log").splitlines()
    #     print("---")
    #     pprint(content)
    #
    #     content = readfile("cloudmesh_mllog.log")
    #
    # def test_manual_test(self):
    #     HEADING()
    #     Shell.rm("cloudmesh_mllog.log")
    #     StopWatch.clear()
    #     # this code is in a manula README-mlcommons.md
    #
    #     # define the organization
    #
    #     config = """
    #     benchmark:
    #       name: Earthquake
    #       user: Gregor von Laszewski
    #       e-mail: laszewski@gmail.com
    #       organisation:  University of Virginia
    #       division: BII
    #       status: success
    #       platform: rivanna
    #       badkey: ignored
    #     """.strip()
    #
    #     submitter = yaml.safe_load(config)
    #
    #     # activate the MLcommons logger
    #     StopWatch.activate_mllog()
    #
    #     StopWatch.organization_mllog(**submitter)
    #
    #     # save an event with a value
    #     StopWatch.event("test", values="1")
    #
    #     # save a dict in an event
    #     data = {"a": 1}
    #     StopWatch.event("stopwtch dict event", values=data)
    #
    #     # start a timer
    #     StopWatch.start("stopwatch sleep")
    #
    #     # do some work
    #     time.sleep(0.1)
    #
    #     # stop the timer
    #     StopWatch.stop("stopwatch sleep")
    #
    #     # print the table
    #     StopWatch.benchmark(tag="Earthquake", node="summit", user="Gregor", version="0.1")

    #StopWatch.log_constant(**log)



    # def test_stopwatch_log_event(self):
    #     HEADING()
    #     data = { "a": 1 }
    #     with intercept_mllogger() as log_stream:
    #         StopWatch.log_event(values=data)
    #     log_text = log_stream.getvalue()
    #     assert ':::MLLOG' in log_text, 'logger must have mllog entries when activated'
    #
    #     log_object = convert_mllog_to_object(log_stream)
    #     assert (
    #         all(list(map(lambda x: x['namespace'] == "cloudmesh", log_object))),
    #         "Logger must have cloudmesh namespace."
    #     )
    #
    #     assert (
    #         any(list(map(lambda x: x['key'] == "mllog-event-values", log_object))),
    #         "Logger event keys must apply the key label across all logs"
    #     )
    #
    #     for x in log_object:
    #         if x['event_type'] == "POINT_IN_TIME":
    #             assert isinstance(x['value'], str), "Value must be converted to string."
    #             assert x['value'] == str(data), "Event data must capture passed values in string format"
    #     assert len(log_object) == 1, "MLPerf logging must not trigger start/stop entries when logging event"
    #
    # def test_stopwatch_log_constant(self):
    #     HEADING()
    #     data = {"a": 1}
    #     log = {"DEFAULT_LOGGER_NAME": "testing default logger name"}
    #     with intercept_mllogger() as log_stream:
    #         StopWatch.log_constant(**log)
    #     log_text = log_stream.getvalue()
    #     assert ':::MLLOG' in log_text, 'logger must have mllog entries when activated'
    #     log_object = convert_mllog_to_object(log_stream)
    #     for x in log_object:
    #         if x['event_type'] == "POINT_IN_TIME":
    #             assert (
    #                 x['key'] == mllog_constants["DEFAULT_LOGGER_NAME"],
    #                 "Logged key must match string representation in mlperf_logging"
    #             )
    #
    # def test_stopwatch_log_evalblock(self):
    #     HEADING()
    #     data = { "a": 1, "b": 5 }
    #     with intercept_mllogger() as log_stream:
    #         StopWatch.start("Test Notebook", mllog_key="BLOCK_START")
    #         StopWatch.log_event(MY_TEST_KEY=data)
    #         time.sleep(2)
    #         StopWatch.stop("Test Notebook", values=data, mllog_key="BLOCK_STOP")
    #     log_text = log_stream.getvalue()
    #     assert ':::MLLOG' in log_text, 'logger must have mllog entries when activated'
    #
    #     log_object = convert_mllog_to_object(log_stream)
    #
    #     assert len(log_object) == 3, "Multiple log entires should be independent events"
    #
    #     assert (
    #         log_object[0]["event_type"] == "INTERVAL_START" and \
    #         log_object[1]["event_type"] == "POINT_IN_TIME" and \
    #         log_object[2]["event_type"] == "INTERVAL_END",
    #         "Events must occur in sequence."
    #     )
    #
    #     assert (
    #         log_object[0]["key"] == "block_start",
    #         "mllog_key constant references should dereference when logged."
    #     )
    #     assert (
    #         log_object[1]["key"] == "mllog-event-MY_TEST_KEY",
    #         "Log events that do not map to mllog constants should be prefixed with 'mllog-event-'"
    #     )
    #     assert (
    #         log_object[1]["value"] == str(data),
    #         "Logged events should persist data in string format"
    #     )
    #     assert (
    #         log_object[2]["value"] == str(data),
    #         "Events must support the persistance of values."
    #     )
    #     assert (
    #         log_object[0]["value"] is None,
    #         "Events must not require values."
    #     )
    #
    # def test_stopwatch_log_evalblock(self):
    #     HEADING()
    #     with intercept_mllogger() as log_stream:
    #         StopWatch.start("Test Notebook", mllog_key="BLOCK_START")
    #         StopWatch.stop("Test Notebook", mllog_key="BLOCK_STOP")
    #     log_text = log_stream.getvalue()
    #
    # def test_stopwatch_organization_mllog(self):
    #     for method in (True, False):
    #         with yaml_generator('test.yml', flat=method) as f:
    #             with intercept_mllogger() as log_stream:
    #                 StopWatch.start("Test Notebook", mllog_key="BLOCK_START")
    #                 StopWatch.organization_mllog(f, prefix_="general", flatdict_=method)
    #                 StopWatch.stop("Test Notebook", mllog_key="BLOCK_STOP")
    #             log_text = log_stream.getvalue()
    #             assert ':::MLLOG' in log_text, 'logger must have mllog entries when activated'
    #             log_object = convert_mllog_to_object(log_stream)
    #             assert log_object[1]['key'] == "submission_benchmark" and log_object[1]['value'] == "Earthquake" and \
    #                    log_object[2]['key'] == "submission_poc_name" and log_object[2]['value'] == "Gregor von Laszewski" and \
    #                    log_object[3]['key'] == "submission_poc_email" and log_object[3]['value'] == "laszewski@gmail.com" and \
    #                    log_object[4]['key'] == "submission_org" and log_object[4]['value'] == "University of Virginia" and \
    #                    log_object[5]['key'] == "submission_division" and log_object[5]['value'] == "BII" and \
    #                    log_object[6]['key'] == "submission_status" and log_object[6]['value'] == "submission" and \
    #                    log_object[7]['key'] == "submission_platform" and log_object[7]['value'] == "rivanna"
    #             assert not any([obj['value'] == "ignored" for obj in log_object])
    #
    #

    def test_benchmark(self):
        HEADING()
        StopWatch.benchmark(sysinfo=False, tag="cc-db", user="test", node="test")
