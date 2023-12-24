###############################################################
# pytest -v --capture=no  tests/test_host.py
# pytest -v --capture=no  tests/test_host..py::Test_host.test_001
# pytest -v tests/test_host.py
###############################################################
import getpass

import pytest
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import HEADING


# from cloudmesh.common.Host import Host


@pytest.mark.incremental
class Test_host(object):

    def test_001_whoami(self):
        HEADING()

        result = Shell.run("whoami")
        print(result)
        assert getpass.getuser() in result
