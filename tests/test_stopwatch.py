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
        StopWatch.start("sleep 1")
        time.sleep(0.1)
        StopWatch.stop("sleep 1")
        assert True

    def test_stopwatch_2(self):
        HEADING()
        StopWatch.start("sleep 2")
        time.sleep(0.1)
        StopWatch.stop("sleep 2")

        StopWatch.benchmark(sysinfo=True, csv=True)
        assert True
