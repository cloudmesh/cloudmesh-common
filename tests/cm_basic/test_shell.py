""" run with

python setup.py install; nosetests -v --nocapture tests/cm_basic/test_shell.py:Test_shell.test_001

nosetests -v --nocapture tests/cm_basic/test_shell.py

or

nosetests -v tests/cm_basic/test_shell.py

"""
from __future__ import print_function

from cloudmesh_client.common.Shell import Shell
from cloudmesh_client.common.util import HEADING


def run(command):
    parameter = command.split(" ")
    shell_command = parameter[0]
    args = parameter[1:]
    result = Shell.execute(shell_command, args)
    return str(result)


# noinspection PyMethodMayBeStatic,PyPep8Naming
class Test_shell(object):
    """

    """

    def setup(self):
        pass

    def test_001(self):
        HEADING("check if we can run help:return: ")
        r = run("cm help")
        print(r)
        assert "Documented commands" in r

        assert "banner" in r
        assert "help" in r
        assert "EOF" in r
        assert "q" in r
        assert "quit" in r
