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
import pytest
import os
from pathlib import Path

@pytest.mark.incremental
class Test_copy_class:
    """

    """

    def test_remove_remnants(self):
        HEADING()
        Benchmark.Start()
        Shell.rm('a_cool_file.txt')
        Shell.rm('a_cool_file_2.txt')
        Shell.rm('my_ftp_copied.txt')
        Shell.rm('file_for_ftp_server.txt')
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
        try:
            Shell.run('curl -T a_cool_file.txt ftp://ftp.dlptest.com --user dlpuser:rNrKYTX9g7z3RgJRmxWuGHbeu')
        except Exception as e:
            print(e.output)
        Shell.copy2('file_for_ftp_server.txt', 'ftp://dlpuser:rNrKYTX9g7z3RgJRmxWuGHbeu@ftp.dlptest.com/copied.txt')
        Shell.copy2('ftp://dlpuser:rNrKYTX9g7z3RgJRmxWuGHbeu@ftp.dlptest.com/copied.txt', 'my_ftp_copied.txt')
        assert os.path.exists('my_ftp_copied.txt')

    def test_remove_remnants(self):
        HEADING()
        Benchmark.Start()
        Shell.rm('a_cool_file.txt')
        Shell.rm('a_cool_file_2.txt')
        Shell.rm('my_ftp_copied.txt')
        Shell.rm('file_for_ftp_server.txt')
        Benchmark.Stop()
