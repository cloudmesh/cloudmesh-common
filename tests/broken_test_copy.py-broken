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
from cloudmesh.vpn.vpn import Vpn
import pytest
import os
import time
from pathlib import Path


variables = Variables()

# ----------------------------------
# GET remote host from cms variables
#
# host, user = set_remote_host_user()
host = "rivanna.hpc.virginia.edu"
# ----------------------------------

username = variables["username"]

if username is None:
    Console.warning("No username provided. Use cms set username=ComputingID")
    # quit()

job = None

try:
    if not Vpn.enabled() and not Vpn.is_uva():
        Console.error('vpn not enabled')
        login_success = False
        raise Exception
    command = f"ssh {username}@{host} hostname"
    print(command)
    content = Shell.run(command, timeout=3)
    login_success = True
except Exception as e:  # noqa: E722
    print(e)
    login_success = False


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
        Shell.rm('a_cool_subdir_file.txt')
        Shell.rmdir('nesteddir')
        if login_success:
            try:
                os.system(f'ssh {username}@{host} "rm my_cool_file_on_rivanna.txt"')
            except Exception as e:
                print(e.output)
        Benchmark.Stop()

    def test_regular_copy(self):
        HEADING()
        Benchmark.Start()
        Shell.run('touch a_cool_file.txt')
        Shell.copy('a_cool_file.txt', 'a_cool_file_2.txt')
        assert os.path.exists('a_cool_file_2.txt')
        Benchmark.Stop()

    def test_ftp_copy(self):
        HEADING()
        Benchmark.Start()
        Shell.run('touch file_for_ftp_server.txt')
        Shell.copy_file('file_for_ftp_server.txt', 'ftp://dlpuser:rNrKYTX9g7z3RgJRmxWuGHbeu@ftp.dlptest.com/copied.txt')
        Shell.copy_file('ftp://dlpuser:rNrKYTX9g7z3RgJRmxWuGHbeu@ftp.dlptest.com/copied.txt', 'my_ftp_copied.txt')
        assert os.path.exists('my_ftp_copied.txt')

    @pytest.mark.skipif(not login_success,
                        reason=f"host {username}@{host} not found or VPN not enabled")
    def test_scp_rivanna(self):
        HEADING()
        Benchmark.Start()
        Shell.run(f'ssh {username}@{host} "touch my_cool_file_on_rivanna.txt"')
        Shell.copy_file(
            f'scp:{username}@{host}:my_cool_file_on_rivanna.txt',
            'my_now_on_local_computer_file.txt')
        assert os.path.exists('my_now_on_local_computer_file.txt')
        Benchmark.Stop()

    def test_subdirectories_copy(self):
        HEADING()
        Benchmark.Start()
        Shell.run('touch a_cool_subdir_file.txt')
        Shell.copy_file('a_cool_subdir_file.txt', 'nesteddir/nesteddirtwo/new.txt')
        assert os.path.exists('nesteddir/nesteddirtwo/new.txt')
        Benchmark.Stop()

    def test_remove_remnants2(self):
        HEADING()
        Benchmark.Start()
        Shell.rm('a_cool_file.txt')
        Shell.rm('a_cool_file_2.txt')
        Shell.rm('my_ftp_copied.txt')
        Shell.rm('file_for_ftp_server.txt')
        Shell.rm('my_now_on_local_computer_file.txt')
        Shell.rm('a_cool_subdir_file.txt')
        Shell.rmdir('nesteddir')
        if login_success:
            try:
                os.system(f'ssh {username}@{host} "rm my_cool_file_on_rivanna.txt"')
            except Exception as e:
                print(e.output)
        Benchmark.Stop()




