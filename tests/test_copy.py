###############################################################
# pytest -v --capture=no  tests/test_copy.py
# pytest -v --capture=no  tests/test_copy.py::Test_copy.test_001
# pytest -v tests/test_copy.py
###############################################################
import getpass

from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import HEADING
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.systeminfo import os_is_windows, os_is_linux
from cloudmesh.common.util import path_expand
from cloudmesh.common.Shell import Console
from cloudmesh.common.variables import Variables
import pytest
import os
import time
from pathlib import Path


variables = Variables()

if "host" not in variables:
    host = "rivanna.hpc.virginia.edu"
else:
    host = variables["host"]

username = variables["username"]

if username is None:
    Console.error("No username provided. Use cms set username=ComputingID")
    quit()

@pytest.mark.incremental
class Test_copy_class:
    """

    """

    def test_remove_remnants1(self):
        HEADING()
        Benchmark.Start()
        Shell.rm('a_cool_file.txt')
        Shell.rm('a_cool_file_2.txt')
        Shell.rm('my_ftp_copied.txt')
        Shell.rm('file_for_ftp_server.txt')
        Shell.rm('my_now_on_local_computer_file.txt')
        try:
            os.system(f'ssh {username}@{host} "rm my_cool_file_on_rivanna.txt"')
        except Exception as e:
            print(e.output)
        Benchmark.Stop()

    def test_regular_copy(self):
        HEADING()
        Benchmark.Start()
        Shell.run('touch a_cool_file.txt')
        Shell.copy2('a_cool_file.txt', 'a_cool_file_2.txt')
        assert os.path.exists('a_cool_file_2.txt')
        Benchmark.Stop()

    def test_ftp_copy(self):
        HEADING()
        Benchmark.Start()
        Shell.run('touch file_for_ftp_server.txt')
        Shell.copy2('file_for_ftp_server.txt', 'ftp://dlpuser:rNrKYTX9g7z3RgJRmxWuGHbeu@ftp.dlptest.com/copied.txt')
        Shell.copy2('ftp://dlpuser:rNrKYTX9g7z3RgJRmxWuGHbeu@ftp.dlptest.com/copied.txt', 'my_ftp_copied.txt')
        assert os.path.exists('my_ftp_copied.txt')

    def test_scp_rivanna(self):
        HEADING()
        Benchmark.Start()
        Shell.run(f'ssh {username}@{host} "touch my_cool_file_on_rivanna.txt"')
        Shell.copy2(
            f'scp:{username}@{host}:my_cool_file_on_rivanna.txt',
            'my_now_on_local_computer_file.txt')
        Benchmark.Stop()
        assert os.path.exists('my_now_on_local_computer_file.txt')

    def test_remove_remnants2(self):
        HEADING()
        Benchmark.Start()
        Shell.rm('a_cool_file.txt')
        Shell.rm('a_cool_file_2.txt')
        Shell.rm('my_ftp_copied.txt')
        Shell.rm('file_for_ftp_server.txt')
        Shell.rm('my_now_on_local_computer_file.txt')
        try:
            os.system(f'ssh {username}@{host} "rm my_cool_file_on_rivanna.txt"')
        except Exception as e:
            print(e.output)
        Benchmark.Stop()




