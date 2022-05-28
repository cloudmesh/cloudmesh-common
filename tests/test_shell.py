###############################################################
# pytest -v --capture=no  tests/test_shell.py
# pytest -v tests/test_shell.py
# npytest -v --capture=no  tests/test_shell.py::Test_shell.test_001
###############################################################
import getpass
import subprocess

from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import HEADING
from cloudmesh.common.systeminfo import os_is_windows
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

    def test_whoami(self):
        HEADING()
        try:
            r = Shell.run("whoami").strip()
        except Exception as e:
            print(e)
        print("whoami:",r)
        if os_is_windows:
            assert r is not ''
        else:
            assert getpass.getuser() in r

    def test_which(self):
        HEADING()
        r = Shell.which("python")
        print(r)
        assert r is not None
