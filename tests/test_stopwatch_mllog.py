###############################################################
# pytest -v --capture=no tests/test_stopwatch.py
# pytest -v --capture=no tests/test_stopwatch..py::Test_stopwatch.test_001
# pytest -v  tests/test_stopwatch.py
###############################################################

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

@contextlib.contextmanager
def yaml_generator(filename, prefix="general", flat=False):
    if flat:
        mllog_sampleyaml = f"""
name: ignored
{prefix}.name: Earthquake
{prefix}.user: Gregor von Laszewski
{prefix}.e-mail: laszewski@gmail.com
{prefix}.organisation:  University of Virginia
{prefix}.division: BII
{prefix}.status: submission
{prefix}.platform: rivanna
{prefix}.badkey: ignored
followon: ignored
"""
    else:
        mllog_sampleyaml=f"""
name: ignored
{prefix}:
  name: Earthquake
  user: Gregor von Laszewski
  e-mail: laszewski@gmail.com
  organisation:  University of Virginia
  division: BII
  status: submission
  platform: rivanna
  badkey: ignored
followon: ignored
"""
    my_tempdir = tempfile.gettempdir()
    temppath = pathlib.Path(my_tempdir) / filename
    with open(temppath, 'wb') as f:
        f.write(mllog_sampleyaml.encode('utf-8'))
    try:
        yield temppath
    finally:
        os.remove(temppath)



def convert_mllog_to_object(log_stream: StringIO):
    """Utility method to transform the mlperf logging strings into a python object.

    :param log_stream: An io-like object that contains a stream of newline split json strings
    :type log_stream: StringIO

    :returns: a list of python dictionaries representing the logging events.
    :rtype: list(dict)
    """
    obj = list()
    text = log_stream.getvalue().replace(":::MLLOG ", "")
    for x in text.split("\n"):
        if x != "":
            try:
                obj.append(json.loads(x))
            except json.JSONDecodeError as e:
                pass
    return obj


@contextlib.contextmanager
def intercept_mllogger(filename=None):
    """A context function used to capture logging events in mlperf.
    This method does so by directly registering a stream object to the logging
    module.

    :yields: a StringIO object that captures the StopWatch mllog events.
    """
    StopWatch.activate_mllog(filename=filename)
    temp_out = StringIO('')
    stream_handler = logging.StreamHandler(temp_out)
    StopWatch.mllogger.logger.addHandler(stream_handler)
    try:
        yield temp_out
    finally:
        StopWatch.mllogger.logger.removeHandler(stream_handler)


@pytest.mark.incremental
class Test_Printer:

    def test_stopwatch_activate_mllog(self):
        HEADING()
        StopWatch.activate_mllog()
        print(StopWatch.mllogging)
        assert StopWatch.mllogging == True

    def test_stopwatch_1(self):
        HEADING()
        StopWatch.start("stopwatch sleep 1")
        time.sleep(0.1)
        StopWatch.stop("stopwatch sleep 1")
        StopWatch.status("stopwatch sleep 1", True)
        assert True

    def test_stopwatch_2(self):
        HEADING()
        StopWatch.start("stopwatch sleep 2")
        time.sleep(0.1)
        StopWatch.stop("stopwatch sleep 2")
        StopWatch.status("stopwatch sleep 2", True)

    def test_stopwatch_loop_sum(self):
        HEADING()
        cumulate = False
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

        print (t)

        assert t >= n * dt

    def test_stopwatch_loop_individual(self):
        HEADING()
        cumulate = False
        dt = 0.1
        n = 10
        for i in range(0,n):
            StopWatch.start(f"stopwatch loop {i}")
            time.sleep(dt)
            StopWatch.stop(f"stopwatch loop {i}")
            StopWatch.message(f"stopwatch loop {i}", i)
            StopWatch.status(f"stopwatch loop {i}", True)
            t = StopWatch.get(f"stopwatch loop {i}")
            print (t)
            assert t >= dt

        t = StopWatch.sum("stopwatch loop", digits=4)

        print (t)

        assert t >= n * dt

    def test_stopwatch_event(self):
        HEADING()
        data = {"a": 1}
        t = StopWatch.event("stopwtch event", msg=data)

    def test_print(self):
        StopWatch.benchmark(sysinfo=True, csv=True, sum=True, tag="pytest")
        assert True

    def test_stopwatch_log_event(self):
        HEADING()
        data = { "a": 1 }
        with intercept_mllogger() as log_stream:
            StopWatch.log_event(values=data)
        log_text = log_stream.getvalue()
        assert ':::MLLOG' in log_text, 'logger must have mllog entries when activated'

        log_object = convert_mllog_to_object(log_stream)
        assert (
            all(list(map(lambda x: x['namespace'] == "cloudmesh", log_object))),
            "Logger must have cloudmesh namespace."
        )

        assert (
            any(list(map(lambda x: x['key'] == "mllog-event-values", log_object))),
            "Logger event keys must apply the key label across all logs"
        )

        for x in log_object:
            if x['event_type'] == "POINT_IN_TIME":
                assert isinstance(x['value'], str), "Value must be converted to string."
                assert x['value'] == str(data), "Event data must capture passed values in string format"
        assert len(log_object) == 1, "MLPerf logging must not trigger start/stop entries when logging event"

    def test_stopwatch_log_constant(self):
        HEADING()
        data = {"a": 1}
        log = {"DEFAULT_LOGGER_NAME": "testing default logger name"}
        with intercept_mllogger() as log_stream:
            StopWatch.log_constant(**log)
        log_text = log_stream.getvalue()
        assert ':::MLLOG' in log_text, 'logger must have mllog entries when activated'
        log_object = convert_mllog_to_object(log_stream)
        for x in log_object:
            if x['event_type'] == "POINT_IN_TIME":
                assert (
                    x['key'] == mllog_constants["DEFAULT_LOGGER_NAME"],
                    "Logged key must match string representation in mlperf_logging"
                )

    def test_stopwatch_log_evalblock(self):
        HEADING()
        data = { "a": 1, "b": 5 }
        with intercept_mllogger() as log_stream:
            StopWatch.start("Test Notebook", mllog_key="BLOCK_START")
            StopWatch.log_event(MY_TEST_KEY=data)
            time.sleep(2)
            StopWatch.stop("Test Notebook", values=data, mllog_key="BLOCK_STOP")
        log_text = log_stream.getvalue()
        assert ':::MLLOG' in log_text, 'logger must have mllog entries when activated'

        log_object = convert_mllog_to_object(log_stream)

        assert len(log_object) == 3, "Multiple log entires should be independent events"

        assert (
            log_object[0]["event_type"] == "INTERVAL_START" and \
            log_object[1]["event_type"] == "POINT_IN_TIME" and \
            log_object[2]["event_type"] == "INTERVAL_END",
            "Events must occur in sequence."
        )

        assert (
            log_object[0]["key"] == "block_start",
            "mllog_key constant references should dereference when logged."
        )
        assert (
            log_object[1]["key"] == "mllog-event-MY_TEST_KEY",
            "Log events that do not map to mllog constants should be prefixed with 'mllog-event-'"
        )
        assert (
            log_object[1]["value"] == str(data),
            "Logged events should persist data in string format"
        )
        assert (
            log_object[2]["value"] == str(data),
            "Events must support the persistance of values."
        )
        assert (
            log_object[0]["value"] is None,
            "Events must not require values."
        )

    def test_stopwatch_log_evalblock(self):
        HEADING()
        with intercept_mllogger() as log_stream:
            StopWatch.start("Test Notebook", mllog_key="BLOCK_START")
            StopWatch.stop("Test Notebook", mllog_key="BLOCK_STOP")
        log_text = log_stream.getvalue()

    def test_stopwatch_organization_mllog(self):
        for method in (True, False):
            with yaml_generator('test.yml', flat=method) as f:
                with intercept_mllogger() as log_stream:
                    StopWatch.start("Test Notebook", mllog_key="BLOCK_START")
                    StopWatch.organization_mllog(f, prefix_="general", flatdict_=method)
                    StopWatch.stop("Test Notebook", mllog_key="BLOCK_STOP")
                log_text = log_stream.getvalue()
                assert ':::MLLOG' in log_text, 'logger must have mllog entries when activated'
                log_object = convert_mllog_to_object(log_stream)
                assert log_object[1]['key'] == "submission_benchmark" and log_object[1]['value'] == "Earthquake" and \
                       log_object[2]['key'] == "submission_poc_name" and log_object[2]['value'] == "Gregor von Laszewski" and \
                       log_object[3]['key'] == "submission_poc_email" and log_object[3]['value'] == "laszewski@gmail.com" and \
                       log_object[4]['key'] == "submission_org" and log_object[4]['value'] == "University of Virginia" and \
                       log_object[5]['key'] == "submission_division" and log_object[5]['value'] == "BII" and \
                       log_object[6]['key'] == "submission_status" and log_object[6]['value'] == "submission" and \
                       log_object[7]['key'] == "submission_platform" and log_object[7]['value'] == "rivanna"
                assert not any([obj['value'] == "ignored" for obj in log_object])


