# ##############################################################
# pytest -v --capture=no tests/test_browser.py
# pytest -v  tests/test_browser.py
# pytest -v --capture=no  tests/test_browser.py::TestBrowser::<METHODNAME>
# ##############################################################

"""
This is the test for Shell.browser.
"""

import os
from pathlib import Path

from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import HEADING


class TestBrowser:

    def test_shell_browser(self):
        HEADING()
        Benchmark.Start()
        dir = os.path.join(Path.home(), 'cm/cloudmesh-common/tests/test.svg')
        # Shell.copy("test-graphviz.svg", '/tmp/test-graphviz.svg')
        # Shell.copy("test-graphviz.svg", "~/test-graphviz.svg")
        # r = Shell.browser("~/test-graphviz.svg")
        # Shell.copy("test-graphviz.svg", f"{Path.home()}/test-graphviz.svg")
        r = Shell.browser(f'https://google.com')
        r = Shell.browser(dir)
        r = Shell.browser(f"file:///{dir}")
        r = Shell.browser(f"~/cm/cloudmesh-common/tests/test.svg")
        r = Shell.browser(f'tests/test.svg')
        #r = Shell.browser(f'./test.svg')
        # assert r == path_expand(f'~/test-graphviz.svg')
        # input()
        # r = Shell.browser("file://~/test-graphviz.svg")
        # r = Shell.browser("file://test-graphviz.svg")
        # r = Shell.browser("file://tmp/test-graphviz.svg")
        print(r)
        Benchmark.Stop()
