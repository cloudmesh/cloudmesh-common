# ##############################################################
# pytest -v --capture=no tests/test_browser.py
# pytest -v  tests/test_browser.py
# pytest -v --capture=no  tests/test_browser.py::TestBrowser::<METHODNAME>
# ##############################################################

"""
This is the test for Shell.browser.
"""

from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import HEADING
from cloudmesh.common.Benchmark import Benchmark

import time


class TestBrowser:

    def test_shell_browser(self):
        HEADING()
        Benchmark.Start()
        # Shell.copy("test-graphviz.svg", '/tmp/test-graphviz.svg')
        # Shell.copy("test-graphviz.svg", "~/test-graphviz.svg")
        # r = Shell.browser("~/test-graphviz.svg")
        # Shell.copy("test-graphviz.svg", f"{Path.home()}/test-graphviz.svg")
        r = Shell.browser(f'http://google.com')
        print('testing unsecured')
        time.sleep(3)
        r = Shell.browser(f'https://google.com')
        print('testing secured')
        time.sleep(3)
        r = Shell.browser(f"C:/Users/abeck/cm/cloudmesh-cc/test-graphviz.svg")
        print('i just tried a fullpath')
        time.sleep(3)
        r = Shell.browser(f"file:///C:/Users/abeck/cm/cloudmesh-cc/test-graphviz.svg")
        print('i just tried with file:')
        time.sleep(3)
        r = Shell.browser(f"~/test-graphviz.svg")
        print('i just opened the home dir and the svg in there')
        time.sleep(5)
        r = Shell.browser(f'test-graphviz.svg')
        print('i just tried no slashes')
        time.sleep(5)
        r = Shell.browser(f'./test-graphviz.svg')
        print('i just tried something wacky')
        time.sleep(5)
        # assert r == path_expand(f'~/test-graphviz.svg')
        # input()
        # r = Shell.browser("file://~/test-graphviz.svg")
        # r = Shell.browser("test-graphviz.svg")
        # r = Shell.browser("file://test-graphviz.svg")
        # r = Shell.browser("file://tmp/test-graphviz.svg")
        # r = Shell.browser("http://google.com")
        # r = Shell.browser("https://google.com")
        print(r)
        Benchmark.Stop()
