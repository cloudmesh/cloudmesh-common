###############################################################
# pip install .; pytest -v --capture=no tests/test_stopwatch.py:Test_stopwatch.test_001
# pytest -v --capture=no tests/test_stopwatch.py
# pytest -v  tests/test_stopwatch.py
###############################################################

from __future__ import print_function
from cloudmesh.common.util import HEADING
from cloudmesh.common.StopWatch import StopWatch
import pytest
import time


@pytest.mark.incremental
class Test_Printer:

    def test_stopwatch(self):
        HEADING()
        StopWatch("sleep 1")
        time.sleep(1)
        StopWatch("sleep 1")
        StopWatch.benchmark(sysinfo=True)
        assert True
