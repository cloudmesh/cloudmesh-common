###############################################################
# pip install .; npytest -v --capture=no  tests/test_shell.py:Test_shell.test_001
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

    """
    def test_(self):
        HEADING()
        r = run("")
        print(r)
        assert True

    def get_python(cls):
    def check_python(cls):
    def pip(cls, *args):

    def mkdir(cls, directory):
    def rmdir(top, verbose=False):
        def cat(cls, *args):

    def live(cls, command, cwd=None):
    def check_output(cls, *args, **kwargs):
    def ls(cls, *args):
    def ps(cls, *args):
    def bash(cls, *args):
    def git(cls, *args):
    def head(cls, *args):
    def kill(cls, *args):
    def ping(cls, host=None, count=1):
    def pwd(cls, *args):
    def rm(cls, *args):
    def scp(cls, *args):
    def sort(cls, *args):
    def sh(cls, *args):
    def ssh(cls, *args):
    def tail(cls, *args):
    def fgrep(cls, *args):
    def grep(cls, *args):
    def cm_grep(cls, lines, what):
    def remove_line_with(cls, lines, what):
    def find_lines_with(cls, lines, what):
    def terminal_type(cls):
    def which(cls, command):
    def command_exists(cls, name):
    def operating_system(cls):
    def unzip(cls, source_filename, dest_dir):
    def distribution(cls):
"""


# not tested
"""
    def browser(filename):
    def terminal(cls, command='pwd'):
    def brew(cls, *args):
    def VBoxManage(cls, *args):
    def blockdiag(cls, *args):
    def cm(cls, *args):
    def cms(cls, *args):
    def cmsd(cls, *args):
    def keystone(cls, *args):
    def nova(cls, *args):
    def rackdiag(cls, *args):
    def rsync(cls, *args):
    def sudo(cls, *args):
    def pandoc(cls, *args):
    def mongod(cls, *args):
    def dialog(cls, *args):
    def lsb_release(cls):
    def vagrant(cls, *args):
    def edit(filename):

"""

