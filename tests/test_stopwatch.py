###############################################################
# pytest -v --capture=no tests/test_stopwatch.py
# pytest -v --capture=no tests/test_stopwatch..py::Test_stopwatch.test_001
# pytest -v  tests/test_stopwatch.py
###############################################################

import time

import pytest
from cloudmesh.common.StopWatch import StopWatch

from cloudmesh.common.util import HEADING


@pytest.mark.incremental
class Test_Printer:

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

    def test_stopwatch_loop(self):
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


    def test_print(self):
        StopWatch.benchmark(sysinfo=True, csv=True, sum=True)
        assert True
