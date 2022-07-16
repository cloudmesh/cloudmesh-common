###############################################################
# pytest -v --capture=no tests/test_stopwatch.py
# pytest -v --capture=no tests/test_stopwatch..py::Test_stopwatch.test_001
# pytest -v  tests/test_stopwatch.py
###############################################################

from typing import Dict, Any
import json
import time

import pytest
from cloudmesh.common.StopWatch import StopWatch

from cloudmesh.common.util import HEADING

from io import StringIO  # Python 3
import sys


def convert_mllog_to_object(log_stream: StringIO):
    obj = list()
    text = log_stream.getvalue().replace(":::MLLOG ", "")
    for x in text.split("\n"):
        if x != "":
            obj.append(json.loads(x))
    return obj


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
        # Create the in-memory "file"
        temp_out = StringIO()
        # Replace default stdout (terminal) with our stream
        sys.stdout = temp_out
        data = {"a": 1}
        StopWatch.activate_mllog()
        t = StopWatch.log_event(values=data)
        sys.stdout = sys.__stdout__
        log_text = temp_out.getvalue()
        assert ':::MLLOG' in log_text, 'logger must have mllog entries when activated'

        log_object = convert_mllog_to_object(temp_out)
        import pprint
        pprint.pprint(log_object)
        assert all(list(map(lambda x: x['namespace'] == "cloudmesh", log_object))), "Logger must have cloudmesh namespace."

        assert (any(list(map(lambda x: x['key'] == "mllog-start-values", log_object))) and
                any(list(map(lambda x: x['key'] == "mllog-stop-values", log_object))) and
                any(list(map(lambda x: x['key'] == "mllog-event-values", log_object)))), "Logger event keys must apply the key label across all logs"

        for x in log_object:
            if x['event_type'] == "POINT_IN_TIME":
                assert isinstance(x['value'], str), "Value must be converted to string."
                assert x['value'] == str(data), "Event data must capture passed values in string format"
