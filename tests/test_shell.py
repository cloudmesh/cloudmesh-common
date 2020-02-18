###############################################################
# pip install .; npytest -v --capture=no  tests/test_shell..py::Test_shell.test_001
# pytest -v --capture=no  tests/test_shell.py
# pytest -v tests/test_shell.py
###############################################################
import getpass

from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import HEADING
import pytest


def run(command):
    parameter = command.split(" ")
    shell_command = parameter[0]
    args = parameter[1:]
    result = Shell.execute(shell_command, args)
    return str(result)



@pytest.mark.incremental
class Test_shell(object):
    """

    """

    def setup(self):
        pass

    def test_001(self):
        HEADING("check if we can run help:return: ")
        r = run("whoami")
        print(r)
        assert getpass.getuser() in r
