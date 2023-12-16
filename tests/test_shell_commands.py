###############################################################
# pytest -v --capture=no  tests/test_shell_commands.py
# pytest -v tests/test_shell_commands.py
# pytest -v --capture=no  tests/test_shell_commands.py::Test_shell.test_001
###############################################################
import getpass
import os
from pathlib import Path

import pytest
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.Shell import Shell
from cloudmesh.common.systeminfo import os_is_windows, os_is_linux
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import path_expand


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

    def setup_method(self):
        pass

    def test_shell_mkdir(self):
        HEADING()

        os.system('rm -rf shell-directory')
        os.system('rm -rf shell-new-dir/another-dir')
        os.system('rm -rf ~/shell-dir')
        Benchmark.Start()
        Shell.mkdir('shell-directory')
        assert os.path.exists('shell-directory')
        Shell.mkdir('shell-new-dir/another-dir')
        assert os.path.exists('shell-new-dir/another-dir')
        Shell.mkdir('~/shell-dir')
        dir = os.path.join(Path.home(), 'shell-dir')
        assert os.path.exists(dir)
        Benchmark.Stop()
        os.system('rm -rf shell-directory')
        os.system('rm -rf shell-new-dir/another-dir')
        os.system('rm -rf ~/shell-dir')

    def test_map_filename(self):
        HEADING()
        Benchmark.Start()
        # user = os.path.basename(os.environ["HOME"])
        # the above is not necessarily the user in windows.
        user = getpass.getuser()

        if os_is_windows():
            pwd = os.getcwd().replace("C:","/mnt/c").replace("\\","/")
        else:
            pwd = os.getcwd()

        print("pwd",pwd)

        ## wsl:~/dir         /mnt/c/Users/USER/dir
        # wsl:dir           /mnt/c/Users/USER/{PWD}/dir
        # wsl:./dir         /mnt/c/Users/USER/{PWD}/dir
        ## wsl:/mnt/c/Users  /mnt/c/Users
        # wsl:/dir          /dir

        result = Shell.map_filename(name='wsl:~/cm')
        assert result.user == user
        assert result.host == 'wsl'
        if os_is_linux():
            assert result.path == f'/mnt/c/home/{user}/cm'
        else:
            assert result.path == f'/mnt/c/Users/{user}/cm'

        result = Shell.map_filename(name='wsl:dir')
        assert result.user == user
        assert result.host == 'wsl'
        assert result.path == f'{pwd}/dir'

        result = Shell.map_filename(name='wsl:./dir')
        assert result.user == user
        assert result.host == 'wsl'
        assert result.path == f'{pwd}/dir'

        result = Shell.map_filename(name='wsl:/mnt/c/home')
        assert result.user == user
        assert result.host == 'wsl'
        assert result.path == f'/mnt/c/home'

        result = Shell.map_filename(name='C:~/cm')
        assert result.user == user
        assert result.host == 'localhost'
        if os_is_linux():
            if user == 'root':
                assert result.path == f'C:\\root\\cm'
            else:
                assert result.path == f'C:\\home\\{user}\\cm'
        else:
            if os_is_windows():
                assert result.path == os.path.join(str(Path.home()), 'cm')

        result = Shell.map_filename(name='scp:user@host:~/cm')
        assert result.user == "user"
        assert result.host == 'host'
        assert result.path == f'~/cm'

        result = Shell.map_filename(name='scp:user@host:/tmp')
        assert result.user == "user"
        assert result.host == 'host'
        assert result.path == f'/tmp'

        result = Shell.map_filename(name='~/cm')
        assert result.user == user
        assert result.host == 'localhost'
        assert result.path == path_expand('~/cm')

        result = Shell.map_filename(name='/tmp')
        assert result.user == user
        assert result.host == 'localhost'
        if os_is_windows():
            assert result.path == '\\tmp'
        else:
            assert result.path == '/tmp'

        Shell.mkdir("./tmp")
        result = Shell.map_filename(name='./tmp')

        assert result.user == user
        assert result.host == 'localhost'
        assert str(result.path) == path_expand('./tmp')

        Shell.rmdir("./tmp")
        assert os.path.exists(path_expand('./tmp')) == False
        Benchmark.Stop()

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

