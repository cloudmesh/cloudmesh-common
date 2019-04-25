###############################################################
# pip install .; npytest -v --capture=no  tests/test_ping.py:Test_ping.test_001
# pytest -v --capture=no  tests/test_ping.py
# pytest -v tests/test_ping.py
###############################################################
from __future__ import print_function

import getpass

from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import HEADING
import pytest

@pytest.mark.incremental
class Test_ping:

    def setup(self):
        pass

    def test_001(self):
        HEADING()
        result = Shell.pings(ips=['google.com', 'youtube.com', 'com'], count=3, processors=3)
        assert {'google.com': 0} in result
        assert {'youtube.com': 0} in result
        assert {'com': 0} not in result
