###############################################################
# pytest -v --capture=no  tests/test_verbose.py
# pytest -v tests/test_verbose.py
# pytest -v --capture=no  tests/test_verbose..py::Test_verbose.test_001
###############################################################

import io
import os
from contextlib import redirect_stdout

import pytest
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.util import HEADING
from cloudmesh.common.variables import Variables

variables = Variables()

old = variables["verbose"]

@pytest.mark.incremental
class Test_Verbose:

    def setup_method(self):
        global old
        old = variables["verbose"]
        print()
        print ("VERBOSE <-", old)
        variables["verbose"] = 10
        print ("VERBOSE =", variables["verbose"])

    def teardown_class(self):
        global old
        variables["verbose"] = old
        print()
        print ("VERBOSE ->", old)

    def test_value(self):
        os.system("cms debug on")
        v = variables["verbose"]
        print()
        print ("Variables", v)
        assert True

    def test_VERBOSE(self):
        HEADING()

        help = "hallo"
        with io.StringIO() as buf, redirect_stdout(buf):
            VERBOSE(help)
            output = buf.getvalue()

        assert "help" in output
        assert "hallo" in output
        assert "#" in output
        
    def test_not_VERBOSE(self):
        HEADING()

        variables["verbose"] = 0
        help = "hallo"
        with io.StringIO() as buf, redirect_stdout(buf):
            VERBOSE(help)
            output = buf.getvalue()

        import re
        output = re.sub(r'\x1b\[[0-9;]*m', '', output)

        print (output)
        variables["verbose"] = 10

        assert "help" not in output
        assert "hallo" not in output
        assert "#" not in output

    # def test_6_print_VERBOSE(self):
    #     HEADING()
    #
    #     print ("Location:", variables.filename)
    #     help = "hallo"
    #
    #     for v in [0,1,2,3,4,5,6,7,8,9,10]:
    #         print("TEST FOR VERBOSE", v)
    #         with io.StringIO() as buf, redirect_stdout(buf):
    #             variables["verbose"] = v
    #             VERBOSE(help, verbose=6)
    #             output = buf.getvalue()
    #         print (output)
    #
    #         if v < 6:
    #             assert "hallo" not in output
    #             assert "#" not in output
    #         else:
    #             assert "hallo" in output
    #             assert "#" in output
    #
    #     variables["verbose"] = old
