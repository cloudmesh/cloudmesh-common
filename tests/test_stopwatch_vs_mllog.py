###############################################################
# pytest -v --capture=no tests/test_stopwatch_mllog.py
# pytest -v --capture=no tests/test_stopwatch_mllog.py::Test_stopwatch.test_001
# pytest -v  tests/test_stopwatch_mllog.py
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
from pprint import pprint
import textwrap

import yaml

from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import readfile

import pytest
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.console import Console

from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner

# MLCommons logging
from mlperf_logging import mllog
import logging


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

def clean():
    Shell.rm("cloudmesh_mllog.log")
    StopWatch.clear()

def read_mllog(filename):
    content = readfile(filename)
    content = content.replace(":::MLLOG ", "").replace("null", "None").strip().splitlines()
    data = []
    for line in content:
        try:
            entry = eval(line)
            del entry["time_ms"]
            del entry["metadata"]
            del entry["namespace"]
            data.append(entry)
        except Exception as e:
            Console.error(e, traceflag=True)
    return data


@pytest.mark.incremental
class Test_Printer:

    def test_mllog_example_py(self):
        HEADING()
        clean()
        StopWatch.clear()

        os.system("python tests/mllog-example.py")

        content = readfile("cloudmesh_mllog.log")
        print ("---")
        print (content)
        print ("---")
        assert "cloudmesh-common/cloudmesh/common/StopWatch.py" not in content
        assert False
        assert '"INTERVAL_END", "key": "stopwatch sleep", "value": "stopwatch sleep"' in content
        assert '"event_type": "POINT_IN_TIME", "key": "submission_benchmark", "value": "Earthquake"' in content

class a:

    def test_mllog_native(self):
        HEADING()
        clean()
        StopWatch.clear()

        Shell.rm("cloudmesh_mlperf_native.log")

        os.system("python tests/mllog-native.py")

        content = readfile("cloudmesh_mlperf_native.log")
        print("---")
        print(content)
        print("---")
        assert "cloudmesh-common/cloudmesh/common/StopWatch.py" not in content
        # assert '"INTERVAL_END", "key": "stopwatch sleep", "value": "stopwatch sleep"' in content
        # assert '"event_type": "POINT_IN_TIME", "key": "submission_benchmark", "value": "Earthquake"' in content

        correct = textwrap.dedent("""
        "event_type": "POINT_IN_TIME", "key": "submission_benchmark", "value": "Earthquake",
        "event_type": "POINT_IN_TIME", "key": "submission_org", "value": "University of Virginia",
        "event_type": "POINT_IN_TIME", "key": "submission_division", "value": "BII",
        "event_type": "POINT_IN_TIME", "key": "submission_status", "value": "success",
        "event_type": "POINT_IN_TIME", "key": "submission_platform", "value": "rivanna",
        "event_type": "INTERVAL_START", "key": "init_start", "value": null,
        "event_type": "POINT_IN_TIME", "key": "number_of_ranks", "value": 1,
        "event_type": "POINT_IN_TIME", "key": "number_of_nodes", "value": 1,
        "event_type": "POINT_IN_TIME", "key": "accelerators_per_node", "value": 1,
        "event_type": "INTERVAL_END", "key": "init_stop", "value": null,
        "event_type": "POINT_IN_TIME", "key": "eval_start", "value": "Start Taining",
        "event_type": "POINT_IN_TIME", "key": "eval_stop", "value": "Stop Training",
        "event_type": "POINT_IN_TIME", "key": "eval_start", "value": "Start Inference",
        "event_type": "POINT_IN_TIME", "key": "eval_stop", "value": "Stop Inference",
        "event_type": "INTERVAL_END", "key": "run_stop", "value": "Benchmark run finished",
        """).strip().splitlines()

        print("---")
        print(content)
        print("---")

        for line in correct:
            assert line in content
        
        
    def test_mllog_stopwatch_native_compare(self):
        HEADING()
        clean()
        StopWatch.clear()
        StopWatch.activate_mllog()

        # StopWatch.start("RUN_START", value="Benchmark start")

        data = yaml.safe_load(benchmark_config)

        StopWatch.organization_mllog(**data)

        StopWatch.start("total", mllog_key="RUN_START")

        StopWatch.start("initialization", mllog_key="INIT_SATRT")

        StopWatch.event('number_of_ranks', value=1)
        StopWatch.event('number_of_nodes', value=1)
        StopWatch.event('accelerators_per_node', value=1)

        StopWatch.stop("initialization", mllog_key="INIT_STOP")

        # Training
        start = time.time()
        StopWatch.start("training", mllog_key="EVAL_START", value="Start Taining")
        StopWatch.stop("training", mllog_key="EVAL_STOP", value="Stop Training")

        # Inference
        start = time.time()
        StopWatch.start("inference", mllog_key="EVAL_START", value="Start: Inference")
        StopWatch.stop("inference", mllog_key="EVAL_STOP", value="Stop: Inference")

        StopWatch.stop("total", mllog_key="RUN_STOP", value="Benchmark run finished", metadata={'status': 'success'})

        banner("NATIVE")
        native_log = read_mllog("cloudmesh_mlperf_native.log")
        pprint(native_log)

        banner("CLOUDMESH")
        cloudmesh_log = read_mllog("cloudmesh_mllog.log")
        pprint(cloudmesh_log)


        # assert native_log == cloudmesh_log

class b:

    def test_mllog_example_py(self):
        HEADING()
        clean()
        StopWatch.clear()

        os.system("python tests/mllog-example.py")

        content = readfile("cloudmesh_mllog.log")
        print ("---")
        print (content)
        print ("---")
        assert "cloudmesh-common/cloudmesh/common/StopWatch.py" not in content
        assert False
        assert '"INTERVAL_END", "key": "stopwatch sleep", "value": "stopwatch sleep"' in content
        assert '"event_type": "POINT_IN_TIME", "key": "submission_benchmark", "value": "Earthquake"' in content


class a:

    def test_check_loading(self):
        HEADING()
        clean()
        StopWatch.activate_mllog()
        StopWatch.mllogger.event("test", "1", stack_offset=1)
        content = readfile("cloudmesh_mllog.log").splitlines()
        line = Shell.find_lines_with(content, what='"key": "test"')[0]
        print (line)
        assert "cloudmesh-common/tests/test_stopwatch_mllog.py" in line
        assert '"value": "1"' in line
        assert '"value": "1"' in line
        assert "cloudmesh-common/cloudmesh/common/StopWatch.py" not in line

    def test_stopwatch_activate_mllog(self):
        HEADING()
        clean()
        StopWatch.activate_mllog()
        print(StopWatch.mllogging)
        assert StopWatch.mllogging == True

    def test_stopwatch_1(self):
        HEADING()
        StopWatch.start("stopwatch sleep 1")
        time.sleep(0.1)
        StopWatch.stop("stopwatch sleep 1")
        StopWatch.status("stopwatch sleep 1", True)
        content = readfile("cloudmesh_mllog.log").splitlines()
        _start = content[0]
        _stop = content[1]

        print()
        print (_start)
        print (_stop)

        assert "cloudmesh-common/cloudmesh/common/StopWatch.py" not in _start
        assert "cloudmesh-common/cloudmesh/common/StopWatch.py" not in _stop

        assert "INTERVAL_START" in _start
        assert "INTERVAL_END" in _stop
        assert "stopwatch sleep 1" in _start
        assert "stopwatch sleep 1" in _stop
        assert True

    def test_stopwatch_2(self):
        HEADING()
        StopWatch.start("stopwatch sleep 2")
        time.sleep(0.1)
        StopWatch.stop("stopwatch sleep 2")
        StopWatch.status("stopwatch sleep 2", True)
        content = readfile("cloudmesh_mllog.log").splitlines()
        _start = content[2]
        _stop = content[3]

        print()
        print (_start)
        print (_stop)

        assert "cloudmesh-common/cloudmesh/common/StopWatch.py" not in _start
        assert "cloudmesh-common/cloudmesh/common/StopWatch.py" not in _stop

        assert "INTERVAL_START" in _start
        assert "INTERVAL_END" in _stop
        assert "stopwatch sleep 2" in _start
        assert "stopwatch sleep 2" in _stop

        assert True

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

        content = readfile("cloudmesh_mllog.log")
        assert "cloudmesh-common/cloudmesh/common/StopWatch.py" not in content

    def test_stopwatch_loop_individual(self):
        HEADING()
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
        content = readfile("cloudmesh_mllog.log")
        assert "cloudmesh-common/cloudmesh/common/StopWatch.py" not in content

    def test_stopwatch_dict_event(self):
        HEADING()
        data = {"a": 1}
        t = StopWatch.event("stopwtch dict event", values=data)
        content = readfile("cloudmesh_mllog.log").splitlines()[-1]

        print (content)
        assert "{'a': 1}" in content
        assert '"key": "stopwtch dict event"' in content
        assert "cloudmesh-common/cloudmesh/common/StopWatch.py" not in str(content)

    def test_stopwatch_organization(self):
        HEADING()
        data = yaml.safe_load(benchmark_config)
        StopWatch.organization_mllog(**data)

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
        assert '"value": "submission"' in content
        assert '"event_type": "POINT_IN_TIME", "key": "submission_platform"' in content
        assert '"value": "rivanna"' in content
        assert "cloudmesh-common/cloudmesh/common/StopWatch.py" not in str(content)


    def test_stopwatch_organization(self):
        HEADING()
        data = yaml.safe_load(benchmark_config)
        StopWatch.organization_mllog(**data)

        content = readfile("cloudmesh_mllog.log").splitlines()
        print("---")
        pprint(content)

        content = readfile("cloudmesh_mllog.log")
        assert "cloudmesh-common/cloudmesh/common/StopWatch.py" not in content


    def test_manual_test(self):
        HEADING()
        clean()
        StopWatch.clear()
        # this code is in a manula README-mlcommons.md

        # define the organization

        config = """
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

        submitter = yaml.safe_load(config)

        # activate the MLcommons logger
        StopWatch.activate_mllog()

        StopWatch.organization_mllog(**submitter)

        # save an event with a value
        StopWatch.event("test", values="1")

        # save a dict in an event
        data = {"a": 1}
        StopWatch.event("stopwtch dict event", values=data)

        # start a timer
        StopWatch.start("stopwatch sleep")

        # do some work
        time.sleep(0.1)

        # stop the timer
        StopWatch.stop("stopwatch sleep")

        # print the table
        StopWatch.benchmark(tag="Earthquake", node="summit", user="Gregor", version="0.1")

        content = readfile("cloudmesh_mllog.log")
        print ("---")
        print (content)
        print ("---")
        assert "cloudmesh-common/cloudmesh/common/StopWatch.py" not in content
        assert '"INTERVAL_END", "key": "stopwatch sleep", "value": "stopwatch sleep"' in content
        assert '"event_type": "POINT_IN_TIME", "key": "submission_benchmark", "value": "Earthquake"' in content

    def test_stopwatch_log_evalblock(self):
        HEADING()
        clean()
        StopWatch.activate_mllog()
        StopWatch.start("Test Notebook", mllog_key="BLOCK_START")
        StopWatch.stop("Test Notebook", mllog_key="BLOCK_STOP")

        content = readfile("cloudmesh_mllog.log")
        print("---")
        print(content)
        print("---")
        assert "cloudmesh-common/cloudmesh/common/StopWatch.py" not in content
        assert '"event_type": "INTERVAL_START", "key": "block_start"' in content


    def test_stopwatch_block_log_data(self):
        HEADING()
        clean()
        StopWatch.activate_mllog()
        data = { "a": 1, "b": 5 }

        StopWatch.start("Test Notebook", mllog_key="BLOCK_START")
        StopWatch.log_event(MY_TEST_KEY=data)
        time.sleep(0.1)
        StopWatch.stop("Test Notebook", values=data, mllog_key="BLOCK_STOP")

        content = readfile("cloudmesh_mllog.log")
        print("---")
        print(content)
        print("---")
        assert "cloudmesh-common/cloudmesh/common/StopWatch.py" not in content
        assert '"event_type": "INTERVAL_END"' in content
        assert "{'a': 1, 'b': 5, 'name': 'Test Notebook'}" in content

    def test_benchmark(self):
        HEADING()
        StopWatch.benchmark(sysinfo=False, tag="cc-db", user="test", node="test")
