###############################################################
# pytest -v --capture=no  tests/test_host.py
# pytest -v --capture=no  tests/test_host..py::Test_host.test_001
# pytest -v tests/test_host.py
###############################################################
import getpass

from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import HEADING
import pytest
from cloudmesh.common.Host import Host
from cloudmesh.common.Host import Execution


@pytest.mark.incremental
class Test_host(object):

    def test_001_pwd(self):
        HEADING()

        result = Execution.run("whoami")
        print(result)
        assert getpass.getuser() in r
