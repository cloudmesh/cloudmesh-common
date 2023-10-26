###############################################################
# pytest -v --capture=no  tests/test_shell.py
# pytest -v tests/test_shell.py
# pytest -v --capture=no  tests/test_shell.py::Test_shell.test_001
###############################################################
import getpass
import subprocess

from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import HEADING
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.Benchmark import Benchmark
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

    def setup_method(self):
        pass

    def test_whoami(self):
        HEADING()
        Benchmark.Start()
        try:
            r = Shell.run("whoami").strip()
        except Exception as e:
            print(e)
        Benchmark.Stop()
        print("whoami:",r)
        if os_is_windows():
            assert r != ''
        else:
            assert getpass.getuser() in r

    def test_which(self):
        HEADING()
        Benchmark.Start()
        r = Shell.which("python")
        Benchmark.Stop()
        print(r)
        assert r is not None

    def test_ls(self):
        HEADING()
        Benchmark.Start()
        r = Shell.ls()
        Benchmark.Stop()
        print(r)
        assert 'VERSION' in r
        assert 'tests' in r

    def test_ps(self):
        HEADING()
        Benchmark.Start()
        r = Shell.ps()
        Benchmark.Stop()
        #print(r)
        assert r is not None

    def test_run(self):
        HEADING()
        Benchmark.Start()
        r1 = Shell.run('ls')
        r2 = Shell.run('pwd')
        r3 = Shell.run('hostname')
        print(r1)
        print(r2)
        print(r3)
        Benchmark.Stop()
        assert r1 is not None
        assert r2 is not None
        assert r3 is not None

    def test_cat(self):
        HEADING()
        Benchmark.Start()
        r1 = Shell.cat('tests/test_verbose.py')
        r2 = Shell.cat('.gitignore')
        Benchmark.Stop()
        print(r1, r2)
        assert '.DS' in r2
        assert 'variables' in r1

    def test_cms(self):
        HEADING()
        Benchmark.Start()
        r1 = Shell.cms('vpn status')
        r2 = Shell.cms('echo -r blue "hello"')
        print(r1)
        print(r2)
        Benchmark.Stop()
        assert 'True' or 'False' in r1
        assert 'hello' in r2

    def test_pwd(self):
        HEADING()
        Benchmark.Start()
        r = Shell.pwd()
        Benchmark.Stop()
        assert 'cm/cloudmesh-common' in r or 'cm\\cloudmesh-common' in r

    def test_open(self):
        HEADING()
        Benchmark.Start()
        filename = '~/cm/cloudmesh-common/cloudmesh/common/console.py'
        Shell.open(filename, program='xcode')
        Benchmark.Stop()
        assert True  # has to be a visual test!


